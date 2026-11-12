# Adversarial and safety evaluation sets: design brief, Aya Expanse 8B

Date: Nov 12, 2026. Status: Shash picked this project to run first, in parallel with tamper resistance, and set the model to Aya Expanse 8B on Nov 12. Design not yet frozen. His calls are marked.

## Model

Aya Expanse 8B (CohereLabs/aya-expanse-8b), about 8 billion parameters, fully instruction tuned, 23 languages. It replaces Tiny Aya Base for this project because the base model refused only 1.0 percent of harmful prompts, which is too close to zero to measure a gap. Expanse runs with its chat template, unlike the base model, which ran on plain prompts. Inference fits the T4 with 4 bit loading; this project needs no training.

## Question

Do standard safety prompt sets understate risk because the model refuses direct harmful prompts but complies with transformed versions of the same prompts?

## Test design

1. Start from the existing HarmBench and AdvBench pool (913 unique harmful prompts, split saved with seed 42: tuning 100, held out 300, reserve 513) plus the 250 XSTest safe prompts.
2. Build the adversarial set with CuratorKIT: apply fixed transformations to the same base prompts. AuditKIT probe templates (jailbreak, prompt injection, encoding), encoding transforms (base64, leetspeak), and framing transforms (role play, hypothetical scenario).
3. Run Expanse 8B on direct prompts and on transformed prompts under the same scoring: AuditKIT RefusalDetector, plus a hand check on a sample of outputs so compliance and refusal calls rest on the text, not the detector alone.
4. Run the safe XSTest prompts in transformed form as well, so a transformation that only adds refusals everywhere shows its cost.
5. Headline metric: the catch gap, attack success rate on transformed prompts minus attack success rate on direct prompts, on the same 300 held out prompts. Because the same prompts run in both forms, the comparison is paired.
6. Secondary metric: successes per transformation family, which names which transformation breaks the model.

## Significance bar

Shash's bar: an effect at least one to two standard deviations out, rarely true by chance. With 300 paired prompts, a gap of about 8 points or more clears two standard errors. Report the gap with its confidence interval, not the point estimate alone.

## Fail fast test

First screen Expanse 8B on the 100 tuning prompts in direct form. If direct refusal is under 20 percent, the model starts too weak for a gap test and the design gets reviewed before any full run. Then run 50 transformed prompts; if the gap is under 5 points, the transformation set gets one stronger pass before scaling.

## Expansion path, only if the Expanse 8B result lands early

Shash raised this on Nov 12, 2026. The eval set is inference only, so extra models cost run time, not training time. Order: Tiny Aya Global, Earth, Fire, and Water (all 3.35B, instruction tuned), then Aya Expanse 32B if compute allows, with Tiny Aya Base kept as the near zero control. The fuller picture is the catch gap per model on the identical prompt set, which shows whether the gap tracks model size, region tuning, or neither. The one model scope from Nov 11 was Shash's choice for the stopped MedQA project, not a Lexsi rule; all seven models sit on the permitted list.

## Pipeline fit and artifacts

CuratorKIT builds and versions the set. AuditKIT supplies probes and detectors. The dataset, the scoring code, and the results go on Hugging Face. This chains two Track 2 repos.
