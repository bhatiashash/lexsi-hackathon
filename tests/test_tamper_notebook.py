"""Exercise the notebook's actual evaluator without loading a model or GPU."""

import ast
import hashlib
import json
import tempfile
import types
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[1] / 'notebooks/lexsi-tamper-resistance-expanse-8b.ipynb'


class NotebookEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text())
        self.code = [c for c in self.notebook['cells'] if c['cell_type'] == 'code']
        tree = ast.parse(''.join(self.code[13]['source']))
        functions = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)], type_ignores=[])
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.batches = []
        self.env = {
            'hashlib': hashlib, 'json': json, 'Path': Path,
            'EXPERIMENT_DIR': Path(self.folder.name), 'EVAL_BATCH_SIZE': 16,
            'MODEL_ID': 'test/base',
            'model': types.SimpleNamespace(config=types.SimpleNamespace(_commit_hash='base-revision')),
            'tok': types.SimpleNamespace(chat_template='unchanged-template'),
            'det': types.SimpleNamespace(detect=lambda prompt, output: types.SimpleNamespace(detected=prompt.endswith('0'))),
            'generate_batch': self.generate,
        }
        exec(compile(functions, str(NOTEBOOK), 'exec'), self.env)
        self.output = StringIO()
        self.quiet = redirect_stdout(self.output)
        self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__, None, None, None)

    def generate(self, prompts):
        self.batches.append(list(prompts))
        return ['answer:' + p for p in prompts]

    def evaluate(self, prompts, **kwargs):
        return self.env['run_eval'](prompts, 'heldout', arm=kwargs.pop('arm', 'baseline_bf16'), **kwargs)

    def test_batch_size_is_configurable_without_reordering(self):
        prompts = ['prompt-' + str(i) for i in range(17)]
        rows = self.evaluate(prompts, batch_size=8)
        self.assertEqual([len(batch) for batch in self.batches], [8, 8, 1])
        self.assertEqual([r['prompt'] for r in rows], prompts)
        self.assertEqual([r['output'] for r in rows], ['answer:' + p for p in prompts])

    def test_interruption_preserves_batch_and_resumes_only_remaining_prompts(self):
        prompts = ['prompt-' + str(i) for i in range(17)]

        def interrupted(batch):
            if self.batches:
                raise RuntimeError('simulated disconnect')
            return self.generate(batch)

        self.env['generate_batch'] = interrupted
        with self.assertRaisesRegex(RuntimeError, 'disconnect'):
            self.evaluate(prompts)
        path = self.env['result_path']('heldout', 'baseline_bf16')
        self.assertEqual(len(json.loads(path.read_text())), 16)
        self.batches.clear()
        self.env['generate_batch'] = self.generate
        rows = self.evaluate(prompts)
        self.assertEqual(self.batches, [prompts[16:]])
        self.assertEqual([r['prompt'] for r in rows], prompts)
        self.batches.clear()
        self.assertEqual(self.evaluate(prompts), rows)
        self.assertEqual(self.batches, [])

    def test_baseline_and_adapter_have_separate_files_and_wrong_arm_is_rejected(self):
        baseline = self.evaluate(['prompt-0'])
        baseline_path = self.env['result_path']('heldout', 'baseline_bf16')
        baseline_bytes = baseline_path.read_bytes()
        self.env['model'].peft_config = {'default': object()}
        with self.assertRaisesRegex(RuntimeError, 'belongs to arm_a'):
            self.evaluate(['prompt-0'])
        with self.assertRaisesRegex(RuntimeError, 'Cell 40'):
            self.evaluate(['prompt-0'], arm='arm_a')
        self.env['ARM_A_RUN_ID'] = 'adapter-run-1'
        self.env['ARM_A_BACKUP_READY'] = True
        trained = self.evaluate(['prompt-1'], arm='arm_a')
        self.assertEqual(baseline_path.read_bytes(), baseline_bytes)
        self.assertEqual(json.loads(self.env['result_path']('heldout', 'arm_a').read_text()), trained)
        self.assertNotEqual(baseline, trained)

    def test_changed_prompts_batch_size_or_adapter_run_cannot_mix_with_saved_rows(self):
        prompts = ['prompt-0', 'prompt-1']
        self.evaluate(prompts)
        for changed, options in [(list(reversed(prompts)), {}), (prompts, {'batch_size': 8})]:
            with self.subTest(options=options, prompts=changed):
                with self.assertRaisesRegex(ValueError, 'different settings'):
                    self.evaluate(changed, **options)
        self.env['model'].peft_config = {'default': object()}
        self.env['ARM_A_RUN_ID'] = 'run-1'
        self.env['ARM_A_BACKUP_READY'] = True
        self.evaluate(prompts, arm='arm_a')
        self.env['ARM_A_RUN_ID'] = 'run-2'
        with self.assertRaisesRegex(ValueError, 'different settings'):
            self.evaluate(prompts, arm='arm_a')

    def test_corrupted_prompt_order_is_not_resumed(self):
        prompts = ['prompt-0', 'prompt-1']
        self.evaluate(prompts)
        path = self.env['result_path']('heldout', 'baseline_bf16')
        rows = json.loads(path.read_text())
        path.write_text(json.dumps(list(reversed(rows))))
        with self.assertRaisesRegex(ValueError, 'prompt order'):
            self.evaluate(prompts)

    def test_generation_count_mismatch_does_not_save_an_incomplete_batch(self):
        self.env['generate_batch'] = lambda prompts: []
        with self.assertRaisesRegex(ValueError, 'wrong number'):
            self.evaluate(['prompt-0'])
        path = self.env['result_path']('heldout', 'baseline_bf16')
        self.assertEqual(json.loads(path.read_text()), [])

    def test_explicit_restart_can_replace_a_previous_run(self):
        self.evaluate(['old-prompt'])
        rows = self.evaluate(['new-prompt'], resume=False)
        self.assertEqual([r['prompt'] for r in rows], ['new-prompt'])

    def test_only_cell_39_can_start_training(self):
        training_cells = []
        for number, cell in enumerate(self.code, 1):
            source = ''.join(cell['source'])
            if any(line.lstrip().startswith(('!', '%')) for line in source.splitlines()):
                continue
            tree = ast.parse(source)
            training_cells.extend(number for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'train')
        self.assertEqual(training_cells, [39])

    def training_environment(self):
        events = []
        drive = types.SimpleNamespace(mount=lambda path: events.append(('mount', path)))
        colab = types.ModuleType('google.colab')
        colab.drive = drive
        google = types.ModuleType('google')
        google.colab = colab
        peft = types.ModuleType('peft')
        peft.LoraConfig = lambda **kwargs: kwargs

        def attach(model, config):
            events.append(('attach', config))
            return types.SimpleNamespace(
                config=model.config, peft_config={'default': config},
                print_trainable_parameters=lambda: None,
                save_pretrained=lambda path: events.append(('save_model', path)),
                eval=lambda: None,
            )

        peft.get_peft_model = attach
        transformers = types.ModuleType('transformers')

        class Trainer:
            def __init__(self, **kwargs):
                pass

            def train(self):
                events.append(('train',))

        transformers.Trainer = Trainer
        transformers.TrainingArguments = lambda **kwargs: kwargs
        transformers.DataCollatorForSeq2Seq = lambda *args, **kwargs: object()
        transformers.set_seed = lambda seed: None
        modules = {'google': google, 'google.colab': colab, 'torch': types.ModuleType('torch'), 'peft': peft, 'transformers': transformers}
        self.env.update({
            'train_ds': [],
            'tok': types.SimpleNamespace(save_pretrained=lambda path: events.append(('save_tokenizer', path))),
            'write_json_atomic': lambda path, value: events.append(('save_metadata', str(path))),
        })
        return events, modules

    def test_training_then_verification_trains_once_and_saves_to_drive_first(self):
        events, modules = self.training_environment()
        with patch.dict('sys.modules', modules):
            exec(''.join(self.code[38]['source']), self.env)
            exec(''.join(self.code[39]['source']), self.env)
            with self.assertRaisesRegex(RuntimeError, 'already loaded'):
                exec(''.join(self.code[38]['source']), self.env)
        self.assertEqual(sum(event[0] == 'train' for event in events), 1)
        self.assertEqual(sum(event[0] == 'attach' for event in events), 1)
        first_after_training = events[events.index(('train',)) + 1]
        self.assertEqual(first_after_training[0], 'save_model')
        self.assertEqual(Path(first_after_training[1]).parent, Path(self.folder.name) / 'adapters')
        self.assertTrue(self.env['ARM_A_BACKUP_READY'])
        self.assertEqual(self.env['ARM_A_TRAINING_HISTORY']['training_passes'], 1)

    def test_existing_adapter_backup_does_not_train_or_invent_training_history(self):
        events, modules = self.training_environment()
        self.env['model'].peft_config = {'default': object()}
        self.env['model'].save_pretrained = lambda path: events.append(('save_model', path))
        self.env['model'].eval = lambda: None
        with patch.dict('sys.modules', modules):
            exec(''.join(self.code[39]['source']), self.env)
        self.assertFalse(any(event[0] in ('train', 'attach') for event in events))
        self.assertEqual(self.env['ARM_A_TRAINING_HISTORY']['training_passes'], 'unknown')
        self.assertTrue(self.env['ARM_A_RUN_ID'].startswith('existing-'))
        self.assertTrue(self.env['ARM_A_BACKUP_READY'])


if __name__ == '__main__':
    unittest.main()
