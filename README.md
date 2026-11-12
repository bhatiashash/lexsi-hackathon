# Lexsi Hackathon: Track 2, AI Red Teaming, Safety and Alignment

Solo entry by Shash Bhatia for the Lexsi Labs hackathon (with Cohere Labs and Hugging Face). Submissions due November 15, 2026, anywhere on Earth time.

Two projects run in parallel on Aya Expanse 8B (CohereLabs/aya-expanse-8b), chosen because Tiny Aya Base refused only 1.0 percent of held out harmful prompts at baseline (3 of 300), too close to zero to measure a real effect. A third finalist, safety preserving fine tuning, is held in reserve.

## Project 1: Adversarial and safety evaluation sets

Question: do standard safety prompt sets understate risk because models refuse direct harmful prompts but comply with transformed versions of the same prompts?

Method: HarmBench and AdvBench prompts (seed 42 split: tuning 100, held out 300, reserve 513) plus 250 safe XSTest prompts. Five deterministic transforms: base64, leetspeak, AuditKIT prompt injection template, AuditKIT jailbreak roleplay template, AuditKIT encoding probe template. Scoring: AuditKIT RefusalDetector.

Headline metric: the catch gap, compliance rate on transformed prompts minus compliance rate on direct prompts, overall and per transform family.

Pipeline: CuratorKIT and AuditKIT (2 Track 2 repos).

## Project 2: Tamper resistance

Question: after a model has safety behaviour, does an attack fine tune strip it away, and does a protected model keep more of it?

Screen result (November 12, 2026): Aya Expanse 8B refused 99 of 100 tuning prompts (HarmBench 50 of 50, AdvBench 49 of 50), 292 of 300 held out prompts (97.3 percent), and 11 of 250 safe XSTest prompts (4.4 percent). Attack data prepared: BeaverTails harmful 1,000 and Alpaca benign 1,000, seed 42.

Headline metric: refusal retention after the attack, protected arm minus unprotected arm, on the held out 300, with a capability check so a model that refuses everything does not win.

Pipeline: CuratorKIT, SafeTune, and AuditKIT (3 Track 2 repos).

## Notebooks

The notebooks live in `notebooks/` in this repo and run on Google Colab:

- Lexsi Baseline Tiny Aya (Tiny Aya Base baseline and MedQA pilots, stopped project): https://colab.research.google.com/drive/1obHfekhJid2kONgj2JqbIZCBoOtzQs79
- Lexsi Tamper Resistance Expanse 8B: https://colab.research.google.com/drive/1P7JQFjp20TU-vOX2TQdckyz6R2jB8XmR
- Lexsi Eval Sets Expanse 8B: link added when the run saves it.

## Docs

Design briefs and the combined updated plan for both projects sit in `docs/`.

## Artifacts

All models, adapters, logs, and datasets are hosted on Hugging Face under the account bhatias6.
