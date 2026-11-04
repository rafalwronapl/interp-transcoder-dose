"""Memoize ONLY exact immutable FIT metadata digest; scientific worker unchanged."""
from pathlib import Path
from . import status_resume as previous
from . import worker as w
BASE=Path(__file__).parent
class ExactFitMemo:
    def __init__(self,unwrap,digest,path):
        self.original_unwrap=unwrap;self.original_digest=digest;self.path=path.resolve();self.value=None;self.hash=None;self.hits=0
    def unwrap(self,path):
        value=self.original_unwrap(path)
        if Path(path).resolve()==self.path:
            self.value=value;self.hash=self.original_digest(value)
        return value
    def digest(self,value):
        if value is self.value and self.value is not None:
            self.hits+=1;return self.hash
        return self.original_digest(value)
    def verify(self):
        if self.value is not None and self.original_digest(self.value)!=self.hash:raise ValueError('Immutable FIT was mutated')
def main():
    original_unwrap=w.unwrap;original_digest=w.digest;original_measure=w.measure
    memo=ExactFitMemo(original_unwrap,original_digest,BASE/'run/frozen_fit.json')
    def measure(*args,**kwargs):
        result=original_measure(*args,**kwargs)
        memo.verify() # before previous.main publishes completed scientific seal
        w.immutable(BASE/'run/fit_digest_memo.json',dict(scope='Only object-identical verified frozen FIT',digest=memo.hash,hits=memo.hits,final_immutable_check=True,numerical_worker_unchanged=True))
        return result
    w.unwrap=memo.unwrap;w.digest=memo.digest;w.measure=measure
    try:previous.main()
    finally:w.unwrap=original_unwrap;w.digest=original_digest;w.measure=original_measure
if __name__=='__main__':main()
