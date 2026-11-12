"""Làm sạch ảnh phòng 4 chủ đề: cắt thanh đáy, xoá nút/toolbar/nhân vật/ghim vẽ sẵn,
thay chữ bảng Chủ đề 4 (1975 → 1972) và chú thích ảnh 30.4.1975. Dùng: python3 clean_room.py <vào> <ra_dir>"""
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
src, out = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('room_src.png', '.')
H = 725
im = cv2.imread(src)[:H].copy()
m = np.zeros(im.shape[:2], np.uint8)
def rect(x0, y0, x1, y1): cv2.rectangle(m, (x0, y0), (x1, y1), 255, -1)
rect(0, 0, 478, 58); rect(1402, 0, 1668, 62)                      # nút Về bản đồ + tiêu đề; thanh công cụ
cv2.fillPoly(m, [np.array([(0, 540), (175, 540), (210, 640), (300, 660), (300, 715), (230, 725), (0, 725)])], 255)  # nhân vật
for (x, y) in [(240, 425), (583, 383), (1148, 380), (1562, 446), (513, 590), (849, 585), (1450, 530)]:  # ghim vẽ sẵn
    cv2.circle(m, (x, y), 19, 255, -1)
# chữ trên bảng 4 + dải phụ đề + chú thích ảnh "(30.4.1975)"
region = np.zeros_like(m); cv2.fillPoly(region, [np.array([(1336, 148), (1659, 66), (1661, 228), (1338, 258)])], 255)
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
light = ((hsv[..., 2] > 140) & (hsv[..., 1] < 110)).astype(np.uint8) * 255
txt = cv2.dilate(cv2.bitwise_and(light, region), np.ones((5, 5), np.uint8))
m = cv2.bitwise_or(m, txt)
rect(1503, 252, 1652, 296)
im = cv2.inpaint(im, m, 7, cv2.INPAINT_TELEA)
blur = cv2.GaussianBlur(im, (0, 0), 2.0); mm = cv2.GaussianBlur(m, (0, 0), 2.5)[..., None] / 255.0
im = (im * (1 - mm * .5) + blur * (mm * .5)).astype(np.uint8)
cv2.imwrite(f'{out}/mask.png', m)

# ---- chữ mới trên bảng 4 (nắn phối cảnh theo góc bảng)
pil = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')
def coeffs(dst, src_):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src_):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()
def warp_text(lines, quad, size, cw, ch, fill, font_path, gap=1.18, stroke=0):
    layer = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(font_path, size)
    hs = [f.getbbox(l)[3] - f.getbbox(l)[1] for l in lines]; tot = sum(hs) + (len(lines) - 1) * size * (gap - 1)
    y = (ch - tot) / 2
    for l, hh in zip(lines, hs):
        wl = d.textlength(l, font=f); d.text(((cw - wl) / 2, y - f.getbbox(l)[1]), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=(10, 30, 32, 160)); y += hh + size * (gap - 1)
    W, Hh = pil.size
    c = coeffs(quad, [(0, 0), (cw, 0), (cw, ch), (0, ch)])
    return layer.transform((W, Hh), Image.PERSPECTIVE, c, Image.BICUBIC)
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
main_q = [(1352, 150), (1645, 80), (1647, 178), (1352, 219)]
band_q = [(1360, 212), (1628, 192), (1630, 222), (1362, 246)]
pil.alpha_composite(warp_text(['Vĩ tuyến 17 sau giải phóng', 'Quảng Trị (1972)'], main_q, 45, 760, 200, (246, 233, 200, 255), SERIF, stroke=1))
pil.alpha_composite(warp_text(['Đôi bờ sum họp, gỡ bom mìn, hồi sinh quê hương'], band_q, 25, 800, 60, (238, 228, 205, 255), SANS))
pil.convert('RGB').save(f'{out}/room_clean.png')
pil.convert('RGB').save(f'{out}/museum-room.webp', quality=88)
print('ok', pil.size)

# ---- sửa chú thích bảng loa: "Tiếng nói của miền Nam…" dễ gây hiểu nhầm (loa 500W là của bờ Bắc)
_out_png = f"{out}/room_clean.png"
from PIL import Image as _I, ImageDraw as _D, ImageFont as _F
import numpy as _np
_im = _I.open(_out_png).convert("RGB")
_a = _np.array(_im)
_box = (1364, 641, 1516, 672)
_reg = _a[_box[1]:_box[3], _box[0]:_box[2]].reshape(-1, 3).astype(float)
_lum = _reg.sum(1)
_bg = _reg[_lum <= _np.percentile(_lum, 40)].mean(0)
_yy, _xx = _np.mgrid[_box[1]:_box[3], _box[0]:_box[2]]
_e = _np.minimum.reduce([_xx - _box[0], _box[2] - 1 - _xx, _yy - _box[1], _box[3] - 1 - _yy]).astype(float)
_al = _np.clip(_e / 3.0, 0, 1)[..., None]
_a[_box[1]:_box[3], _box[0]:_box[2]] = (_a[_box[1]:_box[3], _box[0]:_box[2]] * (1 - _al) + _bg * _al).astype(_np.uint8)
_im = _I.fromarray(_a)
_d = _D.Draw(_im)
_f = _F.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 12)
for _i, _s in enumerate(["Cuộc “đấu loa” giữa", "hai bờ giới tuyến."]):
    _w = _d.textlength(_s, font=_f)
    _d.text(((1330 + 1527 + 26) / 2 - _w / 2 - 6, 643 + _i * 14), _s, font=_f, fill=(236, 228, 210))
_im.save(_out_png)
_im.save(_out_png.rsplit("/", 1)[0] + "/museum-room.webp", quality=88)
print("plaque ok")
