"""Biến ảnh mockup trang Hiệp định thành ảnh cảnh nền (bỏ giao diện vẽ sẵn: thanh trên, danh sách trái, panel phải, thanh chủ đề)."""
import sys
import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
H, W = im.shape[:2]
m = np.zeros((H, W), np.uint8)
# thanh thương hiệu + breadcrumb, thanh công cụ
cv2.rectangle(m, (30, 0), (680, 82), 255, -1)
cv2.rectangle(m, (1250, 0), (1660, 62), 255, -1)
# danh sách trái
cv2.rectangle(m, (12, 120), (225, 352), 255, -1)
# thanh chủ đề dưới
cv2.rectangle(m, (95, 832), (1575, 935), 255, -1)
cv2.rectangle(m, (1170, 160), (1672, 770), 255, -1)
f = 4
lo = cv2.resize(im, (W // f, H // f), interpolation=cv2.INTER_AREA)
lom = cv2.dilate(cv2.resize(m, (W // f, H // f), interpolation=cv2.INTER_NEAREST), np.ones((3, 3), np.uint8))
for r in (25, 12):
    lo = cv2.inpaint(lo, lom, r, cv2.INPAINT_NS)
up = cv2.resize(lo, (W, H), interpolation=cv2.INTER_CUBIC)
up = cv2.GaussianBlur(up, (0, 0), 9)
alpha = cv2.GaussianBlur(cv2.dilate(m, np.ones((15, 15), np.uint8)).astype(np.float32) / 255, (0, 0), 10)[..., None]
res = (im * (1 - alpha) + up * alpha).astype(np.uint8)
# bóng tối nhẹ ở mép phải để panel HTML nổi trên nền
grad = np.clip((np.arange(W) - W * 0.62) / (W * 0.38), 0, 1)[None, :, None]
res = (res * (1 - 0.35 * grad)).astype(np.uint8)
cv2.imwrite(out, res)
cv2.imwrite(out.rsplit(".", 1)[0] + ".webp", res, [cv2.IMWRITE_WEBP_QUALITY, 86])
print("ok", res.shape)
