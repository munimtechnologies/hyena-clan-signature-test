# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Calibrated re-test of "individual but not group signatures" in spotted hyena whoops
(Lehmann, Jensen, Gersick, Strandburg-Peshkin and Holekamp 2022, Proc. R. Soc. B 289: 20220548).

The paper reports clan classification of unseen hyenas at mean accuracy 0.32 against a weighted
chance expectation of 0.24 and calls it "no more accurate than expected by chance", without a test.
This script asks, as registered in HYENA-PREREG.md:
  T1 (primary)  leave-one-hyena-out clan-balanced accuracy vs. a null that relabels whole hyenas
                between clans (clan sizes kept), on the A/S whoops of all hyenas;
  T2            the same on the handheld recordings only (drops the 5 collared Talek West females);
  T3            power: the same test on relabeled worlds with an injected clan offset of delta times
                the spread of individual hyenas' mean whoops (delta 0.25, 0.5, 0.75, 1.0);
  T4            the authors' scheme (one random unseen hyena per clan, 1000 draws) reproduced, and
                its mean (accuracy - chance) compared with the same relabeling null;
  T5            females only (dispersing males may carry their natal clan's signature).
Only numpy is needed at import time; scikit-learn is imported when a forest is built.
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np

FEATS = ["M%d" % i for i in range(5, 21)]  # M5..M20: the 16 acoustic measures (M22 is all zero)
COLLARS = ["BORA", "BYTE", "FAY-", "MGTA", "WRTH"]
MAIN_FILE = "hyena_whoops_2021_07_08.csv"
CLAN_FILE = "hyenaClanCode.txt"
COLLAR_FILE = "%s_2020_06_12.csv"
ALPHA = 0.05
POWER_TARGET = 0.8
DELTAS = (0.25, 0.5, 0.75, 1.0)
DELTA_REF = "0.50"
MIN_WORLDS = 99
# Published values for the A/S clan analysis (paper, Results): mean 0.32, s.d. 0.15, chance 0.24.
PUB_MEAN, PUB_WE = 0.32, 0.24
TOL_MEAN, TOL_WE = 0.05, 0.04


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def load_clan_code(path):
    rows = read_rows(path)
    need = {"Var1", "M3", "M4", "M5"}
    if not rows or not need.issubset(set(rows[0].keys())):
        raise SystemExit("clan code: expected columns %s, got %s"
                         % (sorted(need), list(rows[0].keys()) if rows else "no rows"))
    by_index, by_name = {}, {}
    for r in rows:
        idx = int(float(r["Var1"]))
        name, clan, sex = r["M3"].strip(), r["M4"].strip(), r["M5"].strip()
        by_index[idx] = (name, clan, sex)
        by_name[name] = (idx, clan, sex)
    return by_index, by_name


def parse_feats(r):
    out = []
    for f in FEATS:
        try:
            out.append(float(r.get(f)))
        except (TypeError, ValueError):
            out.append(float("nan"))
    return out


def _check_cols(rows, label):
    if not rows:
        raise SystemExit("%s: no rows" % label)
    missing = [c for c in ["Var1", "Var2", "M23"] + FEATS if c not in rows[0]]
    if missing:
        raise SystemExit("%s: missing columns %s (have %s)" % (label, missing, list(rows[0].keys())))


def load_whoops(data_dir):
    """One record per whoop: hyena name, clan, sex, bout, whoop type, source, 16 features.
    Main-file Var1 is the row index of hyenaClanCode.txt; each collar file is one hyena."""
    by_index, by_name = load_clan_code(os.path.join(data_dir, CLAN_FILE))
    recs = []
    main = read_rows(os.path.join(data_dir, MAIN_FILE))
    _check_cols(main, MAIN_FILE)
    for r in main:
        idx = int(float(r["Var1"]))
        if idx not in by_index:
            raise SystemExit("main file Var1 %d is not in the clan code" % idx)
        name, clan, sex = by_index[idx]
        if name in COLLARS:
            raise SystemExit("main file Var1 %d maps to collared hyena %s" % (idx, name))
        recs.append({"hyena": name, "clan": clan, "sex": sex, "bout": r["Var2"].strip(),
                     "wtype": r["M23"].strip(), "source": "main", "feats": parse_feats(r)})
    for name in COLLARS:
        if name not in by_name:
            raise SystemExit("collared hyena %s is not in the clan code" % name)
        _, clan, sex = by_name[name]
        rows = read_rows(os.path.join(data_dir, COLLAR_FILE % name))
        _check_cols(rows, COLLAR_FILE % name)
        for r in rows:
            recs.append({"hyena": name, "clan": clan, "sex": sex, "bout": r["Var2"].strip(),
                         "wtype": r["M23"].strip(), "source": "collar", "feats": parse_feats(r)})
    return recs


def build(recs, types=("A", "S"), source=None, sex=None):
    sel = [r for r in recs if r["wtype"] in types
           and (source is None or r["source"] == source)
           and (sex is None or r["sex"] == sex)]
    if not sel:
        raise SystemExit("empty data set for types=%s source=%s sex=%s" % (types, source, sex))
    X = np.array([r["feats"] for r in sel], dtype=float)
    ok = np.all(np.isfinite(X), axis=1)
    dropped = int(np.sum(~ok))
    sel = [r for r, k in zip(sel, ok) if k]
    X = X[ok]
    names = sorted({r["hyena"] for r in sel})
    code = {n: i for i, n in enumerate(names)}
    hy = np.array([code[r["hyena"]] for r in sel], dtype=int)
    clan_by_name = {}
    for r in sel:
        clan_by_name[r["hyena"]] = r["clan"]
    clans = sorted(set(clan_by_name.values()))
    ccode = {c: i for i, c in enumerate(clans)}
    clan_of_hy = np.array([ccode[clan_by_name[n]] for n in names], dtype=int)
    return {"X": X, "hy": hy, "names": names, "clans": clans, "clan_of_hy": clan_of_hy,
            "dropped_nonfinite": dropped, "n_whoops": int(len(sel)), "n_hyenas": len(names),
            "hyenas_per_clan": {c: int(np.sum(clan_of_hy == ccode[c])) for c in clans},
            "whoops_per_clan": {c: int(np.sum(clan_of_hy[hy] == ccode[c])) for c in clans}}


def make_rf(n_trees, seed, n_jobs):
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=n_trees, random_state=int(seed) % (2 ** 32 - 1),
                                  n_jobs=n_jobs)


def per_hyena_accuracy(X, hy, clan_of_hy, n_trees, seed, n_jobs=1):
    """Leave one hyena out: share of each hyena's whoops assigned to its own clan."""
    y = clan_of_hy[hy]
    acc = np.zeros(len(clan_of_hy))
    for h in range(len(clan_of_hy)):
        test = hy == h
        rf = make_rf(n_trees, seed * 1009 + h, n_jobs)
        rf.fit(X[~test], y[~test])
        acc[h] = float(np.mean(rf.predict(X[test]) == y[test]))
    return acc


def clan_balanced(acc, clan_of_hy):
    """Mean over clans of the mean per-hyena accuracy (chance is 1/number of clans)."""
    return float(np.mean([acc[clan_of_hy == c].mean() for c in np.unique(clan_of_hy)]))


def perm_p(obs, null):
    null = np.asarray(null, dtype=float)
    return float((1 + np.sum(null >= obs - 1e-12)) / (1 + null.size))


def weighted_expectation(ytr, yte, clans):
    """Expected share correct when guessing clans in proportion to the training whoops."""
    return float(sum(np.mean(yte == c) * np.mean(ytr == c) for c in clans))


def authors_scheme(X, hy, clan_of_hy, iters, n_trees, rng, seed_base, n_jobs=1):
    """Paper's scheme: test set = all whoops of one random hyena per clan; train on the rest."""
    y = clan_of_hy[hy]
    clans = np.unique(clan_of_hy)
    groups = [np.flatnonzero(clan_of_hy == c) for c in clans]
    acc, we = np.zeros(iters), np.zeros(iters)
    for r in range(iters):
        pick = np.array([rng.choice(g) for g in groups])
        test = np.isin(hy, pick)
        rf = make_rf(n_trees, seed_base + r, n_jobs)
        rf.fit(X[~test], y[~test])
        acc[r] = float(np.mean(rf.predict(X[test]) == y[test]))
        we[r] = weighted_expectation(y[~test], y[test], clans)
    return acc, we


def offset_matrix(X, hy, n_hy):
    """A with A A^T = covariance of the hyenas' mean whoops (between-individual spread)."""
    means = np.array([X[hy == h].mean(axis=0) for h in range(n_hy)])
    w, V = np.linalg.eigh(np.cov(means, rowvar=False))
    return V * np.sqrt(np.clip(w, 0.0, None))[None, :]


def inject(X, hy, clan_lab_hy, delta, A, rng, n_clans):
    """Add a clan offset drawn from delta^2 times the between-individual covariance."""
    g = rng.standard_normal((n_clans, X.shape[1]))
    offsets = delta * (g @ A.T)
    return X + offsets[clan_lab_hy[hy]]


def verdict(p_all, p_hand, power_ref):
    if p_all is None or p_hand is None:
        return "INCOMPLETE"
    if p_all <= ALPHA and p_hand <= ALPHA:
        return "GROUP_SIGNAL_ROBUST"
    if p_all <= ALPHA:
        return "GROUP_SIGNAL_NOT_ROBUST_TO_COLLARS"
    if p_hand <= ALPHA:
        return "GROUP_SIGNAL_HANDHELD_ONLY"
    if power_ref is None:
        return "INCOMPLETE"
    return "NO_GROUP_SIGNAL_POWERED" if power_ref >= POWER_TARGET else "NO_GROUP_SIGNAL_UNDERPOWERED"


def null_loop(d, worlds, rng, trees, seed_base, n_jobs, deadline):
    scores = []
    for w in range(worlds):
        if time.time() > deadline:
            break
        perm = rng.permutation(d["clan_of_hy"])
        acc = per_hyena_accuracy(d["X"], d["hy"], perm, trees, seed_base + w + 1, n_jobs)
        scores.append(clan_balanced(acc, perm))
    return scores


def loho_test(d, worlds, rng, trees, seed_base, n_jobs, deadline):
    acc = per_hyena_accuracy(d["X"], d["hy"], d["clan_of_hy"], trees, seed_base, n_jobs)
    obs = clan_balanced(acc, d["clan_of_hy"])
    null = null_loop(d, worlds, rng, trees, seed_base, n_jobs, deadline)
    p = perm_p(obs, null) if len(null) >= MIN_WORLDS else None
    return {"observed": obs, "chance": 1.0 / len(d["clans"]), "worlds": len(null), "p": p,
            "null_mean": float(np.mean(null)) if null else None,
            "null_q95": float(np.quantile(null, 0.95)) if null else None,
            "per_hyena": {n: float(a) for n, a in zip(d["names"], acc)}}, null


def power_loop(d, null, worlds, rng, trees, seed_base, n_jobs, deadline):
    A = offset_matrix(d["X"], d["hy"], len(d["clan_of_hy"]))
    out, k = {}, 0
    for delta in DELTAS:
        hits = done = 0
        for _ in range(worlds):
            if time.time() > deadline:
                break
            perm = rng.permutation(d["clan_of_hy"])
            Xi = inject(d["X"], d["hy"], perm, delta, A, rng, len(d["clans"]))
            k += 1
            acc = per_hyena_accuracy(Xi, d["hy"], perm, trees, seed_base + k, n_jobs)
            done += 1
            if perm_p(clan_balanced(acc, perm), null) <= ALPHA:
                hits += 1
        out["%.2f" % delta] = {"worlds": done, "hits": hits,
                               "power": (hits / done) if done else None}
    return out


def describe(d):
    return {k: d[k] for k in ("n_whoops", "n_hyenas", "hyenas_per_clan", "whoops_per_clan",
                              "dropped_nonfinite", "clans")}


def write_md(res, path):
    L = ["# Hyena clan-signature re-test: results", "",
         "Registered verdict: **%s**" % res.get("verdict", "PENDING (job still running)"), ""]
    for key in ("T1_all", "T2_handheld", "T5_females"):
        t = res.get(key)
        if t:
            L.append("- %s: observed clan-balanced accuracy %.4f (chance %.4f), null mean %s, "
                     "worlds %d, p %s" % (key, t["observed"], t["chance"], t["null_mean"],
                                          t["worlds"], t["p"]))
    if res.get("T3_power"):
        for k, v in res["T3_power"].items():
            L.append("- T3 power at delta %s: %s of %s worlds (power %s)"
                     % (k, v["hits"], v["worlds"], v["power"]))
    t4 = res.get("T4_authors")
    if t4:
        L.append("- T4 authors' scheme: mean accuracy %.4f (s.d. %.4f), mean chance %.4f over %d "
                 "draws; reproduction %s" % (t4["mean_acc"], t4["sd_acc"], t4["mean_we"],
                                             t4["iters"], t4["reproduction"]))
        if t4.get("null_worlds"):
            L.append("- T4 null: observed mean(acc - chance) %.4f, %d worlds, p %s"
                     % (t4["null_obs"], t4["null_worlds"], t4["null_p"]))
    L += ["", "Data sets:", "```", json.dumps(res["datasets"], indent=1), "```", "",
          "Made with AI agents working in MV2's name (MV2, Munim, Inc.); not yet checked by a "
          "human expert.", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def save(res, out_dir):
    with open(os.path.join(out_dir, "hyena_results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    write_md(res, os.path.join(out_dir, "RESULTS-HYENA.md"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--worlds", type=int, default=299)
    ap.add_argument("--worlds-fem", type=int, default=199)
    ap.add_argument("--power-worlds", type=int, default=40)
    ap.add_argument("--p0-iters", type=int, default=1000)
    ap.add_argument("--p0-trees", type=int, default=500)
    ap.add_argument("--p0-null-worlds", type=int, default=99)
    ap.add_argument("--p0-null-iters", type=int, default=40)
    ap.add_argument("--trees", type=int, default=100)
    ap.add_argument("--n-jobs", type=int, default=2)
    ap.add_argument("--budget-min", type=float, default=270.0)
    ap.add_argument("--seed", type=int, default=20261123)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    deadline = time.time() + 60.0 * a.budget_min
    rng = np.random.default_rng(a.seed)
    recs = load_whoops(a.data_dir)
    types_all = {}
    for r in recs:
        types_all[r["wtype"]] = types_all.get(r["wtype"], 0) + 1
    d_all = build(recs)
    d_hand = build(recs, source="main")
    d_fem = build(recs, sex="F")
    res = {"paper": "doi:10.1098/rspb.2022.0548", "settings": vars(a), "whoop_types": types_all,
           "datasets": {"all": describe(d_all), "handheld": describe(d_hand),
                        "females": describe(d_fem)}}
    t0 = time.time()
    res["T1_all"], null_all = loho_test(d_all, a.worlds, rng, a.trees, 10000, a.n_jobs, deadline)
    save(res, a.out_dir)
    print("T1 done %.0fs p=%s" % (time.time() - t0, res["T1_all"]["p"]), flush=True)
    res["T2_handheld"], _ = loho_test(d_hand, a.worlds, rng, a.trees, 20000, a.n_jobs, deadline)
    save(res, a.out_dir)
    print("T2 done %.0fs p=%s" % (time.time() - t0, res["T2_handheld"]["p"]), flush=True)
    if len(null_all) >= MIN_WORLDS:
        res["T3_power"] = power_loop(d_all, null_all, a.power_worlds, rng, a.trees, 30000,
                                     a.n_jobs, deadline)
    save(res, a.out_dir)
    print("T3 done %.0fs" % (time.time() - t0), flush=True)
    acc, we = authors_scheme(d_all["X"], d_all["hy"], d_all["clan_of_hy"], a.p0_iters,
                             a.p0_trees, rng, 40000, a.n_jobs)
    t4 = {"iters": a.p0_iters, "mean_acc": float(acc.mean()), "sd_acc": float(acc.std(ddof=1)),
          "mean_we": float(we.mean())}
    t4["reproduction"] = ("REPRODUCED" if abs(t4["mean_acc"] - PUB_MEAN) <= TOL_MEAN
                          and abs(t4["mean_we"] - PUB_WE) <= TOL_WE else "NOT_REPRODUCED")
    res["T4_authors"] = t4
    save(res, a.out_dir)
    print("T4a done %.0fs" % (time.time() - t0), flush=True)
    res["T5_females"], _ = loho_test(d_fem, a.worlds_fem, rng, a.trees, 50000, a.n_jobs, deadline)
    save(res, a.out_dir)
    print("T5 done %.0fs" % (time.time() - t0), flush=True)
    acc, we = authors_scheme(d_all["X"], d_all["hy"], d_all["clan_of_hy"], a.p0_null_iters,
                             a.trees, rng, 60000, a.n_jobs)
    obs = float(np.mean(acc - we))
    null = []
    for w in range(a.p0_null_worlds):
        if time.time() > deadline:
            break
        perm = rng.permutation(d_all["clan_of_hy"])
        acc, we = authors_scheme(d_all["X"], d_all["hy"], perm, a.p0_null_iters, a.trees, rng,
                                 70000 + 100 * w, a.n_jobs)
        null.append(float(np.mean(acc - we)))
    t4.update({"null_obs": obs, "null_worlds": len(null),
               "null_p": perm_p(obs, null) if len(null) >= MIN_WORLDS else None})
    p3 = res.get("T3_power", {}).get(DELTA_REF, {}).get("power")
    res["verdict"] = verdict(res["T1_all"]["p"], res["T2_handheld"]["p"], p3)
    res["elapsed_s"] = time.time() - t0
    save(res, a.out_dir)
    print("verdict %s" % res["verdict"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
