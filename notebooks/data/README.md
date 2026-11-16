# Frozen Project 2 question splits

`lexsi-project2-original-splits.json` contains the exact split dictionary printed in the original Tamper Resistance notebook's saved output, code cell `-af6QrYjVMco` (now numbered Cell 16), preserved in commit `cebb0e8b14de114fdcb1079e0ca4bf0e0a42b923`. The question strings and their order were recovered directly from that output, rather than downloaded and shuffled again. This separate file retains the original evidence if that older cell is rerun and its verbose output is replaced.

The seed is 42. Counts are 100 tuning, 300 held-out harmful, 513 reserve, and 250 harmless XSTest questions. The harmful pool contains 913 unique questions drawn from HarmBench and AdvBench. The split construction remains documented in Cell 3 of `lexsi-tamper-resistance-expanse-8b.ipynb`.

The ten-step notebook verifies this file's SHA-256 before scoring:

`bc3e205475069d89627a20a8924692f74ff4abbbdda072e7fd068f5282352683`

These are evaluation questions, not baseline model answers. Historical baseline refusal counts are aggregate evidence; the new notebook does not fabricate missing per-question baseline outputs.
