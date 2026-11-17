#!/usr/bin/env python3
"""Locate candidate slide regions via dark outlines or a sampled fill color."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--width-in', type=float, default=7.5)
    p.add_argument('--height-in', type=float, default=10.0)
    p.add_argument('--threshold', type=int, default=145, help='Dark-outline grayscale threshold')
    p.add_argument('--sample', help='Sample a fill color at X,Y instead of detecting dark outlines')
    p.add_argument('--distance', type=float, default=20, help='RGB Euclidean distance from sampled color')
    p.add_argument('--min-width', type=int, default=100)
    p.add_argument('--min-height', type=int, default=30)
    p.add_argument('--max-results', type=int, default=80)
    args = p.parse_args()
    if args.width_in <= 0 or args.height_in <= 0:
        raise ValueError('Page dimensions must be positive')
    img = cv2.imread(str(args.image))
    if img is None:
        raise FileNotFoundError(args.image)
    height, width = img.shape[:2]
    sampled = None
    if args.sample:
        sx, sy = map(int, args.sample.split(','))
        if sx < 0 or sy < 0 or sx >= width or sy >= height:
            raise ValueError('Sample point outside image')
        sampled = img[sy, sx].astype(np.float32)
        mask = (np.linalg.norm(img.astype(np.float32) - sampled, axis=2) <= args.distance).astype(np.uint8)
        _, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        candidates = [tuple(map(int, row[:4])) for row in stats[1:]]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = (gray < args.threshold).astype(np.uint8) * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        candidates = [cv2.boundingRect(c) for c in contours]
    candidates.sort(key=lambda b: (b[1], b[0], -b[2] * b[3]))
    unique = []
    for x, y, w, h in candidates:
        if w < args.min_width or h < args.min_height:
            continue
        if any(abs(x-a)<8 and abs(y-b)<8 and abs(w-c)<16 and abs(h-d)<16 for a,b,c,d in unique):
            continue
        unique.append((x, y, w, h))
    scale = min(args.width_in / width, args.height_in / height)
    pad_x = (args.width_in - width * scale) / 2
    pad_y = (args.height_in - height * scale) / 2
    regions = [{'box_px': [x,y,w,h], 'box_inches': [round(pad_x+x*scale, 4), round(pad_y+y*scale, 4), round(w*scale, 4), round(h*scale, 4)]} for x,y,w,h in unique[:args.max_results]]
    print(json.dumps({'image_px': [width,height], 'sample_rgb': list(map(int, sampled[::-1])) if sampled is not None else None, 'regions': regions, 'note': 'Candidate bounding boxes; visually inspect text-safe space, icons, and irregular borders.'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
