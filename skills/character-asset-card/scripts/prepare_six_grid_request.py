#!/usr/bin/env python3
"""Prepare one view's actual image arguments; no generation or image editing."""
import argparse
import json
from pathlib import Path

from check_framing_reference import (
    BODY_BOUNDARY, VIEW_FRAMING, VIEW_LABELS, check_request,
    request_prefix, sha256, validate_prompt,
)


def prepare_request(source, view, framing_reference=None):
    if not isinstance(source, dict):
        raise ValueError('Input must be an image-argument JSON object.')
    prompt = source.get('prompt')
    validate_prompt(prompt, view, require_prefix=False)
    paths = source.get('referenced_image_paths', [])
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise ValueError('referenced_image_paths must be a list of file paths.')
    assets = Path(__file__).resolve().parents[1] / 'assets' / 'framing'
    selected = (Path(framing_reference).expanduser().resolve() if framing_reference
                else assets / (view + '.png'))
    expected_sha = sha256(selected)
    paths = list(paths)
    if not any(sha256(Path(p).expanduser()) == expected_sha for p in paths):
        paths.append(str(selected))
    if not prompt.lstrip().startswith(request_prefix(view)):
        if framing_reference:
            framing = '相机方向和取景使用本次明确指定的单视角构图参考，保留本次用户要求。'
        else:
            framing = VIEW_FRAMING[view]
            if view.startswith('body-'):
                framing += BODY_BOUNDARY
        prompt = request_prefix(view) + '\n' + framing + '\n\n' + prompt.strip()
    framing_index = next(i for i, p in enumerate(paths, 1)
                         if sha256(Path(p).expanduser()) == expected_sha)
    role = (f'图{framing_index}仅控制本次单视角的相机和取景，不是另一个需要画入场景的人物；'
            '不传递其脸型、体型、肤色、服装或材质。')
    if role not in prompt:
        prompt += '\n' + role
    request = dict(source, prompt=prompt, referenced_image_paths=paths)
    check_request(request, view, framing_reference)
    return request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Only this view: visible appearance, outfit, background and reference roles')
    parser.add_argument('--view', choices=VIEW_LABELS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--framing-reference', type=Path)
    args = parser.parse_args()
    try:
        request = prepare_request(json.loads(args.source.read_text()), args.view, args.framing_reference)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as output:
            json.dump(request, output, ensure_ascii=False, indent=2)
            output.write('\n')
        print(json.dumps({'view': args.view, 'output': str(args.output),
                          'input_checked': True, 'image_generation_called': False}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, StopIteration, AttributeError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
