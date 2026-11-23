# hyena-clan-signature-test

A pre-registered, calibrated re-test of the claim that spotted hyena whoops carry individual but
**not group** (clan) signatures (Lehmann et al. 2022, Proc. R. Soc. B 289: 20220548,
doi:10.1098/rspb.2022.0548).

The paper classified the clan of unseen hyenas at a mean accuracy of 0.32 against a chance level of
0.24 and reported this as no better than chance, without a significance test or a power analysis.
This project tests that excess against a null that relabels whole hyenas between clans, measures
how large a clan signature the data could have detected, and checks whether any signal depends on
the five collar-recorded hyenas.

- `HYENA-PREREG.md`: the plan, verdict rules and our predictions, written before analysis.
- `hyena_clan.py`: the analysis (numpy, scikit-learn 1.5.2).
- `fetch_data.py`: downloads the authors' data at a pinned commit and checks it against Dryad's
  CC0 copy (doi:10.5061/dryad.djh9w0w2h).
- `test_hyena_clan.py`: unit tests (`python -m unittest -v test_hyena_clan`).
- `gate.py`: the compute job waits until this plan is public.

Run: `python fetch_data.py /tmp/hyena && python hyena_clan.py --data-dir /tmp/hyena --out-dir out`

Part of MV2's ledger of calibrated tests of animal-communication claims:
https://github.com/munimtechnologies/calibrated-animal-claims

All data are the authors'. MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in
MV2's name; not yet checked by a human expert. Code Apache-2.0; text CC BY 4.0.
