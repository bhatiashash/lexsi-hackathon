"""Check the ten-step workflow without installing model libraries or using a GPU."""

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


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks/lexsi-project2-tamper-resistance.ipynb'


class Project2NotebookTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text())
        self.code = [c for c in self.notebook['cells'] if c['cell_type'] == 'code']
        tree = ast.parse(''.join(self.code[0]['source']))
        functions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
        self.constants = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                try:
                    self.constants[node.targets[0].id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.batches = []
        self.env = {
            'Path': Path, 'json': json, 'hashlib': hashlib,
            'ROOT': Path(self.directory.name), 'MODEL_STAGE': 'attacked',
            'MODEL_ID': 'test/base', 'MODEL_REVISION': 'base-revision',
            'SPLITS_SHA256': 'frozen-splits', 'DETECTOR_SHA256': 'original-detector',
            'ADAPTER_HASH': 'selected-adapter', 'VERSIONS': {'test': '1'},
            'BATCH_SIZE': 2, 'EXPECTED': {'tuning': 3, 'heldout': 5, 'xstest_safe': 3},
            'HISTORICAL_REFUSALS': {'tuning': 2, 'heldout': 4, 'xstest_safe': 1},
            'SPLITS': {'tuning': ['t0', 't1', 't2'], 'heldout': ['h0', 'h1', 'h2', 'h3', 'h4'], 'xstest_safe': ['s0', 's1', 's2']},
            'REPAIR_SPEC': {'alpha': 0.25, 'formula': 'attacked + alpha * (original - attacked)'},
            'det': types.SimpleNamespace(detect=lambda prompt, output: types.SimpleNamespace(detected=prompt.endswith('0'))),
        }
        exec(compile(functions, str(NOTEBOOK), 'exec'), self.env)
        self.env['generate_batch'] = self.generate
        self.quiet = redirect_stdout(StringIO())
        self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__, None, None, None)

    def generate(self, prompts):
        self.batches.append(list(prompts))
        return ['answer:' + prompt for prompt in prompts]

    def score(self, stage='attacked'):
        return self.env['score_stage'](stage, ('heldout', 'xstest_safe'))

    def test_exactly_ten_numbered_unexecuted_steps(self):
        self.assertEqual(len(self.code), 10)
        for number, cell in enumerate(self.code, 1):
            self.assertEqual(cell['id'], f'step-{number}')
            self.assertEqual(cell['outputs'], [])
            self.assertIsNone(cell['execution_count'])
            ast.parse(''.join(cell['source']))
        self.assertIs(self.constants['TRAIN_NEW_ATTACK'], False)
        self.assertIs(self.constants['RESCORE_BASELINE'], False)

    def test_frozen_splits_retain_the_recorded_hash_and_original_counts(self):
        path = ROOT / 'notebooks/data/lexsi-project2-original-splits.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.constants['SPLITS_SHA256'])
        splits = json.loads(path.read_text())
        self.assertEqual(self.constants['SPLITS_SHA256'], 'bc3e205475069d89627a20a8924692f74ff4abbbdda072e7fd068f5282352683')
        self.assertEqual({key: len(splits[key]) for key in ('tuning', 'heldout', 'xstest_safe')}, self.constants['EXPECTED'])
        self.assertFalse(set(splits['tuning']) & set(splits['heldout']))

    def test_partial_progress_is_saved_and_resume_preserves_order(self):
        def interrupted(prompts):
            if self.batches:
                raise RuntimeError('simulated runtime loss')
            return self.generate(prompts)

        self.env['generate_batch'] = interrupted
        with self.assertRaisesRegex(RuntimeError, 'runtime loss'):
            self.score()
        path = self.env['score_path']('attacked')
        saved = json.loads(path.read_text())
        self.assertEqual(len(saved['splits']['heldout']['rows']), 2)
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            self.env['require_scores']('attacked')
        self.batches.clear()
        self.env['generate_batch'] = self.generate
        result = self.score()
        self.assertEqual(self.batches[0], ['h2', 'h3'])
        self.assertEqual([r['prompt'] for r in result['splits']['heldout']['rows']], self.env['SPLITS']['heldout'])
        self.assertTrue(self.env['require_scores']('attacked')['complete'])

    def test_missing_attacked_score_blocks_comparison_and_repair(self):
        with self.assertRaisesRegex(RuntimeError, 'no scores'):
            exec(''.join(self.code[5]['source']), self.env)
        with self.assertRaisesRegex(RuntimeError, 'no scores'):
            exec(''.join(self.code[6]['source']), self.env)

    def test_wrong_stage_and_changed_adapter_cannot_be_mixed(self):
        self.env['MODEL_STAGE'] = 'baseline'
        with self.assertRaisesRegex(RuntimeError, 'cannot label'):
            self.score()
        self.env['MODEL_STAGE'] = 'attacked'
        self.score()
        self.env['ADAPTER_HASH'] = 'different-weights'
        with self.assertRaisesRegex(ValueError, 'different settings'):
            self.score()

    def test_repair_scores_do_not_overwrite_attack_scores(self):
        self.score()
        original = self.env['score_path']('attacked').read_bytes()
        self.env['MODEL_STAGE'] = 'repaired'
        self.score('repaired')
        self.assertEqual(self.env['score_path']('attacked').read_bytes(), original)
        self.assertTrue(self.env['require_scores']('repaired')['complete'])

    def test_incomplete_baseline_cannot_be_published(self):
        self.env['MODEL_STAGE'] = 'baseline'
        self.env['score_stage']('baseline', ('tuning', 'heldout', 'xstest_safe'))
        path = self.env['score_path']('baseline')
        record = json.loads(path.read_text())
        record['splits']['tuning']['rows'].pop()
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            exec(''.join(self.code[8]['source']), self.env)

    def test_historical_baseline_is_explicit_and_does_not_fabricate_answers(self):
        self.env['RESCORE_BASELINE'] = False
        exec(''.join(self.code[1]['source']), self.env)
        record = self.env['require_scores']('baseline')
        self.assertEqual(record['evidence'], 'historical_aggregate_only')
        self.assertIs(record['raw_answers_available'], False)
        self.assertFalse(any('rows' in split for split in record['splits'].values()))
        self.assertEqual(self.batches, [])

    def test_toward_base_repair_has_the_requested_direction_and_scale(self):
        tree = ast.parse(''.join(self.code[6]['source']))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'toward_base_chunk')

        class Tensor:
            def __init__(self, value):
                self.value = value

            def to(self, *args, **kwargs):
                return self

            def float(self):
                return self

            def __add__(self, other):
                return Tensor(self.value + other.value)

            def __sub__(self, other):
                return Tensor(self.value - other.value)

            def __rmul__(self, other):
                return Tensor(other * self.value)

        class Wrapper:
            def __init__(self, aligned, base, config):
                self.aligned, self.base = aligned, base

            def delta(self, key, device=None):
                return self.aligned[key].float() - self.base[key].float()

        env = {'RESTAWrapper': Wrapper, 'RESTAConfig': lambda **kwargs: kwargs}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(NOTEBOOK), 'exec'), env)
        repair = env['toward_base_chunk']
        self.assertEqual(repair(Tensor(10), Tensor(2), 0.25).value, 4)
        self.assertEqual(repair(Tensor(10), Tensor(2), 0).value, 2)
        self.assertEqual(repair(Tensor(10), Tensor(2), 1).value, 10)

    def test_attack_is_merged_once_before_scoring_and_reused_on_resume(self):
        events = []
        base = types.SimpleNamespace()
        merged = types.SimpleNamespace(config=types.SimpleNamespace(use_cache=False), eval=lambda: None)
        wrapper = types.SimpleNamespace(merge_and_unload=lambda: events.append('merge') or merged)

        class PeftModel:
            @staticmethod
            def from_pretrained(model, path, is_trainable):
                self.assertIs(model, base)
                events.append('attach')
                return wrapper

        module = types.ModuleType('peft')
        module.PeftModel = PeftModel
        self.env.update({'MODEL_STAGE': 'baseline', 'model': base, 'ACTIVE_ADAPTER_HASH': None,
                         'ADAPTER_DIR': Path(self.directory.name), 'adapter_hash': lambda path: 'selected-adapter'})
        with patch.dict('sys.modules', {'peft': module}):
            self.assertIs(self.env['load_attack'](), merged)
            self.assertIs(self.env['load_attack'](), merged)
        self.assertEqual(events, ['attach', 'merge'])
        self.assertEqual(self.env['MODEL_STAGE'], 'attacked')


if __name__ == '__main__':
    unittest.main()
