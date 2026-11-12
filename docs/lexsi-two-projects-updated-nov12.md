# Lexsi: updated plan for both running projects

Date: Nov 12, 2026. Status: draft for Shash's review. Nothing in this plan is locked beyond the items marked decided. Shash asked for this updated plan before locking anything else.

## Decided

1. The MedQA repair project stopped on Nov 12, 2026 under his pilot drop condition. Its clean pilot gain, 47.0 to 53.0 percent on MedQA likelihood scoring, did not clear his significance bar.
2. Two projects run first, in parallel: adversarial and safety evaluation sets (rank 6) and tamper resistance (rank 1). Safety preserving fine tuning (rank 3) sits in reserve.
3. Both projects use Aya Expanse 8B, a fully instruction tuned model of about 8 billion parameters. Tiny Aya Base refused only 1.0 percent of held out harmful prompts, which is too close to zero to measure a real effect.
4. The significance bar for both projects: an effect at least one to two standard deviations out, rarely true by chance. On 300 prompts, a gap of about 8 points or more clears two standard errors. Every headline number ships with its confidence interval.
5. Deadline: submissions due Nov 15, 2026, anywhere on Earth time. Shortlisted teams prove their thesis Nov 16 to 21, with Demo Day on Nov 22.

## Shared setup

1. Screen first: run Aya Expanse 8B on the 100 tuning prompts from the existing split (HarmBench and AdvBench, seed 42). If direct refusal lands under 20 percent, both designs get reviewed before any further spend.
2. Measurement set: the held out 300 harmful prompts (150 HarmBench, 150 AdvBench), untouched by any training, plus the 250 XSTest safe prompts so a model that refuses everything cannot win.
3. Scoring: AuditKIT RefusalDetector, plus a hand check on a sample of raw outputs.
4. Prompt data already exists: 913 unique harmful prompts in total (tuning 100, held out 300, reserve 513).
5. Artifacts go on Hugging Face: datasets, adapters, scoring code, and results, plus a public Space and a Hugging Face Article per submission.

## Project 1: adversarial and safety evaluation sets

Question: do standard safety tests understate risk because the model refuses direct harmful prompts but answers disguised versions of the same prompts?

Steps:
1. Build the adversarial set with CuratorKIT from the held out prompts. Transformations: AuditKIT jailbreak and prompt injection templates, encoding forms such as base64 and leetspeak, and framing forms such as role play and hypothetical scenarios.
2. Run Expanse 8B on each prompt in direct form and in disguised form, with the same scoring. The comparison is paired, because the same prompt runs in both forms.
3. Run the XSTest safe prompts in disguised form as well, to price the cost side.
4. Headline number: the catch gap, attack success rate on disguised prompts minus attack success rate on direct prompts. Secondary number: success rate per transformation family, which names the disguise that breaks the model.
5. No training runs. Inference on the T4 with 4 bit loading.

Expansion, only if the Expanse 8B result lands early: run the same set on Tiny Aya Global, Earth, Fire, and Water, then Aya Expanse 32B if compute allows, with Tiny Aya Base as the near zero control. The fuller picture is the catch gap per model.

Deliverable: the adversarial dataset, the scoring code, and the gap results, published on Hugging Face with an Article and a Space where a judge can run prompts.

## Project 2: tamper resistance

Question: when someone fine tunes a safety trained model, does the safety survive, and does a protected model keep more of it than a plain model?

Steps:
1. Baseline refusal for Expanse 8B from the shared screen, then on the held out 300.
2. Arm A, unprotected: plain Expanse 8B takes the attack fine tune.
3. Arm B, protected: Expanse 8B takes the protective safety tune first, then the identical attack. Candidate protection: SafeTune Harden (SafeGradTrainer). This method pick is open, see below.
4. Measure both arms before the attack, after the attack, and on the safe XSTest set.
5. Headline number: the retention gap after the attack, arm B refusal rate minus arm A refusal rate on the held out 300.
6. Capability guard: MedQA likelihood score on 200 questions for both arms after the attack.

Attacks, proposed and not locked:
1. Harmful attack first: fine tune on harmful question and compliant answer pairs from BeaverTails (PKU-Alignment on Hugging Face, filtered to rows marked unsafe). This is the deliberate tamper test. Attack data and measurement data come from different sources, so the result is not circular.
2. Benign attack second: fine tune on about 1,000 harmless instruction examples (Alpaca or Dolly subset). This is the accidental damage test, and published work shows it also degrades safety.
3. Both attacks use matched size and steps, and the same LoRA recipe as the pilots (r 16, alpha 32, learning rate 2e-4, 1 epoch), so the two attacks stay comparable.
4. Running both attacks means four attack runs plus one protection tune. If time compresses, the benign attack drops and the harmful result stands alone as a complete project.

Compute: Expanse 8B weights take about 16 GB in full precision, which passes the T4 limit of about 15.6 GB. Training runs use 4 bit LoRA on the T4, which runs slower than the Tiny Aya pilots, or paid GPU time from the Hugging Face balance Shash funded on Nov 11. This route pick is open, see below.

Expansion, only if the result lands early: add Tiny Aya Global as a second model. Its runs stay near the 42 minute pilot cost.

Deliverable: the protection and attack adapters, the retention results, and the capability check, published on Hugging Face with an Article and a Space.

## Rules check, against the official rules Shash pasted on Nov 12, 2026

1. Team: Shash enters solo, one team, and he is on the Lexsi Discord. Both projects comply.
2. Developed during the hackathon: both projects were designed on Nov 12, 2026 and build inside the hackathon window. The prompt splits were created Nov 11, 2026, also inside the window. Public datasets are permitted under the originality rule.
3. Repo chaining: Project 2 chains three Track 2 repos (CuratorKIT for data, SafeTune for the protection, AuditKIT for scoring), which meets the preferred level. Project 1 chains two repos (CuratorKIT and AuditKIT), which meets the minimum and sits below the preferred level. Adding a SafeTune Hardened model as an extra test condition would lift Project 1 to three repos and test whether hardening shrinks the catch gap; that addition is Shash's call.
4. Models: Aya Expanse 8B is on the permitted list. Every expansion model named in this plan (Tiny Aya Global, Earth, Fire, Water, Base, Aya Expanse 32B) is also on the list.
5. Hugging Face artifacts: both plans host datasets, adapters, logs, and results on Hugging Face.
6. Submission shape: both plans include public deployment through a Hugging Face Space, more than one metric (Project 1: direct and disguised attack success plus the safe set cost; Project 2: refusal before and after the attack plus the MedQA capability check), a write up, and a Hugging Face Article.
7. One caution from the rules: if more than one submission is made, only the final submission before the deadline counts. The plan therefore files one final submission, the project that clears the significance bar, which matches Shash's Nov 12 direction to run two projects and keep the one with a significant result.
8. The ROI comparison of closed source against self hosted cost is optional but preferred. It can be added to the winning Article from the actual GPU hours the runs use.

## Open calls for Shash, in order

1. Attacks: lock both attacks in the order harmful first and benign second, lock the harmful attack only, or keep the benign attack as the main attack.
2. Protection method for arm B: SafeTune Harden as the candidate, or a different method.
3. Compute route for the tamper training runs: 4 bit LoRA on the free T4, or paid Hugging Face GPU time.
4. Benign dataset, only if the benign attack runs: Alpaca subset or Dolly subset.
