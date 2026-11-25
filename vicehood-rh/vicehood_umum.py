#!/usr/bin/env python3
"""VICEHOOD RH — Daftar Waitlist (versi untuk umum).

GRATIS, tanpa deposit, tanpa connect wallet.
Cara pakai:
  1. Install requests:  pip install requests
  2. Isi X_NAME dengan nama X kamu (tanpa @, maks 15 karakter,
     huruf/angka/underscore) dan EVM_ADDRESS dengan alamat EVM
     kamu (0x + 40 karakter hex).
  3. Jalankan:  python3 vicehood_umum.py
  4. Selesaikan juga 3 tugas X di https://www.vicehood.xyz/
     (Follow @vicehood_rh, RT & Like postingan pin, Quote).
     Situs menandai tugas selesai saat kartunya diketuk.

Skrip ini mendaftar 1 akun (akun kamu sendiri) ke Early List
ViceHood RH. Server mengembalikan nomor posisi antrian kamu.
Supply: 3.333 slot. Tidak ada link referral di waitlist ini —
daftar langsung di situsnya.

Dibagikan gratis oleh Tim Konoha — silakan dipakai & dibagikan.
"""
import json
import sys

import requests

# ======= ISI BAGIAN INI =======
X_NAME = "NAMAXKAMU"          # contoh: chengjigarap (tanpa @, maks 15 karakter)
EVM_ADDRESS = "0x0000000000000000000000000000000000000000"  # alamat EVM kamu
# ==============================

BASE = "https://www.vicehood.xyz/api"


def main():
    if X_NAME in ("NAMAXKAMU", "") or EVM_ADDRESS.startswith("0x0000"):
        print("Isi dulu X_NAME dan EVM_ADDRESS di bagian atas skrip.")
        sys.exit(1)
    if not (1 <= len(X_NAME) <= 15 and X_NAME.replace("_", "").isalnum()):
        print("X_NAME tidak valid (huruf/angka/underscore, maks 15 karakter).")
        sys.exit(1)
    if not (len(EVM_ADDRESS) == 42 and EVM_ADDRESS.startswith("0x")):
        print("EVM_ADDRESS tidak valid (0x + 40 karakter hex).")
        sys.exit(1)

    r = requests.post(
        BASE + "/join",
        json={"x_name": X_NAME, "evm_address": EVM_ADDRESS,
              "follow_done": True, "rt_done": True, "quote_done": True},
        headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/131.0.0.0 Mobile Safari/537.36",
                 "Origin": "https://www.vicehood.xyz",
                 "Referer": "https://www.vicehood.xyz/",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
        timeout=30)
    if r.status_code != 200:
        print("Gagal:", r.status_code, r.text[:200])
        sys.exit(1)
    d = r.json()
    print("Berhasil! @%s masuk Early List di posisi #%s" % (d["x_name"], d["position"]))
    print("EVM:", d["evm_masked"])

    # Verifikasi independen
    lk = requests.get(BASE + "/lookup", params={"q": X_NAME}, timeout=20).json()
    print("Verifikasi lookup:", "ADA di list, posisi #%s" % lk["position"] if lk.get("found") else "BELUM ketemu — coba lagi sebentar lagi")


if __name__ == "__main__":
    main()
