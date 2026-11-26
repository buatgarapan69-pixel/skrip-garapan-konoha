#!/usr/bin/env python3
"""LOAF Markets — daftar waitlist League of Loaf pakai email (GRATIS).

LOAF Markets = DEX self-custodial buat aset dunia nyata (RWA).
League of Loaf = kompetisi trading simulasi, hadiah USDC NYATA per ronde
(top 200 tiap ronde; Round 3 pool 3.000 USDC, juara 1 $750).
Tiap peserta dapat 100.000 mock USDC per ronde. TIDAK ADA token/airdrop.

Cara pakai:
    python3 loaf_waitlist.py
    -> masukkan email kamu saat ditanya.

Skrip ini cuma kirim email kamu ke endpoint waitlist resmi LOAF
(https://landing-backend-xi.vercel.app/api/subscribe) — sama seperti
isi form waitlist di https://www.loafmarkets.com/ .

Status 27 Nov 2026: beta.loafmarkets.com sedang UPGRADE, Round 3 sudah
berakhir 5 Nov 2026, Round 4 BELUM ada tanggal. Daftar waitlist dulu
supaya dapat kursi begitu ronde berikutnya dibuka.
"""
import json
import urllib.request
import urllib.error

ENDPOINT = "https://landing-backend-xi.vercel.app/api/subscribe"


def main():
    email = input("Email kamu: ").strip()
    if "@" not in email or "." not in email:
        print("Email tidak valid.")
        return
    payload = {
        "timestamp": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "email": email,
        "entryPoint": "hero_waitlist",
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.loafmarkets.com",
            "Referer": "https://www.loafmarkets.com/",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("HTTP", r.status, "->", r.read().decode()[:200])
            print("BERHASIL: kamu masuk waitlist LOAF. Pantau email + "
                  "@loafmarkets buat pengumuman Round 4.")
    except urllib.error.HTTPError as e:
        print("GAGAL HTTP", e.code, "->", e.read().decode()[:300])
    except Exception as e:
        print("GAGAL:", e)


if __name__ == "__main__":
    main()
