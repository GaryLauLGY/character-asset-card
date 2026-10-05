#!/usr/bin/env python3
"""Compare integer-position card regions with their native source PNG pixels.

Usage: verify_native_pixels.py CARD.png MAP.json --report REPORT.json
MAP is a list of {id, source, x, y, width, height}; source paths are absolute
or relative to MAP.json. This reads images only and never resizes them.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('card', type=Path)
    parser.add_argument('mapping', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error('Report already exists; choose a new path.')
    with Image.open(args.card) as image:
        if image.format != 'PNG':
            parser.error('The final card must be PNG.')
        image.load()
        card = image.convert('RGBA')
    modules = json.loads(args.mapping.read_text())
    if not isinstance(modules, list) or not modules:
        parser.error('Mapping must be a nonempty list.')
    results = []
    for module in modules:
        source = Path(module['source'])
        if not source.is_absolute():
            source = args.mapping.parent / source
        x, y, width, height = (module[k] for k in ('x', 'y', 'width', 'height'))
        if any(type(v) is not int for v in (x, y, width, height)):
            parser.error('All rectangle values must be integers.')
        if min(x, y) < 0 or min(width, height) <= 0 or x + width > card.width or y + height > card.height:
            parser.error('Rectangle is outside the card: ' + str(module['id']))
        with Image.open(source) as image:
            image.load()
            original = image.convert('RGBA')
        same_size = original.size == (width, height)
        # Compare each channel separately: RGBA getbbox alone can hide RGB
        # differences when both images have an identical alpha channel.
        equal = same_size and all(
            channel.getbbox() is None
            for channel in ImageChops.difference(
                original, card.crop((x, y, x + width, y + height))
            ).split()
        )
        results.append({'id': module['id'], 'source': str(source.resolve()),
                        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'native_size': list(original.size), 'size_identical': same_size,
                        'pixels_identical': equal})
    passed = all(r['pixels_identical'] for r in results)
    report = {'card': str(args.card.resolve()), 'size': list(card.size),
              'sha256': hashlib.sha256(args.card.read_bytes()).hexdigest(),
              'passed': passed, 'modules': results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('x') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(f"Native pixel match: {sum(r['pixels_identical'] for r in results)}/{len(results)}")
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
