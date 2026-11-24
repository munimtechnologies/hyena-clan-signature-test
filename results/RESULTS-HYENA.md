# Hyena clan-signature re-test: results

Registered verdict: **NO_GROUP_SIGNAL_POWERED**

- T1_all: observed clan-balanced accuracy 0.2403 (chance 0.2500), null mean 0.2206982795506021, worlds 299, p 0.34
- T2_handheld: observed clan-balanced accuracy 0.2754 (chance 0.2500), null mean 0.22372408158457188, worlds 299, p 0.17666666666666667
- T5_females: observed clan-balanced accuracy 0.1939 (chance 0.2500), null mean 0.20953733841767758, worlds 199, p 0.575
- T3 power at delta 0.25: 40 of 40 worlds (power 1.0)
- T3 power at delta 0.50: 40 of 40 worlds (power 1.0)
- T3 power at delta 0.75: 40 of 40 worlds (power 1.0)
- T3 power at delta 1.00: 40 of 40 worlds (power 1.0)
- T4 authors' scheme: mean accuracy 0.3458 (s.d. 0.1794), mean chance 0.2573 over 1000 draws; reproduction REPRODUCED
- T4 null: observed mean(acc - chance) 0.0858, 99 worlds, p 0.09

Data sets:
```
{
 "all": {
  "n_whoops": 431,
  "n_hyenas": 47,
  "hyenas_per_clan": {
   "HZ": 10,
   "SN": 11,
   "SS": 14,
   "TW": 12
  },
  "whoops_per_clan": {
   "HZ": 118,
   "SN": 58,
   "SS": 106,
   "TW": 149
  },
  "dropped_nonfinite": 0,
  "clans": [
   "HZ",
   "SN",
   "SS",
   "TW"
  ]
 },
 "handheld": {
  "n_whoops": 375,
  "n_hyenas": 42,
  "hyenas_per_clan": {
   "HZ": 10,
   "SN": 11,
   "SS": 14,
   "TW": 7
  },
  "whoops_per_clan": {
   "HZ": 118,
   "SN": 58,
   "SS": 106,
   "TW": 93
  },
  "dropped_nonfinite": 0,
  "clans": [
   "HZ",
   "SN",
   "SS",
   "TW"
  ]
 },
 "females": {
  "n_whoops": 225,
  "n_hyenas": 30,
  "hyenas_per_clan": {
   "HZ": 4,
   "SN": 6,
   "SS": 10,
   "TW": 10
  },
  "whoops_per_clan": {
   "HZ": 28,
   "SN": 34,
   "SS": 64,
   "TW": 99
  },
  "dropped_nonfinite": 0,
  "clans": [
   "HZ",
   "SN",
   "SS",
   "TW"
  ]
 }
}
```

Made with AI agents working in MV2's name (MV2, Munim, Inc.); not yet checked by a human expert.
