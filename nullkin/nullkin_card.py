#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NULLKIN — buat signal card (1200x675) untuk postingan X.

Meniru render kartu di nullkin.xyz: nomor signal = hash FNV-1a dari
(wallet lowercase + handle lowercase) mod 10000, nol di depan 4 digit.
Portrait diambil langsung dari halaman nullkin.xyz (data-URI di HTML).

  pip install pillow
  python3 nullkin_card.py --handle usernamekamu --wallet 0xALAMAT_EVM_KAMU
  -> nullkin-signal-XXXX.png (siap di-posting ke X)

Isi handle + wallet KAMU sendiri. Wallet di kartu hanya tampil
6 karakter awal + 4 akhir (0x1234...abcd) — itu alamat publik.
"""
import argparse
import base64
import io
import math
import re
import sys
import urllib.request

SITE = "https://nullkin.xyz"


def fnv1a(s):
    x = 2166136261
    for ch in s:
        x ^= ord(ch)
        x = (x * 16777619) & 0xFFFFFFFF
    return x


def signal_no(wallet, handle):
    return str(fnv1a(wallet.lower() + handle.lower()) % 10000).zfill(4)


def fetch_portrait():
    """Ambil artwork 400x400 dari HTML nullkin.xyz (data-URI terbesar)."""
    with urllib.request.urlopen(SITE, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    imgs = re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)", html)
    if not imgs:
        sys.exit("ERROR: tidak menemukan gambar di nullkin.xyz")
    raw = base64.b64decode(max(imgs, key=len))
    from PIL import Image
    return Image.open(io.BytesIO(raw)).convert("RGB")


def main():
    ap = argparse.ArgumentParser(description="Buat signal card NULLKIN")
    ap.add_argument("--handle", required=True, help="username X kamu (tanpa @ juga boleh)")
    ap.add_argument("--wallet", required=True, help="alamat EVM 0x (publik saja)")
    ap.add_argument("--out", default="", help="nama file PNG (default: nullkin-signal-XXXX.png)")
    a = ap.parse_args()
    handle = re.sub(r"^@", "", a.handle.strip())
    if not re.match(r"^[A-Za-z0-9_]{1,15}$", handle):
        sys.exit("ERROR: username X tidak valid.")
    wallet = a.wallet.strip()
    if not re.match(r"^0x[0-9a-fA-F]{40}$", wallet):
        sys.exit("ERROR: alamat wallet tidak valid.")
    no = signal_no(wallet, handle)

    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), "#050505")
    g = ImageDraw.Draw(img, "RGBA")

    def F(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    for x in range(0, W, 25):
        g.line([(x, 0), (x, H)], fill=(255, 255, 255, 9))
    for y in range(0, H, 25):
        g.line([(0, y), (W, y)], fill=(255, 255, 255, 9))
    P = 56
    S = H - P * 2
    portrait = fetch_portrait().resize((S, S), Image.NEAREST)
    img.paste(portrait, (P, P))
    g.rectangle([P, P, P + S - 1, P + S - 1], outline=(51, 51, 51), width=1)
    for (x, y, dx, dy) in [(P - 8, P - 8, 1, 1), (P + S + 8, P - 8, -1, 1),
                           (P - 8, P + S + 8, 1, -1), (P + S + 8, P + S + 8, -1, -1)]:
        g.line([(x, y + 26 * dy), (x, y), (x + 26 * dx, y)], fill=(127, 227, 194), width=3)
    X = P + S + 64
    R = W - P
    g.text((X + 52, 80), "NULLKIN", font=F(SANSB, 34), fill="#f2f2f2", anchor="lm")
    g.text((X, 146), "WHITELIST REGISTRATION", font=F(MONO, 15), fill="#7fe3c2", anchor="lm")
    g.text((X, 214), "APPLICANT", font=F(MONO, 15), fill="#8a8a8a", anchor="lm")
    size = 96
    while F(SANSB, size).getlength("@" + handle) > R - X and size > 40:
        size -= 4
    g.text((X, 272), "@" + handle, font=F(SANSB, size), fill="#fafafa", anchor="lm")
    g.text((X, 350), "SIGNAL Nº", font=F(MONO, 15), fill="#8a8a8a", anchor="lm")
    g.text((X + 200, 350), "WALLET", font=F(MONO, 15), fill="#8a8a8a", anchor="lm")
    g.text((X, 388), no, font=F(SANSB, 30), fill="#f2f2f2", anchor="lm")
    g.text((X + 200, 388), wallet[:6] + "…" + wallet[-4:], font=F(SANSB, 30),
           fill="#f2f2f2", anchor="lm")
    seed = fnv1a(wallet.lower() + handle.lower())
    pts, r = [], seed or 7
    for x in range(0, R - X + 1, 4):
        r = (r * 1103515245 + 12345) & 0xFFFFFFFF
        y = 478 + math.sin(x * .045 + seed % 7) * 16 + math.sin(x * .13) * 6 \
            + ((r >> 24) / 255 - .5) * 16
        pts.append((X + x, y))
    g.line(pts, fill="#7fe3c2", width=2)
    g.line([(X, 548), (R, 548)], fill=(38, 38, 38), width=1)
    g.text((X, 584), "KEEP THE SIGNAL ALIVE.", font=F(MONO, 14), fill="#9a9a9a", anchor="lm")
    g.text((R, 584), "PLANNED FOR ZERO", font=F(MONO, 14), fill="#9a9a9a", anchor="rm")
    for y in range(0, H, 3):
        g.rectangle([0, y, W, y], fill=(0, 0, 0, 46))
    out = a.out or ("nullkin-signal-%s.png" % no)
    img.save(out)
    print("Kartu tersimpan:", out, "| Signal Nº:", no)


if __name__ == "__main__":
    main()
