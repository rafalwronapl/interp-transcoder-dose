"""Exact normalized-input/branch-output native measurements.

Batch members are independent full-sequence forwards; no KV cache or reduced
attention graph is assumed. Only the final-position MLP tensor is replaced.
"""
import numpy as np
import torch


class Native:
    def __init__(self,model,layer,answer_ids):
        self.model=model;self.layers=model.model.layers
        self.layer=layer if layer>=0 else len(self.layers)+layer
        self.block=self.layers[self.layer];self.answers=list(answer_ids)
        self.value=None;self.mode=None;self.active=False;self.states={};self.calls=0;self.position=-1
        for p in model.parameters():p.requires_grad_(False)
        self.handles=[self.block.pre_feedforward_layernorm.register_forward_pre_hook(self._residual),
                      self.block.mlp.register_forward_pre_hook(self._input),
                      self.block.post_feedforward_layernorm.register_forward_hook(self._output)]

    def _residual(self,module,args):
        if self.active:self.states['R']=args[0][:,-1].detach().clone()

    def _input(self,module,args):
        if not self.active:return
        x=args[0];self.states['x0']=x[:,-1].detach().clone()
        if self.mode=='input':
            self.states['patch_before']=x[:,self.position].detach().clone()
            x=x.clone();x[:,self.position]=self.value.to(x.dtype)
        self.states['x']=x[:,-1].detach().clone()
        return (x,)+args[1:]

    def _output(self,module,args,y):
        if not self.active:return
        self.states['native_y']=y[:,-1].detach().clone()
        if self.mode=='output':
            self.states['patch_before']=y[:,self.position].detach().clone()
            y=y.clone();y[:,self.position]=self.value.to(y.dtype)
        self.states['y']=y[:,-1].detach().clone()
        return y

    def _margin(self,hidden):
        head=self.model.get_output_embeddings();bias=getattr(head,'bias',None)
        z=torch.nn.functional.linear(hidden,head.weight[self.answers],None if bias is None else bias[self.answers])
        cfg=getattr(self.model.config,'text_config',None) or self.model.config
        softcap=getattr(cfg,'final_logit_softcapping',None)
        if softcap:z=torch.tanh(z/softcap)*softcap
        return z[:,0]-z[:,1]

    def forward(self,ids,mode=None,value=None,full_head=False,gradient=False,position=-1):
        if mode not in (None,'input','output'):raise ValueError('bad patch mode')
        if mode is None and value is not None:raise ValueError('value without mode')
        if value is not None:
            value=torch.as_tensor(value,dtype=torch.float32)
            if value.ndim==1:value=value[None]
            if value.ndim!=2 or not torch.isfinite(value).all():raise ValueError('invalid patch tensor')
        batch=1 if value is None else len(value)
        tokens=torch.tensor(ids,dtype=torch.long)[None].repeat(batch,1)
        if not -len(ids)<=position<len(ids):raise ValueError('patch position outside prompt')
        self.active=True;self.mode=mode;self.value=value;self.states={};self.position=position
        try:
            self.calls+=batch
            context=torch.enable_grad() if gradient else torch.inference_mode()
            with context:
                if full_head:
                    z=self.model(input_ids=tokens,use_cache=False,logits_to_keep=1).logits[:,-1]
                    margin=z[:,self.answers[0]]-z[:,self.answers[1]]
                else:
                    hidden=self.model.model(input_ids=tokens,use_cache=False).last_hidden_state[:,-1]
                    margin=self._margin(hidden)
                if gradient:
                    if mode!='output' or not value.requires_grad:raise ValueError('gradient requires output leaf')
                    grad=torch.autograd.grad(margin.sum(),value)[0]
                    self.states['gradient']=grad.detach().clone()
            return dict(margin=margin.detach().cpu().double().numpy(),
                        **{k:v.detach().cpu().double().numpy() for k,v in self.states.items()})
        finally:self.active=False;self.mode=self.value=None

    def branch(self,z):
        if self.active:raise ValueError('nested native branch inside full forward')
        return self.block.post_feedforward_layernorm(self.block.mlp(z))

    def suffix(self,R,M):
        if self.layer!=len(self.layers)-1:raise ValueError('last-layer suffix only')
        r=torch.as_tensor(R,dtype=torch.float32)+torch.as_tensor(M,dtype=torch.float32)
        if r.ndim==1:r=r[None]
        with torch.inference_mode():return self._margin(self.model.model.norm(r)).double().numpy()

    def gradient(self,ids,y):
        leaf=torch.tensor(y,dtype=torch.float32,requires_grad=True)
        return self.forward(ids,'output',leaf,gradient=True)['gradient']

    def close(self):
        for h in self.handles:h.remove()
