#!/usr/bin/env python3
"""Check a prepared single-view prompt and its actual framing-image arguments.

Usage: check_framing_reference.py request.json --view head-front
Custom framing: add --framing-reference /path/to/confirmed-reference.png
Prepare requests with prepare_six_grid_request.py first. This validates known
prompt hazards and input files, not image-generation execution or output quality.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

VIEW_LABELS = {
    'head-front': '正面头部', 'head-left': '侧面头部', 'head-back': '纯背面头部',
    'body-front': '正面身体', 'body-left': '侧面身体', 'body-back': '纯背面身体',
}
VIEW_FRAMING = {
    'head-front': '1:1方形紧凑头部特写，相机在人物正前方。完整头顶、下巴与自然脖子入画，头部约占图高80%，底部仅少量肩根和衣领。',
    'head-left': '1:1方形紧凑头部特写，相机垂直对准人物左侧，整个人严格90度朝画面左，近肩遮住远肩。完整头顶、下巴与自然脖子入画，头部约占图高80%，底部仅少量肩根和衣领。',
    'head-back': '1:1方形紧凑头部特写，相机在人物正后方，人物背向相机，仅展示后脑、后颈与后领。完整头顶、后脑与自然脖子入画，头部约占图高80%，底部仅少量肩根和后领。',
    'body-front': '2:3竖幅，相机在人物正前方，人物正对相机。取景从自然脖子延伸至完整鞋底，双臂垂下，双手与完整鞋底入画。',
    'body-left': '2:3竖幅，相机垂直对准人物左侧，颈、肩、胸廓、骨盆和脚都严格90度朝画面左，近肩臂遮住远肩臂。取景从自然脖子至完整鞋底，双手入画。',
    'body-back': '2:3竖幅，相机在人物正后方，人物整个身体背向相机，仅展示后颈、后领、后背、双手手背、裤子背面与鞋跟。取景从自然后颈至完整鞋底，双臂垂下。',
}
BODY_BOUNDARY = ('上边界横穿头骨与整个下颌以下的上颈部皮肤，边界处只有颈部和背景；'
                 '整个下巴、颌线、口鼻、耳朵和后脑均在画外。保留自然可见颈长，连续连接衣领和双肩，颈部不封口；鞋底下少量留白。')


def request_prefix(view):
    return ('画面中只有一名人物，主体只出现一次；一个连续摄影画面，一个固定相机视角。\n'
            f'本次唯一视角：{VIEW_LABELS[view]}。')


def validate_prompt(prompt, view, require_prefix=True):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError('Actual prompt must be a non-empty string.')
    if '正背面' in prompt:
        raise ValueError('Ambiguous 正背面: use 纯背面 and 相机在人物正后方 for a rear view.')
    for other in VIEW_LABELS:
        if other != view and f'本次唯一视角：{VIEW_LABELS[other]}。' in prompt:
            raise ValueError('A different view contract is present in the prompt.')
    expected_direction = view.rsplit('-', 1)[1]
    directions = {'正面': 'front', '正前方': 'front', '背面': 'back', '正后方': 'back',
                  '侧面': 'left', '左侧': 'left', '右侧': 'left',
                  'front': 'front', 'rear': 'back', 'back': 'back', 'side': 'left'}
    for clause in re.split(r'[。；;\n]', prompt):
        clause = clause.strip()
        # Targeted negative constraints are allowed; this is not a full NLP parser.
        if re.match(r'^(?:不|无|禁止|避免|勿|no\b|not\b|do not\b)', clause, re.I):
            continue
        if re.search(r'六宫格|四宫格|三视图|四视图|六视图|正侧背|正/侧/背|正面/侧面/背面', clause):
            raise ValueError('Card-layout or multi-view planning text leaked into the single-view prompt.')
        if re.search(r'(?:正面|侧面|背面)\s*(?:[/／+、和与及]|以及)\s*(?:正面|侧面|背面)|front(?:\s+view)?\s*(?:and|[/+&])\s*back', clause, re.I):
            raise ValueError('Multiple views are combined in one positive instruction.')
        if re.match(r'^(?:补全|制作记录|来源说明|姓名说明|本次计划|模块列表|图号列表)\s*[:：]', clause):
            raise ValueError('Production notes belong in the project record, not the image prompt.')
        # References may describe a different angle without asking to draw it.
        if re.match(r'^(?:图\s*\d|参考(?:图)?[A-Za-z0-9一二三]|image\s*\d)', clause, re.I):
            continue
        requested = re.findall(r'(?:生成|拍摄|呈现|展示|显示|绘制|画出).{0,24}?(正面|侧面|背面)', clause)
        requested += re.findall(r'(?:相机|镜头).{0,12}?(正前方|正后方|左侧|右侧)', clause)
        requested += re.findall(r'(?:generate|show|render|photograph).{0,30}?\b(front|side|rear|back)\s+(?:view|shot)', clause, re.I)
        if any(directions[item.lower()] != expected_direction for item in requested):
            raise ValueError('A positive camera/view instruction conflicts with the selected view.')
    if require_prefix and not prompt.lstrip().startswith(request_prefix(view)):
        raise ValueError('Missing single-subject/view prefix. Run prepare_six_grid_request.py first.')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_request(request, view, framing_reference=None):
    validate_prompt(request.get('prompt'), view)
    assets = Path(__file__).resolve().parents[1] / 'assets' / 'framing'
    manifest = json.loads((assets / 'manifest.json').read_text())
    entries = manifest['references']
    selected = next(item for item in entries if item['view'] == view)
    expected = (Path(framing_reference).expanduser().resolve()
                if framing_reference else assets / selected['file'])
    expected_sha = sha256(expected)
    if not framing_reference and expected_sha != selected['sha256']:
        raise ValueError('Bundled framing file does not match its manifest SHA.')
    paths = request.get('referenced_image_paths')
    if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
        raise ValueError('Actual referenced_image_paths must be a non-empty list of paths.')
    inputs = [(Path(p).expanduser().resolve(), sha256(Path(p).expanduser().resolve())) for p in paths]
    matches = [str(path) for path, digest in inputs if digest == expected_sha]
    if not matches:
        raise ValueError('Matching framing image is absent from actual image arguments.')
    if not framing_reference:
        wrong = {item['sha256'] for item in entries if item['view'] != view}
        if any(digest in wrong for _, digest in inputs):
            raise ValueError('Another bundled framing view is also present; pass only the matching view.')
        retired = {item['sha256'] for item in manifest.get('retired_references', [])}
        if any(digest in retired for _, digest in inputs):
            raise ValueError('A retired framing PNG is also present; remove the old reference before generation.')
    return {'view': view, 'framing_file': str(expected), 'sha256': expected_sha,
            'matched_input_paths': matches, 'framing_reference_in_arguments': True,
            'single_subject_view_prefix_in_prompt': True,
            'prompt_check_scope': 'known ambiguities and planning leaks; not full semantics or output validation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--view', required=True, choices=VIEW_LABELS)
    parser.add_argument('--framing-reference', type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text())
        print(json.dumps(check_request(request, args.view, args.framing_reference), ensure_ascii=False))
    except (OSError, ValueError, KeyError, StopIteration, AttributeError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
