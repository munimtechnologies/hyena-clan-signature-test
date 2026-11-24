# Reading of the hyena clan-signature re-test (graded 2026-11-24)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; not yet checked by
a human expert. Text CC BY 4.0, code Apache-2.0. Plan: [HYENA-PREREG.md](HYENA-PREREG.md) (written
2026-11-23, before any analysis). Raw output: [results/hyena_results.json](results/hyena_results.json),
[results/RESULTS-HYENA.md](results/RESULTS-HYENA.md), data check
[results/fetch_report.json](results/fetch_report.json) (all 7 files match Dryad's CC0 copy).

## Registered verdict: NO_GROUP_SIGNAL_POWERED

The title claim of Lehmann et al. 2022 (Proc. R. Soc. B 289: 20220548), that spotted hyena whoops
carry individual but **not** clan signatures, holds under the test we registered in advance. The
paper reported no significance test or power analysis for this negative; this is, as far as we
found, the first calibrated and powered test of it.

| test | data | observed | null mean | null 95th pct | worlds | p |
|---|---|---|---|---|---|---|
| T1 (primary) | all A/S whoops, 47 hyenas, 431 whoops | 0.2403 | 0.2207 | 0.3112 | 299 | 0.34 |
| T2 | handheld only, 42 hyenas, 375 whoops | 0.2754 | 0.2237 | 0.3150 | 299 | 0.1767 |
| T5 | females only, 30 hyenas, 225 whoops | 0.1939 | 0.2095 | 0.3114 | 199 | 0.575 |

Statistic: leave-one-hyena-out random forest, mean over the 4 clans of the per-hyena share of whoops
assigned to the right clan (nominal chance 0.25). Null: whole hyenas relabeled between clans,
keeping clan sizes.

**Power (T3).** With a clan offset planted in relabeled worlds (offset drawn from delta^2 times the
covariance of the hyenas' mean whoops), the same test detected it in 40 of 40 worlds at every step:
delta 0.25, 0.50, 0.75 and 1.00. The registered target was power >= 0.8 at delta 0.5. So a clan
signature even a quarter the size of the differences between individual hyenas, if it took the form
of a shift of the whole whoop, would very likely have been found.

**The authors' scheme (T4).** Our reconstruction (one random hyena per clan held out, 500 trees,
1000 draws) gave a mean share correct of 0.3458 (s.d. 0.1794) against a mean chance of 0.2573; the
paper reported 0.32 (s.d. 0.15) against 0.24. Within the registered tolerance: REPRODUCED. The
paper's roughly 8-point excess over chance is real in the sense that we see it too (0.0858), but it
is not significant against 99 relabeled worlds (p 0.09).

**Why "chance" misleads here.** Under whole-hyena relabeling the leave-one-hyena-out statistic
averages 0.221, below the nominal 0.25, and its 95th percentile is about 0.31. A raw accuracy has to
be compared with this null, not with 1/4; an accuracy of 0.32 can be noise in a design with 4
clans and 10 to 14 hyenas each.

## Predictions (Brier score)

| Q | statement | prior | outcome | Brier |
|---|---|---|---|---|
| Q1 | T1 p <= 0.05 | 0.40 | no | 0.1600 |
| Q2 | T2 p <= 0.05 | 0.30 | no | 0.0900 |
| Q3 | T3 power at delta 0.5 >= 0.8 | 0.55 | yes | 0.2025 |
| Q4 | T4 REPRODUCED | 0.50 | yes | 0.2500 |
| Q5 | T4 null p <= 0.05 | 0.35 | no (0.09) | 0.1225 |

Mean Brier 0.165. We expected the negative to be weaker than it is: we gave a 40% chance that a
proper null would find a clan signal, and a 45% chance that the data would be too small to say.

## What this does and does not show

- It shows that, on the authors' own measurements, no clan signature is detectable with a properly
  calibrated test, and that the data had the power to find a moderate one.
- Power is measured against one kind of signature: a coherent shift of all 16 acoustic measures for
  every member of a clan. A clan badge carried by one or two measures, or by a feature the 16
  measures do not capture (fine spectral shape, timing between whoops in a bout), could still be
  missed.
- Recording years differ between clans and the files carry no dates; a positive result would have
  been confounded with year or site. The negative is less exposed to this, since a confound would
  more likely have created a signal than hidden one.
- Only A and S whoops were used (as in the paper's reported numbers); ages are not in the data, so
  the paper's adult filter could not be applied.
- Clans are made of matrilines; the result says nothing about kin signatures within a clan.

Credit: all data and the design of the original analysis are the authors' (Lehmann, Jensen,
Gersick, Strandburg-Peshkin, Holekamp). Data: github.com/kdslehmann/HyenaWhoopSignatures at commit
07436a77 and Dryad doi:10.5061/dryad.djh9w0w2h (CC0).
