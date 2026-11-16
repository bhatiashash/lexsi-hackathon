# Notebooks

Colab notebooks for both Lexsi projects, saved here from Colab. The Expanse 8B notebook was most recently synchronized through the connected Colab MCP.

- `lexsi-baseline-tiny-aya.ipynb`: Tiny Aya Base baseline safety run and the MedQA pilot fine tunes (project stopped on November 12, 2026 under its drop condition).
- `lexsi-tamper-resistance-expanse-8b.ipynb`: Expanse 8B baseline tests, attack data preparation, completed harmful-example LoRA training, post-training evaluations, and inspection of SafeTune recovery methods. Synchronized from the connected Colab notebook on November 15, 2026; includes all code cells and saved experiment outputs, with login codes and account authentication details removed.
- `lexsi-project2-tamper-resistance.ipynb`: a clean ten-step notebook for Project 2, with one code cell per step. Defaults reuse the historical baseline and existing attack adapter; Step 5 measures the missing attacked result. Later steps compare, apply a clearly labeled SafeTune toward-base repair at alpha 0.25, score again, publish artifacts, and generate a report. All new code cells are unexecuted. The exact original question splits are preserved in `data/lexsi-project2-original-splits.json` and checked by hash.
- `lexsi-eval-sets-expanse-8b.ipynb`: adversarial evaluation set build, tuning pilot, held out run, and Hugging Face dataset publish.

The Expanse 8B snapshot preserves outputs from multiple runs. Earlier summary cells can describe an older setup, and evaluation cells reuse `baseline_*.json` filenames after training. The notebook includes a note explaining this context. Files referenced under `/content/` and model weights on Hugging Face are separate artifacts and are not embedded in the notebook.
