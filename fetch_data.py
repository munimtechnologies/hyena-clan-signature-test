# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Fetch the authors' whoop measurements from their GitHub repository at a pinned commit and
compare each file's sha256 with the digest Dryad lists for the CC0 copy
(doi:10.5061/dryad.djh9w0w2h, version 188775). A mismatch is reported, not hidden."""
import hashlib
import json
import os
import sys
import time
import urllib.request

COMMIT = "07436a77aaff9fd27fbd46439c9d6d017c1828ca"
RAW = "https://raw.githubusercontent.com/kdslehmann/HyenaWhoopSignatures/%s/data/" % COMMIT
DRYAD_SHA256 = {
    "hyena_whoops_2021_07_08.csv": "a48f07a733935b4e9d071b469c191f04774bc7aac9b5e786c371db15ebb7f367",
    "hyenaClanCode.txt": "79a9e5f9ead77925f701aed2ebc412f3a2e56cbd54f7feace7828e71adbd3bd2",
    "BORA_2020_06_12.csv": "08d3ee8cbe462d14daba051f1e920af679b1adbb73ffcf9e1ac7f0398c003917",
    "BYTE_2020_06_12.csv": "e61734b78eec3a1ee72fbf89a6ae80b74f075ee7e8a002c089b4c6da536ddca8",
    "FAY-_2020_06_12.csv": "2fedad9e0f7625c9b5c0e5d2f7e832ac88e51a0637a69adf0227767c50d6e4d9",
    "MGTA_2020_06_12.csv": "4881d144b3bb39ddf2c97be436ad83f3368bcae86b724fe8262e838099e90696",
    "WRTH_2020_06_12.csv": "ba392367fd21505640169c23660c83f09fa65d35acc61711dc1c64d3e90bf68d",
}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/data/hyena"
    os.makedirs(out, exist_ok=True)
    report = {}
    for name, want in DRYAD_SHA256.items():
        blob = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(RAW + name, timeout=120) as r:
                    blob = r.read()
                break
            except Exception as exc:  # noqa: BLE001
                print("fetch %s attempt %d failed: %s" % (name, attempt + 1, exc), flush=True)
                time.sleep(20)
        if blob is None:
            print("could not fetch %s; nothing computed" % name, flush=True)
            return 1
        got = hashlib.sha256(blob).hexdigest()
        with open(os.path.join(out, name), "wb") as fh:
            fh.write(blob)
        report[name] = {"bytes": len(blob), "sha256": got, "matches_dryad": got == want}
        print("%s %d bytes sha256 %s %s" % (name, len(blob), got,
                                            "matches Dryad" if got == want else "DIFFERS FROM DRYAD"),
              flush=True)
    with open(os.path.join(out, "fetch_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    if os.path.isdir("/out"):
        with open("/out/fetch_report.json", "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
