# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
import os
import tempfile
import unittest

import numpy as np

import hyena_clan as hc

try:
    import sklearn  # noqa: F401
    HAVE_SK = True
except ImportError:
    HAVE_SK = False

HEADER = "Var1,Var2," + ",".join(hc.FEATS) + ",M22,M23\n"


def row(var1, bout, wtype, base):
    return "%d,%d,%s,0,%s\n" % (var1, bout, ",".join("%.3f" % (base + i) for i in range(16)), wtype)


class TestPure(unittest.TestCase):
    def test_perm_p(self):
        null = list(range(19))  # 0..18
        self.assertAlmostEqual(hc.perm_p(100.0, null), 1 / 20)
        self.assertAlmostEqual(hc.perm_p(18.0, null), 2 / 20)  # ties count as extreme
        self.assertAlmostEqual(hc.perm_p(-1.0, null), 20 / 20)

    def test_clan_balanced(self):
        acc = np.array([1.0, 0.0, 1.0, 1.0])
        clan = np.array([0, 0, 1, 1])
        self.assertAlmostEqual(hc.clan_balanced(acc, clan), 0.75)

    def test_weighted_expectation(self):
        ytr = np.array([0, 0, 1, 1])
        yte = np.array([0, 1])
        self.assertAlmostEqual(hc.weighted_expectation(ytr, yte, [0, 1]), 0.5)
        self.assertAlmostEqual(hc.weighted_expectation(np.array([0, 0, 0, 1]), np.array([0]),
                                                       [0, 1]), 0.75)

    def test_verdict(self):
        self.assertEqual(hc.verdict(0.01, 0.02, 0.1), "GROUP_SIGNAL_ROBUST")
        self.assertEqual(hc.verdict(0.05, 0.2, 0.9), "GROUP_SIGNAL_NOT_ROBUST_TO_COLLARS")
        self.assertEqual(hc.verdict(0.2, 0.04, 0.9), "GROUP_SIGNAL_HANDHELD_ONLY")
        self.assertEqual(hc.verdict(0.2, 0.3, 0.8), "NO_GROUP_SIGNAL_POWERED")
        self.assertEqual(hc.verdict(0.2, 0.3, 0.79), "NO_GROUP_SIGNAL_UNDERPOWERED")
        self.assertEqual(hc.verdict(None, 0.3, 0.9), "INCOMPLETE")
        self.assertEqual(hc.verdict(0.2, 0.3, None), "INCOMPLETE")

    def test_offsets(self):
        rng = np.random.default_rng(1)
        X = rng.standard_normal((30, 16))
        hy = np.repeat(np.arange(10), 3)
        A = hc.offset_matrix(X, hy, 10)
        means = np.array([X[hy == h].mean(axis=0) for h in range(10)])
        self.assertTrue(np.allclose(A @ A.T, np.cov(means, rowvar=False), atol=1e-8))
        lab = np.array([0, 1] * 5)
        X0 = hc.inject(X, hy, lab, 0.0, A, rng, 2)
        self.assertTrue(np.allclose(X0, X))
        X1 = hc.inject(X, hy, lab, 1.0, A, rng, 2)
        d = X1 - X
        # every whoop of a clan gets the same offset
        self.assertTrue(np.allclose(d[hy == 0], d[0]))
        self.assertTrue(np.allclose(d[hy == 2], d[0]))
        self.assertFalse(np.allclose(d[hy == 1], d[0]))

    def test_load_and_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, hc.CLAN_FILE), "w") as fh:
                fh.write("Var1,M3,M4,M5\n1,AAAA,SN,F\n2,BBB-,HZ,M\n")
                for i, n in enumerate(hc.COLLARS):
                    fh.write("%d,%s,TW,F\n" % (3 + i, n))
            with open(os.path.join(tmp, hc.MAIN_FILE), "w") as fh:
                fh.write(HEADER + row(1, 1, "A", 1.0) + row(1, 2, "S", 2.0) + row(2, 1, "K", 3.0)
                         + row(2, 1, "A", 4.0))
            for i, n in enumerate(hc.COLLARS):
                with open(os.path.join(tmp, hc.COLLAR_FILE % n), "w") as fh:
                    fh.write(HEADER + row(1, 5, "A", 10.0 + i) + row(1, 5, "T", 20.0))
            recs = hc.load_whoops(tmp)
            self.assertEqual(len(recs), 4 + 2 * 5)
            d = hc.build(recs)
            self.assertEqual(d["n_whoops"], 3 + 5)
            self.assertEqual(d["n_hyenas"], 7)
            self.assertEqual(d["hyenas_per_clan"], {"HZ": 1, "SN": 1, "TW": 5})
            self.assertEqual(d["X"].shape, (8, 16))
            dh = hc.build(recs, source="main")
            self.assertEqual(dh["n_hyenas"], 2)
            self.assertEqual(dh["n_whoops"], 3)
            df = hc.build(recs, sex="F")
            self.assertEqual(df["n_hyenas"], 6)
            self.assertNotIn("HZ", df["clans"])

    def test_bad_mapping_fails_loud(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, hc.CLAN_FILE), "w") as fh:
                fh.write("Var1,M3,M4,M5\n1,AAAA,SN,F\n")
            with open(os.path.join(tmp, hc.MAIN_FILE), "w") as fh:
                fh.write(HEADER + row(2, 1, "A", 1.0))
            with self.assertRaises(SystemExit):
                hc.load_whoops(tmp)


@unittest.skipUnless(HAVE_SK, "scikit-learn not installed")
class TestForest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        n_cl, per_cl, per_hy = 4, 3, 5
        self.clan_of_hy = np.repeat(np.arange(n_cl), per_cl)
        self.hy = np.repeat(np.arange(n_cl * per_cl), per_hy)
        self.X = rng.standard_normal((len(self.hy), 16)) * 0.1
        # every feature separates the clans, so every split a tree can choose is a clean one
        self.X += 10.0 * self.clan_of_hy[self.hy][:, None]

    def test_separated_clans_score_one(self):
        acc = hc.per_hyena_accuracy(self.X, self.hy, self.clan_of_hy, 20, 3, 1)
        self.assertAlmostEqual(hc.clan_balanced(acc, self.clan_of_hy), 1.0)

    def test_authors_scheme_shapes(self):
        rng = np.random.default_rng(3)
        acc, we = hc.authors_scheme(self.X, self.hy, self.clan_of_hy, 3, 10, rng, 5, 1)
        self.assertEqual(acc.shape, (3,))
        self.assertTrue(np.all(acc == 1.0))
        self.assertTrue(np.allclose(we, 0.25))


if __name__ == "__main__":
    unittest.main()
