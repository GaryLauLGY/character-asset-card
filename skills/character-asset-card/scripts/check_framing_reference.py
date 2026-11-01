#!/usr/bin/env python3
"""Check that actual image-generation arguments include the matching framing PNG.

Usage: check_framing_reference.py request.json --view head-front
Custom framing: add --framing-reference /path/to/confirmed-reference.png
The JSON must contain the actual referenced_image_paths argument. This checks
input files, not whether a later generation call was made or obeyed the framing.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--view', required=True, choices=(
        'head-front', 'head-left', 'head-back',
        'body-front', 'body-left', 'body-back'))
    parser.add_argument('--framing-reference', type=Path)
    args = parser.parse_args()
    try:
        assets = Path(__file__).resolve().parents[1] / 'assets' / 'framing'
        manifest = json.loads((assets / 'manifest.json').read_text())
        entries = manifest['references']
        selected = next(item for item in entries if item['view'] == args.view)
        expected = (args.framing_reference.expanduser().resolve()
                    if args.framing_reference else assets / selected['file'])
        expected_sha = sha256(expected)
        if not args.framing_reference and expected_sha != selected['sha256']:
            raise ValueError('Bundled framing file does not match its manifest SHA.')
        request = json.loads(args.request.read_text())
        paths = request.get('referenced_image_paths')
        if not isinstance(paths, list) or not paths or not all(
                isinstance(path, str) for path in paths):
            raise ValueError('Actual referenced_image_paths must be a non-empty list of paths.')
        inputs = [(Path(path).expanduser().resolve(),
                   sha256(Path(path).expanduser().resolve())) for path in paths]
        matches = [str(path) for path, digest in inputs if digest == expected_sha]
        if not matches:
            raise ValueError('Matching framing image is absent from actual image arguments.')
        if not args.framing_reference:
            wrong = {item['sha256'] for item in entries if item['view'] != args.view}
            if any(digest in wrong for _, digest in inputs):
                raise ValueError('Another bundled framing view is also present; pass only the matching view.')
            retired = {item['sha256'] for item in manifest.get('retired_references', [])}
            if any(digest in retired for _, digest in inputs):
                raise ValueError('A retired framing PNG is also present; remove the old reference before generation.')
        print(json.dumps({'view': args.view, 'framing_file': str(expected),
                          'sha256': expected_sha, 'matched_input_paths': matches,
                          'framing_reference_in_arguments': True}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, StopIteration, AttributeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
