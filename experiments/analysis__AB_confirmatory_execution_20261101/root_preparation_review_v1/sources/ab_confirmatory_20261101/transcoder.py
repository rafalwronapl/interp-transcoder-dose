"""Exact public JumpReLU operator; loading is reserved for reviewed stages."""
import torch


class Transcoder:
    def __init__(self,state):
        self.wenc=state['w_enc'].float();self.benc=state['b_enc'].float()
        self.wdec=state['w_dec'].float();self.bdec=state['b_dec'].float()
        self.threshold=state['threshold'].float()
        self.skip=state.get('affine_skip_connection')
        if self.skip is not None:self.skip=self.skip.float()

    def forward(self,z):
        pre=z@self.wenc+self.benc;mask=pre>self.threshold
        y=(pre*mask)@self.wdec+self.bdec
        if self.skip is not None:y=y+z@self.skip
        return y,pre,mask

    def changes(self,z,dz):
        y0,pre0,m0=self.forward(z);y1,_,_=self.forward(z+dz)
        frozen=((dz@self.wenc)*m0)@self.wdec
        if self.skip is not None:frozen=frozen+dz@self.skip
        return y1-y0,frozen,y0,y1


def load(folder):
    import json
    from pathlib import Path
    from safetensors.torch import load_file
    folder=Path(folder);cfg=json.loads((folder/'config.json').read_text())
    if cfg['hf_hook_point_in']!='model.layers.15.pre_feedforward_layernorm.output' or cfg['hf_hook_point_out']!='model.layers.15.post_feedforward_layernorm.output':
        raise ValueError('wrong public TC hooks')
    if cfg['architecture']!='jump_relu':raise ValueError('wrong TC architecture')
    state=load_file(str(folder/'params.safetensors'),device='cpu')
    if bool(cfg['affine_connection'])!=('affine_skip_connection' in state):raise ValueError('skip metadata mismatch')
    return Transcoder(state)


def endpoint_terms(tc,z,dz,native0,native1):
    dt,frozen,t0,t1=tc.changes(z,dz)
    e0=t0.double()-native0.double();e1=t1.double()-native1.double()
    native_delta=native1.double()-native0.double()
    # Evaluate identity from endpoints in FP64; separately record float32
    # subtraction discrepancy rather than claiming exact FP32 associativity.
    delta_error=(t1.double()-t0.double())-native_delta
    residual=delta_error-(e1-e0)
    return dict(delta_tc=dt,delta_frozen=frozen,e0=e0,e1=e1,
                energy0=(e0*e0).sum(-1),energy1=(e1*e1).sum(-1),
                mixed=-2*(e1*e0).sum(-1),error_energy=(delta_error*delta_error).sum(-1),
                identity_max=float(residual.abs().max()),
                fp32_delta_error_max=float((dt.double()-native_delta-delta_error).abs().max()))
