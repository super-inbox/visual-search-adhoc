import unittest
import numpy as np
from sampling import coverage_motion,uniform

class SamplingTests(unittest.TestCase):
    def test_short_and_empty(self):
        for n in (0,1,2,100,256):
            self.assertEqual(coverage_motion(np.ones(n)),list(range(n)))
    def test_invalid(self):
        for e in ([float('nan')],[-1],[float('inf')]):
            with self.assertRaises(ValueError):coverage_motion(e)
        with self.assertRaises(ValueError):coverage_motion([1],-1)
    def test_static_uniform(self):
        self.assertEqual(coverage_motion(np.zeros(608)),uniform(608,256))
    def test_exact_budget_order_and_endpoints(self):
        rng=np.random.default_rng(42)
        for n in (257,608,2000):
            for k in (0,1,2,4,31,256):
                e=rng.random(n);x=coverage_motion(e,k)
                self.assertEqual(len(x),k);self.assertEqual(x,sorted(set(x)))
                self.assertTrue(all(0<=i<n for i in x))
                if k>=2:self.assertEqual((x[0],x[-1]),(0,n-1))
    def test_global_coverage_survives_burst(self):
        e=np.zeros(1000);e[400:600]=10
        x=coverage_motion(e,100)
        self.assertTrue(set(uniform(1000,50)).issubset(x))
        self.assertGreater(sum(400<=i<600 for i in x),20)
        self.assertEqual(x,coverage_motion(e,100))
    def test_single_spike_no_collapse(self):
        e=np.zeros(1000);e[500]=10000
        self.assertEqual(coverage_motion(e,100),uniform(1000,100))
if __name__=='__main__':unittest.main()
