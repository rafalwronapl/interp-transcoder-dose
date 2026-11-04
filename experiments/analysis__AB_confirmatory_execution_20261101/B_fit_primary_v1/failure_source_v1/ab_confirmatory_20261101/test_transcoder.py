import unittest
import torch
from .transcoder import Transcoder,endpoint_terms


class TCTests(unittest.TestCase):
    def test_endpoint_identity_and_frozen_skip(self):
        torch.manual_seed(61)
        state={k:torch.randn(*s) for k,s in dict(w_enc=(8,16),b_enc=(16,),w_dec=(16,8),b_dec=(8,),threshold=(16,),affine_skip_connection=(8,8)).items()}
        tc=Transcoder(state);z=torch.randn(4,8);dz=torch.randn(4,8)*.1;n0=torch.randn(4,8);n1=n0+torch.randn(4,8)
        terms=endpoint_terms(tc,z,dz,n0,n1)
        self.assertLess(terms['identity_max'],1e-12)
        torch.testing.assert_close(terms['energy0']+terms['energy1']+terms['mixed'],terms['error_energy'],atol=1e-10,rtol=1e-10)
        tc.threshold.fill_(-1e9)
        # Frozen threshold alone does not freeze ReLU sign. Put every feature
        # strictly in its positive linear region for this affine identity.
        tc.benc.fill_(1000.)
        dt,frozen,_,_=tc.changes(z,dz)
        torch.testing.assert_close(dt,frozen,atol=.003,rtol=1e-3)


if __name__=='__main__':unittest.main()
