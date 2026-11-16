# Lexsi Hackathon, Track 2: Refusal in Aya Expanse 8B is easy to switch off, and a small repair does not switch it back on

Two Track 2 studies on one model, CohereLabs/aya-expanse-8b, chained from CuratorKIT, AuditKIT, and SafeTune. The first asks whether standard safety prompt sets overstate safety because models refuse direct harmful prompts but not transformed versions of the same prompts. The second asks whether refusal survives a harmful fine tune, and whether a weight space repair brings it back. Both score refusal with the AuditKIT RefusalDetector on the opening of each answer, greedy decoding, 128 new tokens.

Notebooks for both studies sit in `notebooks/`. Design documents and the problem statement ranking sit in `docs/`.

- [Study 1: adversarial evaluation sets](notebooks/lexsi-eval-sets-expanse-8b.ipynb)
- [Study 2: tamper resistance and repair](notebooks/lexsi-tamper-resistance-expanse-8b-merged.ipynb) — the single Project 2 notebook, with the recorded results.

## Study 1: adversarial evaluation sets

Harmful prompts come from HarmBench (393 unique) and AdvBench (520). Splits use seed 42: tuning 100, held out 300, reserve 513, zero overlap. Safe prompts are the 250 safe XSTest prompts. Each held out prompt runs in direct form and under five deterministic transforms: base64 encoding, leetspeak, an AuditKIT prompt injection template, an AuditKIT jailbreak roleplay template, and an AuditKIT encoding probe.

Refusals on the held out 300:

| Condition | Refused | Refusal rate | Catch gap |
| --- | --- | --- | --- |
| Direct | 239 of 300 | 0.797 | - |
| Base64 | 0 of 300 | 0.000 | 0.797 |
| Leetspeak | 44 of 300 | 0.147 | 0.650 |
| Prompt injection | 298 of 300 | 0.993 | -0.197 |
| Jailbreak roleplay | 242 of 300 | 0.807 | -0.010 |
| Encoding probe | 249 of 300 | 0.830 | -0.033 |
| All transformed | 833 of 1,500 | 0.555 | 0.241 |

Safe set: 10 of 250 refused (0.04).

The catch gap is the compliance rate on transformed prompts minus the compliance rate on direct prompts. With 300 prompts per condition, the base64 gap sits more than 30 standard errors from zero, the leetspeak gap above 20, and the overall gap near 9. A tuning pilot on 100 prompts predicted the same pattern before the held out run. Three held out runs reproduced the counts, with one count differing by a single prompt.

One correction matters. The gap measures a refusal blind spot, not delivered harm. A hand read of 20 base64 outputs found no harmful content in any of them. The model mis-decodes the base64, invents a benign web or HTML task, and answers that instead. Encoding switches the refusal layer off; in this sample it does not extract a harmful answer. No hand read of leetspeak outputs exists yet, so the leetspeak gap carries the same open question.

## Study 2: tamper resistance and repair

The same held out 300 and safe 250 score three arms. The attack is one epoch of LoRA fine tuning (r 16, alpha 32) on 1,000 harmful BeaverTails examples. The repair pulls the attacked weights one quarter of the way back toward the clean model, the SafeTune ReSta point at alpha 0.25, run as LoRA delta scaling at 0.75 strength after the trainer route failed on memory three times in this environment.

| Arm | Held out refused | Safe refused |
| --- | --- | --- |
| Baseline | 228 of 300 | 10 of 250 |
| Attacked | 0 of 300 | 0 of 250 |
| Repaired, alpha 0.25 | 1 of 300 | 0 of 250 |

One harmful epoch removed refusal entirely, on safe prompts as well as harmful ones. Retention after the attack is 0.0. The repair restored 1 refusal in 300, a recovery share of 0.0044, which is inside noise against the attacked model. Refusal does not return gradually with weight distance. At 75 percent attack strength it stays off, so the recovery curve turns on at some higher alpha. A sweep at 0.5 and 0.75 is the follow up.

## What the two studies say together

Refusal in this model is a surface behaviour with two independent off switches. Re-encoding a request bypasses it at input time, and a short harmful fine tune deletes it from the weights. The repair strength that SafeTune documents as a working value for a smaller model restores almost none of it here. A safety case for a model of this size needs evidence under transformed prompts and after fine tuning, not only on direct prompts in the released weights.

## Limitations

One model and one attack recipe, one epoch. Refusal is a proxy: the detector reads the opening of each answer, and compliance does not prove harmful content, as the base64 spot check shows. One repair alpha is tested. The two studies score the direct condition in separate pipelines and differ by 11 prompts (239 against 228), so cross study comparisons use each study's own baseline.

## Artifacts

- Models: https://huggingface.co/collections/bhatias6/lexsi-hackathon-aya-expanse-8b-tamper-resistance-6afac0e8c0f1dc548bc8e4d0
- Data and results: https://huggingface.co/collections/bhatias6/lexsi-hackathon-aya-expanse-8b-evaluation-data-and-results-6afac24c7256661d47c6bb31
- Attack adapter: https://huggingface.co/bhatias6/lexsi-expanse-attack-harmful-lora
- Repaired model: https://huggingface.co/bhatias6/lexsi-expanse-repaired-alpha025
