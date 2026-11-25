#!/usr/bin/env python3
"""
GLOBE MARKET — Daftar Waitlist Early Access (versi publik, buat orang lain).
Globe = aplikasi social trading pertama di LayerZero ATLAS
(spot, perps, saham). ATLAS live 30 Nov 2026 — yang masuk list sebelum
itu jadi "Founding trader". Pendaftaran GRATIS, cuma butuh email.

CARA PAKAI (Termux / PC, Python 3):
  1. Isi EMAIL di bawah dengan email kamu.
  2. (Opsional) isi REF dengan kode referral teman — kalau tidak ada,
     kosongkan saja, kamu tetap dapat kode referral sendiri.
  3. (Opsional) isi PROXY kalau kamu pakai proxy HTTP, contoh:
     PROXY = "http://user:pass@gate.contoh.com:8080"
     Kalau tidak pakai proxy, biarkan "".
  4. Jalankan:  python3 globe_signup_public.py
  5. Kalau sukses, skrip menampilkan nomor antrean + kode referral
     kamu. Link referral kamu: https://globemarkets.xyz/?ref=KODEMU

TANPA top-up, TANPA deposit, TANPA hubungkan wallet. Kalau situs
meminta deposit/wallet berisi dana, BERHENTI — itu bukan jalur gratis.
Dibagikan gratis oleh Tim Konoha — semoga hoki!
"""
import hashlib
import json
import random
import urllib.request
import uuid

# ── ISI DI SINI ────────────────────────────────────────────────
EMAIL = "emailkamu@contoh.com"   # <-- GANTI dengan email kamu
REF = ""                          # <-- kode referral teman (opsional)
PROXY = ""                        # <-- proxy HTTP (opsional)
# ───────────────────────────────────────────────────────────────

DEVICES = ["Pixel 7", "Pixel 8 Pro", "Samsung Galaxy S23", "Xiaomi 13",
           "OnePlus 11", "Redmi Note 13", "Oppo Reno 10", "Vivo V29"]

URL = "https://globemarkets.xyz/api/waitlist"


def fake_ua(seed):
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    dev = DEVICES[h % len(DEVICES)]
    chrome = 118 + (h // len(DEVICES)) % 14
    return ("Mozilla/5.0 (Linux; Android 13; %s) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/%d.0.0.0 Mobile Safari/537.36"
            % (dev, chrome))


def main():
    if "@" not in EMAIL or EMAIL.startswith("emailkamu@"):
        print("Isi dulu EMAIL kamu di dalam skrip (baris EMAIL = ...).")
        return
    body = json.dumps({
        "email": EMAIL.strip().lower(),
        "source": "access",
        "website": "",
        "ref": REF.strip(),
        "landing": "/",
        "referrer": "",
        "utm_source": "", "utm_medium": "", "utm_campaign": "",
        "utm_content": "",
    }).encode()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": fake_ua(EMAIL),
        "Referer": "https://globemarkets.xyz/" + ("?ref=" + REF.strip() if REF.strip() else ""),
        "Origin": "https://globemarkets.xyz",
        "X-Device-Id": str(uuid.uuid4()),
    }
    if PROXY:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    else:
        opener = urllib.request.build_opener()
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    with opener.open(req, timeout=30) as r:
        data = json.load(r)
    if data.get("ok"):
        print("BERHASIL! Kamu nomor #%s dari %s pendaftar."
              % (data.get("position"), data.get("total")))
        print("Poin: %s | Level: %s" % (data.get("points"), data.get("level")))
        print("Kode referral kamu: %s" % data.get("code"))
        print("Link referral kamu: https://globemarkets.xyz/?ref=%s"
              % data.get("code"))
        print("Jangan lupa: follow X @globemkts + join t.me/globemkts")
    else:
        print("Gagal:", data)


if __name__ == "__main__":
    main()
