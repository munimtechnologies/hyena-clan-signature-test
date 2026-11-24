# hyena-clan-signature-test

A pre-registered, calibrated re-test of the claim that spotted hyena whoops carry individual but
**not group** (clan) signatures (Lehmann et al. 2022, Proc. R. Soc. B 289: 20220548,
doi:10.1098/rspb.2022.0548).

The paper classified the clan of unseen hyenas at a mean accuracy of 0.32 against a chance level of
0.24 and reported this as no better than chance, without a significance test or a power analysis.
This project tests that excess against a null that relabels whole hyenas between clans, measures
how large a clan signature the data could have detected, and checks whether any signal depends on
the five collar-recorded hyenas.

## Result (graded 2026-11-24): the negative holds, with power

Registered verdict **NO_GROUP_SIGNAL_POWERED** ([READING-HYENA.md](READING-HYENA.md)):

- Leave-one-hyena-out clan accuracy 0.2403 on 431 whoops of 47 hyenas, against a relabeling null
  averaging 0.2207: p 0.34 (299 worlds). Handheld recordings only: 0.2754, p 0.1767. Females only:
  0.1939, p 0.575.
- A planted clan offset a quarter the size of the differences between individual hyenas was found
  in 40 of 40 worlds (power 1.0 at every planted size).
- The authors' own scheme reproduces (0.3458 against chance 0.2573; paper 0.32 against 0.24), and
  its excess over chance is not significant against relabeled worlds (p 0.09).

## Files

- `HYENA-PREREG.md`: the plan, verdict rules and our predictions, written before analysis.
- `READING-HYENA.md`: the graded reading, Brier score and limits.
- `results/`: the job's raw output (`hyena_results.json`, `RESULTS-HYENA.md`, `fetch_report.json`).
- `hyena_clan.py`: the analysis (numpy, scikit-learn 1.5.2).
- `fetch_data.py`: downloads the authors' data at a pinned commit and checks it against Dryad's
  CC0 copy (doi:10.5061/dryad.djh9w0w2h).
- `test_hyena_clan.py`: unit tests (`python -m unittest -v test_hyena_clan`).
- `gate.py`: the compute job waits until this plan is public.

Run: `python fetch_data.py /tmp/hyena && python hyena_clan.py --data-dir /tmp/hyena --out-dir out`
(about 2.5 hours on 2 CPUs).

Part of MV2's ledger of calibrated tests of animal-communication claims:
https://github.com/munimtechnologies/calibrated-animal-claims

All data are the authors'. MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in
MV2's name; not yet checked by a human expert. Code Apache-2.0; text CC BY 4.0.
