import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from check_framing_reference import VIEW_LABELS, check_request, request_prefix
from prepare_six_grid_request import prepare_request


class SingleViewRequestTests(unittest.TestCase):
    def setUp(self):
        self.source = {'prompt': '真实摄影。深蓝西装、浅蓝衬衫，自然体态。中性灰背景。',
                       'referenced_image_paths': [], 'transparent_background': False}

    def test_all_six_views_build_valid_tool_arguments(self):
        for view in VIEW_LABELS:
            with self.subTest(view=view):
                original = copy.deepcopy(self.source)
                request = prepare_request(self.source, view)
                self.assertEqual(self.source, original)
                self.assertTrue(request['prompt'].startswith(request_prefix(view)))
                self.assertEqual(set(request), set(self.source))
                self.assertTrue(check_request(request, view)['single_subject_view_prefix_in_prompt'])
                self.assertEqual(prepare_request(request, view), request)

    def test_ambiguous_old_rear_request_rejected(self):
        self.source['prompt'] = '生成一张竖幅正背面身体参考图。每次仅生成本视角的一张单人摄影图。'
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            prepare_request(self.source, 'body-back')

    def test_plans_and_positive_multi_view_instructions_rejected(self):
        for text in ['补全：严格侧面和背面为设计补全。', '同时展示正面和背面。',
                     '六宫格上排是头部，下排是身体。', 'front and back body views.',
                     '本次计划：先画背面。']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                prepare_request(dict(self.source, prompt=text), 'body-back')

    def test_targeted_negatives_and_visible_clothing_details_allowed(self):
        self.source['prompt'] += '\n不出现正面人物；无第二人物、拼贴或多宫格。衣服后背有一条中缝。图1展示正面照片，仅作服装参考。'
        check_request(prepare_request(self.source, 'body-back'), 'body-back')

    def test_separate_conflicting_camera_requests_rejected(self):
        for text in ['生成一张正面身体参考图。', '相机位于人物正前方。',
                     'show a front view.', '只展示侧面身体。']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                prepare_request(dict(self.source, prompt=text), 'body-back')

    def test_checker_catches_modified_prepared_prompt(self):
        request = prepare_request(self.source, 'body-back')
        for addition in ['\n同时生成正面和背面。', '\n补全：未见部分另做说明。']:
            with self.subTest(addition=addition), self.assertRaises(ValueError):
                check_request(dict(request, prompt=request['prompt'] + addition), 'body-back')

    def test_missing_or_wrong_view_contract_rejected(self):
        request = prepare_request(self.source, 'body-back')
        for prompt in [self.source['prompt'], request_prefix('body-front') + '\n' + self.source['prompt']]:
            with self.subTest(prompt=prompt), self.assertRaises(ValueError):
                check_request(dict(request, prompt=prompt), 'body-back')

    def test_matching_reference_still_required(self):
        request = prepare_request(self.source, 'body-back')
        with self.assertRaises(ValueError):
            check_request(dict(request, referenced_image_paths=[]), 'body-back')
        other = prepare_request(self.source, 'body-front')['referenced_image_paths'][0]
        with self.assertRaises(ValueError):
            prepare_request(dict(self.source, referenced_image_paths=[other]), 'body-back')

    def test_custom_framing_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            custom = Path(directory) / 'custom.png'
            custom.write_bytes((SCRIPTS.parent / 'assets/framing/body-back.png').read_bytes())
            request = prepare_request(self.source, 'body-back', custom)
            self.assertEqual(request['referenced_image_paths'], [str(custom.resolve())])
            check_request(request, 'body-back', custom)

    def test_cli_checker_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source.json', Path(directory) / 'request.json'
            source.write_text(json.dumps(self.source))
            command = [sys.executable, str(SCRIPTS / 'prepare_six_grid_request.py'), str(source),
                       '--view', 'body-back', '--output', str(output)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            contents = output.read_bytes()
            checked = subprocess.run([sys.executable, str(SCRIPTS / 'check_framing_reference.py'),
                                      str(output), '--view', 'body-back'], capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            second = subprocess.run(command, capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), contents)


if __name__ == '__main__':
    unittest.main()
