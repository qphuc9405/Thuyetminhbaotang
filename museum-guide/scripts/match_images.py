#!/usr/bin/env python3
"""So khớp ảnh bằng SIFT + RANSAC homography: (a) ảnh trong ZIP với nhau (b) ảnh ZIP với hình trong sách.
Kết quả: data/processed/image_matches.json (số inlier). Không xoá/gộp ảnh nào, chỉ ghi quan hệ."""
import cv2, glob, os, json, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
fs = sorted(glob.glob(str(ROOT / 'data/raw/archive2/*.jpg')))
figs = [f for f in sorted(glob.glob(str(ROOT / 'data/images/book/FIG_*.png')))]
sift = cv2.SIFT_create(nfeatures=1500)
def feat(p):
    im = cv2.imread(p, 0); h, w = im.shape; s = 800 / max(h, w)
    return sift.detectAndCompute(cv2.resize(im, None, fx=s, fy=s), None)
F = {p: feat(p) for p in fs + figs}
bf = cv2.BFMatcher(cv2.NORM_L2)
def inl(a, b):
    ka, da = F[a]; kb, db = F[b]
    if da is None or db is None or len(ka) < 8 or len(kb) < 8: return 0
    m = bf.knnMatch(da, db, k=2)
    good = [x[0] for x in m if len(x) == 2 and x[0].distance < 0.75 * x[1].distance]
    if len(good) < 8: return 0
    A = np.float32([ka[g.queryIdx].pt for g in good]); B = np.float32([kb[g.trainIdx].pt for g in good])
    H, mask = cv2.findHomography(A, B, cv2.RANSAC, 6.0)
    return int(mask.sum()) if mask is not None else 0
out = {'archive_pairs': [], 'archive_vs_book': []}
for i in range(len(fs)):
    for j in range(i + 1, len(fs)):
        n = inl(fs[i], fs[j])
        if n >= 25: out['archive_pairs'].append([os.path.basename(fs[i]), os.path.basename(fs[j]), n])
for a in fs:
    for b in figs:
        n = inl(a, b)
        if n >= 20: out['archive_vs_book'].append([os.path.basename(a), os.path.basename(b), n])
(ROOT / 'data/processed/image_matches.json').write_text(json.dumps(out, indent=1))
idx = {os.path.basename(f): k + 1 for k, f in enumerate(fs)}
for a, b, n in out['archive_pairs']: print(f'IMG{idx[a]:03d}-IMG{idx[b]:03d}: {n}')
for a, b, n in out['archive_vs_book']: print(f'IMG{idx[a]:03d} ~ {b[:12]}: {n}')
