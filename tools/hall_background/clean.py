"""Làm sạch ảnh mẫu nhà trưng bày: cắt bỏ thanh giao diện vẽ sẵn ở đáy, xoá (inpaint) nhãn, ghim, biển chữ,
logo, thanh công cụ, bong bóng thoại và cô hướng dẫn vẽ sẵn – để giao diện tự đặt ghim/nhãn/nhân vật bằng code (đổi được ngôn ngữ).
Vùng bị xoá sẽ hơi nhoè; nhân vật hướng dẫn và nhãn thật được đặt chồng lên đúng các vùng đó."""
import cv2, numpy as np
import sys
# Cách dùng: python3 clean.py <ảnh-mẫu-1672x941.png> <thư-mục-ra>
src, out_dir = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('hall_src.png', '.')
im = cv2.imread(src)
H = 736
im = im[:H]
m = np.zeros(im.shape[:2], np.uint8)
def box(x0,y0,x1,y1,pad=4):
    cv2.rectangle(m,(x0-pad,y0-pad),(x1+pad,y1+pad),255,-1)
# UI chrome
box(0,0,455,80); box(1270,4,1656,64)
# pills + pins
for b in [(306,180,470,230),(1044,198,1236,248),(1256,200,1414,248),(1448,186,1664,236),(524,408,684,455)]: box(*b)
# plaques
for b in [(226,598,344,652),(331,520,424,570),(766,642,1032,686),(1248,448,1350,502),(1396,566,1487,607),(1496,616,1602,667)]: box(*b)
# rotated plaque: polygon
cv2.fillPoly(m,[np.array([(424,640),(560,654),(563,706),(420,693)])],255)
# speech bubble + guide girl
cv2.rectangle(m,(126,294),(322,446),255,-1)
cv2.fillPoly(m,[np.array([(0,280),(150,282),(170,330),(265,450),(262,500),(200,520),(170,736),(0,736)])],255)
cv2.imwrite(f'{out_dir}/mask.png', m)
out = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
# soften inpainted regions slightly
blur = cv2.GaussianBlur(out,(0,0),2.2)
mm = cv2.GaussianBlur(m,(0,0),3)[...,None]/255.0
out = (out*(1-mm*0.5)+blur*(mm*0.5)).astype(np.uint8)
cv2.imwrite(f'{out_dir}/hall_clean.png', out)
cv2.imwrite(f'{out_dir}/museum-hall.webp', out, [cv2.IMWRITE_WEBP_QUALITY, 88])
