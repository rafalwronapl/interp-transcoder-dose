import unittest
import numpy as np
from .baselines_b import compact_ridge,predict_ridge,fit_cell,predict
from .fitting import ridge_fit,predict as reference


class BaselineTests(unittest.TestCase):
    def test_exact_centered_dual_recipe(self):
        r=np.random.default_rng(88);x=r.normal(size=(64,20));y=r.normal(size=(64,24));test=r.normal(size=(5,20))
        fit=compact_ridge(x,y);ref=ridge_fit(x,y)
        np.testing.assert_allclose(predict_ridge(fit,test),reference(ref,test),atol=1e-12,rtol=1e-12)
        cell=fit_cell(x,y,[0]*32+[1]*32);p=predict(cell,test[0],1)
        np.testing.assert_allclose(p['mean'],y[32:].mean(0))
        self.assertEqual(len(p['ridge']),24)

    def test_fail_closed_degenerate_fit(self):
        with self.assertRaises(ValueError):compact_ridge(np.zeros((8,10)),np.ones((8,10)))
        with self.assertRaises(ValueError):compact_ridge(np.empty((0,10)),np.empty((0,10)))
        with self.assertRaises(ValueError):fit_cell(np.ones((8,10)),np.ones((8,10)),[0]*8)


if __name__=='__main__':unittest.main()
