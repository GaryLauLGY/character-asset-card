#!/usr/bin/env python3
"""Lay out 3 square head/neck/shoulder PNGs and 3 body PNGs without resampling.

Usage: compose_six_grid.py HEAD_FRONT HEAD_SIDE HEAD_BACK BODY_FRONT BODY_SIDE
BODY_BACK --output CARD.png --mapping MAP.json [--font FONT]
[--padding edge|neutral]
Use verify_native_pixels.py to verify the resulting map. Framing needs visual QA.
All six frames share a width; narrower sources get copied edge-background pixels.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def frame_native(image, width, height, mode):
    """Add canvas only; every pixel inside the source rectangle stays untouched."""
    left = (width - image.width) // 2
    right = width - image.width - left
    top = (height - image.height) // 2
    bottom = height - image.height - top
    frame = Image.new('RGBA', (width, height), '#f5f5f3')
    if mode == 'edge':
        # Inputs must have background-only edges. Copy strips at integer positions,
        # including transparent RGB values; never resize or alpha-composite them.
        for offset in range(left):
            frame.paste(image.crop((0, 0, 1, image.height)), (offset, top))
        for offset in range(right):
            frame.paste(image.crop((image.width - 1, 0, image.width, image.height)),
                        (left + image.width + offset, top))
        for offset in range(top):
            frame.paste(image.crop((0, 0, image.width, 1)), (left, offset))
        for offset in range(bottom):
            frame.paste(image.crop((0, image.height - 1, image.width, image.height)),
                        (left, top + image.height + offset))
        for box, corner in [
            ((0, 0, left, top), (0, 0)),
            ((left + image.width, 0, width, top), (image.width - 1, 0)),
            ((0, top + image.height, left, height), (0, image.height - 1)),
            ((left + image.width, top + image.height, width, height),
             (image.width - 1, image.height - 1)),
        ]:
            if box[0] < box[2] and box[1] < box[3]:
                frame.paste(image.getpixel(corner), box)
    frame.paste(image, (left, top))
    return frame, {'left': left, 'right': right, 'top': top, 'bottom': bottom,
                   'method': 'integer edge-background copy' if mode == 'edge' else 'neutral canvas'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs=6, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mapping', required=True, type=Path)
    parser.add_argument('--font', type=Path)
    parser.add_argument('--padding', choices=('edge', 'neutral'), default='edge',
                        help='Use neutral if source edges contain the subject.')
    args = parser.parse_args()
    if args.output.exists() or args.mapping.exists():
        parser.error('Choose new output and mapping paths; existing files are protected.')
    if args.output.resolve() == args.mapping.resolve():
        parser.error('Output and mapping must be different files.')
    images = []
    for index, path in enumerate(args.sources):
        with Image.open(path) as source:
            if source.format != 'PNG':
                parser.error(f'Source must be a PNG: {path}')
            source.load()
            if index < 3 and source.width != source.height:
                parser.error(f'Head/neck/shoulder images must be square: {path}')
            images.append(source.convert('RGBA'))
    candidates = [args.font] if args.font else [
        Path('/System/Library/Fonts/PingFang.ttc'),
        Path('/System/Library/Fonts/STHeiti Light.ttc'),
        Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
    ]
    font_path = next((p for p in candidates if p and p.is_file()), None)
    if font_path is None:
        parser.error('Provide a Chinese font using --font.')
    frame_width = max(im.width for im in images)
    margin, gap, label_height, row_gap = 32, 24, 52, 28
    head_height = frame_width
    body_height = max(im.height for im in images[3:])
    width = 2 * margin + 3 * frame_width + 2 * gap
    height = 2 * margin + 2 * label_height + head_height + row_gap + body_height
    card = Image.new('RGBA', (width, height), '#f5f5f3')
    draw = ImageDraw.Draw(card)
    label_font = ImageFont.truetype(str(font_path), 32)
    labels = ['正面头部', '侧面头部', '背面头部', '正面身体', '侧面身体', '背面身体']
    mapping = []
    for index, (source, im) in enumerate(zip(args.sources, images)):
        row, column = divmod(index, 3)
        column_x = margin + column * (frame_width + gap)
        label_y = margin if row == 0 else margin + label_height + head_height + row_gap
        frame_y = label_y + label_height
        frame_height = head_height if row == 0 else body_height
        frame, padding = frame_native(im, frame_width, frame_height, args.padding)
        x = column_x + padding['left']
        y = frame_y + padding['top']
        draw.text((column_x, label_y + 6), f'{index + 1:02d} {labels[index]}', fill='#333333', font=label_font)
        # No mask: preserve even transparent source pixels exactly.
        card.paste(frame, (column_x, frame_y))
        mapping.append({'id': f'{index + 1:02d}', 'source': str(source.resolve()),
                        'x': x, 'y': y, 'width': im.width, 'height': im.height,
                        'frame': {'x': column_x, 'y': frame_y, 'width': frame_width, 'height': frame_height},
                        'padding': padding})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.mapping.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as handle:
        card.save(handle, format='PNG')
    with args.mapping.open('x', encoding='utf-8') as handle:
        json.dump(mapping, handle, ensure_ascii=False, indent=2)
    print(f'Saved {width}x{height} card with 6 unscaled source regions: {args.output}')


if __name__ == '__main__':
    main()
