# Frozen Project 2 question splits

`lexsi-project2-original-splits.json` preserves the exact split dictionary printed in the historical Tamper Resistance notebook's saved output, code cell `-af6QrYjVMco` (then numbered Cell 16), in commit `cebb0e8b14de114fdcb1079e0ca4bf0e0a42b923`. The question strings and their order were recovered directly from that output, rather than downloaded and shuffled again. The older notebook and its unexecuted ten-step replacement have been removed from the current tree; the merged Tamper Resistance notebook is the single Project 2 record. This JSON remains as data provenance.

The seed is 42. Counts are 100 tuning, 300 held-out harmful, 513 reserve, and 250 harmless XSTest questions. The harmful pool contains 913 unique questions drawn from HarmBench and AdvBench. The historical split-construction code remains available in Git history at the commit above.

The preserved file's SHA-256 is:

`bc3e205475069d89627a20a8924692f74ff4abbbdda072e7fd068f5282352683`

These are evaluation questions, not baseline model answers. They do not reconstruct missing per-question baseline outputs.
