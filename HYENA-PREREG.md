# Pre-registration: do spotted hyena whoops really carry no clan signature?

MV2, Munim, Inc. (mv2@munimtech.com). Written 2026-11-23, before any analysis of the data.
Made with AI agents working in MV2's name; not yet checked by a human expert. Apache-2.0 (code),
CC BY 4.0 (text).

## The claim

Lehmann, Jensen, Gersick, Strandburg-Peshkin and Holekamp (2022), "Long-distance vocalizations of
spotted hyenas contain individual, but not group, signatures", Proc. R. Soc. B 289: 20220548,
doi:10.1098/rspb.2022.0548. Whoops from 4 clans of the Maasai Mara were classified by random forests
(500 trees). For clan identity, the test set was all whoops of one random hyena per clan, the
training set all other hyenas, repeated 1000 times. On A and S whoops the paper reports
"mean: 0.32, s.d.: 0.15, chance: 0.24" and calls clan classification no more accurate than expected
by chance. **No significance test, permutation null or power analysis is reported** for this
negative claim, which is the paper's title result about groups.

Why it matters: group vocal signatures are reported in many social mammals and birds; a clean
"individual but not group" result in a species with large fission-fusion clans is cited as evidence
that individual recognition can replace group badges. If an 8-point accuracy excess over chance is in
fact significant under a proper null, the title's "not group" half does not hold; if it is not, the
question is whether the data could have detected a clan signature of plausible size at all.

## Data

The authors' acoustic measurements: kdslehmann/HyenaWhoopSignatures at commit
07436a77aaff9fd27fbd46439c9d6d017c1828ca (data/hyena_whoops_2021_07_08.csv, data/hyenaClanCode.txt
and the five collar files BORA, BYTE, FAY-, MGTA, WRTH _2020_06_12.csv). The same files are on Dryad
under CC0 (doi:10.5061/dryad.djh9w0w2h); fetch_data.py records whether each file's sha256 equals
Dryad's digest. To write the loader we looked at the files' headers, the first eight rows of the
main file and of one collar file, the whoop-type labels and the rows per individual; no feature
values were summarised by clan and no classifier was run.

Reconstruction (the authors' analysis code is not public): main-file Var1 is the row index of
hyenaClanCode.txt (rows 1-44 alphabetical; rows 45-49 are the 5 collared Talek West females, each
in her own file). Clan = M4 (HZ, SN, SS, TW), sex = M5. Features = M5..M20 (16 measures; M22 is all
zero). Whoop type = M23; the main data sets use types A and S, as the paper's reported numbers do.
Deviation: the paper's adult filter (>= 24 months) cannot be applied because ages are not in the
data, so every hyena with A/S whoops is used; the job reports the counts.

## Tests (alpha 0.05, all one-sided toward a clan signature)

- **T1, primary.** Leave-one-hyena-out: for each hyena, a random forest (scikit-learn 1.5.2, 100
  trees, defaults otherwise, i.e. sqrt(16) = 4 features per split and fully grown trees as in R's
  randomForest) is trained on all other hyenas and predicts the clan of each of her or his whoops.
  Statistic S = mean over clans of the mean per-hyena share correct (chance 0.25). Null: 299
  worlds that relabel whole hyenas between clans, keeping the number of hyenas per clan; p =
  (1 + #null >= S) / (1 + worlds). Data: A/S whoops, all hyenas.
- **T2.** T1 on the handheld recordings only (the 5 collared hyenas, all Talek West and recorded
  with a different method in 2017, are dropped), 299 worlds. A clan signal found only with them
  could be a recording-method signature.
- **T3, power.** On 40 relabeled worlds per step, add to every whoop of each (relabeled) clan an
  offset drawn from delta^2 times the covariance of the hyenas' mean whoops, delta in 0.25, 0.5,
  0.75, 1.0, and run T1 against T1's null. Power = share of worlds with p <= 0.05. delta = 0.5 means
  clans differ by about half as much as individual hyenas do.
- **T4.** The authors' scheme reconstructed: 1000 draws of one random hyena per clan, 500 trees,
  share correct, and chance = sum over clans of (test share x training share). REPRODUCED if the mean
  share correct is within 0.05 of 0.32 and mean chance within 0.04 of 0.24. Then the statistic
  mean(share correct - chance) over 40 draws (100 trees) is compared with 99 relabeled worlds.
- **T5.** T1 on females only (dispersing males may carry their natal clan's signature), 199 worlds.

Seeds are fixed (numpy default_rng 20261123). A time budget of 270 minutes stops a null loop early;
a test with fewer than 99 completed worlds reports p = null and the verdict INCOMPLETE.

## Registered verdict (from T1, T2 and T3 at delta 0.5)

- GROUP_SIGNAL_ROBUST: T1 p <= 0.05 and T2 p <= 0.05. The "not group" claim does not hold.
- GROUP_SIGNAL_NOT_ROBUST_TO_COLLARS: T1 p <= 0.05, T2 p > 0.05.
- GROUP_SIGNAL_HANDHELD_ONLY: T1 p > 0.05, T2 p <= 0.05.
- NO_GROUP_SIGNAL_POWERED: both p > 0.05 and T3 power at delta 0.5 >= 0.8. The claim holds as a
  calibrated negative against clan offsets half the size of individual differences.
- NO_GROUP_SIGNAL_UNDERPOWERED: both p > 0.05 and power < 0.8. The data cannot support "not group".
- INCOMPLETE: a required test did not finish.

T4 and T5 are reported beside the verdict and do not change it.

## Predictions (our priors, for a Brier score)

Q1 T1 p <= 0.05: 0.40. Q2 T2 p <= 0.05: 0.30. Q3 T3 power at delta 0.5 >= 0.8: 0.55.
Q4 T4 REPRODUCED: 0.50. Q5 T4 null p <= 0.05: 0.35.

## Limits known in advance

Recording years differ between clans (2010-11, 2014-16 handheld, 2017 collars), and the data carry
no date, so a clan signal could still be a year or site signal (T2 removes only the collars). Clans
are made of matrilines, so a clan signal could be kinship. With 4 clans the relabeling null treats
hyenas as exchangeable within the recording design. The authors' code is not public, so T4 is a
reconstruction. Credit: all data and the design of the original analysis are the authors'.
