"""Делает картинки для новой работы в портфолио.

Нужны два скриншота сайта (лучше с масштабом 2x):
  desktop.png — окно 1440×900,
  phone.png   — экран 390×844.

Запуск:
  python3 tools/make_cover.py <id> "<цвет фона>" desktop.png phone.png

Например:
  python3 tools/make_cover.py vishnya "#EFE5DF" vishnya-d.png vishnya-m.png

Скрипт положит в папку img:
  img/<id>.webp        — обложку 1600×1000: сайт на компьютере и телефон поверх;
  img/<id>-phone.webp  — экран телефона 560×1212 для веера на первом экране.

Нужна библиотека Pillow: pip install pillow
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, '..', 'img')


def rounded(im, r):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def shadow(size, r, blur, alpha):
    w, h = size
    pad = blur * 3
    sh = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=(20, 10, 15, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def phone_frame(shot, width):
    bez = max(8, width // 30)
    scr_w = width - bez * 2
    scr = shot.resize((scr_w, int(shot.height * scr_w / shot.width)), Image.LANCZOS)
    scr = scr.crop((0, 0, scr_w, min(int(scr_w * 844 / 390), scr.height))).convert('RGB')
    body = Image.new('RGBA', (width, scr.height + bez * 2), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle([0, 0, body.width - 1, body.height - 1], int(width * 0.14), fill=(22, 20, 22, 255))
    face = rounded(scr, int(width * 0.11))
    body.paste(face, (bez, bez), face)
    return body


def cover(desktop, phone, bg, W=1600, H=1000):
    canvas = Image.new('RGBA', (W, H), bg)
    dw = int(W * 0.78)
    dh = int(dw * 900 / 1440)
    desk = desktop.resize((dw, int(desktop.height * dw / desktop.width)), Image.LANCZOS).crop((0, 0, dw, dh))
    bar = 34
    win = Image.new('RGB', (dw, dh + bar), (250, 249, 247))
    dr = ImageDraw.Draw(win)
    for i, c in enumerate([(236, 106, 94), (244, 190, 79), (98, 197, 84)]):
        dr.ellipse([18 + i * 22, 12, 30 + i * 22, 24], fill=c)
    win.paste(desk, (0, bar))
    win = rounded(win, 18)
    dx, dy = int(W * 0.06), int(H * 0.09)
    sh, pad = shadow(win.size, 18, 28, 70)
    canvas.alpha_composite(sh, (dx - pad, dy - pad + 18))
    canvas.alpha_composite(win, (dx, dy))
    ph = phone_frame(phone, int(W * 0.22))
    px, py = W - ph.width - int(W * 0.05), H - ph.height + int(H * 0.06)
    sh2, pad2 = shadow(ph.size, int(ph.width * 0.14), 30, 90)
    canvas.alpha_composite(sh2, (px - pad2, py - pad2 + 22))
    canvas.alpha_composite(ph, (px, py))
    return canvas.convert('RGB')


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    key, bg, dpath, mpath = sys.argv[1:]
    desktop = Image.open(dpath).convert('RGB')
    phone = Image.open(mpath).convert('RGB')
    os.makedirs(IMG, exist_ok=True)
    cover(desktop, phone, bg).save(os.path.join(IMG, key + '.webp'), 'WEBP', quality=80, method=6)
    w = 560
    card = phone.resize((w, int(phone.height * w / phone.width)), Image.LANCZOS).crop((0, 0, w, int(w * 844 / 390)))
    card.save(os.path.join(IMG, key + '-phone.webp'), 'WEBP', quality=78, method=6)
    print('Готово: img/%s.webp и img/%s-phone.webp' % (key, key))


if __name__ == '__main__':
    main()
