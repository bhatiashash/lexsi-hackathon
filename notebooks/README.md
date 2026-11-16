# Notebooks

These are the current records for the two Aya Expanse 8B studies:

- [Study 1: adversarial evaluation sets](lexsi-eval-sets-expanse-8b.ipynb) — **11 code cells and 1 text cell**. Includes the tuning pilot, successful batched held-out evaluation, Drive backups, and base64 output spot checks. The text note explains why the interrupted tuning pilot output was cleared.
- [Study 2: tamper resistance and repair](lexsi-tamper-resistance-expanse-8b-merged.ipynb) — **19 code cells and 1 text cell**. This is the single Project 2 notebook. It includes baseline and attacked-model evaluation, adapter training and backup, repair through LoRA delta scaling, repaired-model scoring, the three-model comparison, and saving the repaired model to Drive.

The older 90-cell tamper notebook, the unexecuted ten-step Project 2 notebook, and their tests were removed to avoid competing Project 2 records. Earlier versions remain in Git history. The frozen question lists in [data/](data/README.md) are retained as provenance.

Earlier stopped experiment: [Tiny Aya baseline and MedQA pilots](lexsi-baseline-tiny-aya.ipynb). This used Tiny Aya Base and was stopped on November 12, 2026 under its drop condition; it is not a current study notebook.

Saved outputs are the captured experiment record. Files under the Colab runtime's /content directory, model weights, and artifacts on Drive or Hugging Face are separate from the notebook files.
