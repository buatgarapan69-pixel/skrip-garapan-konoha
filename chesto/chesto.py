#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHESTO AI — daftar + check-in harian (versi bersih buat orang lain).
GRATIS, tanpa deposit, tanpa wallet berisi dana.

CARA PAKAI (1 perintah, pilih menu di dalam):
  python3 chesto.py

Menu:
  [1] Daftar akun baru (email temp otomatis + verifikasi otomatis)
  [2] Check-in harian + klaim welcome bonus (perlu email + password akunmu)
  [3] Cek saldo USDC / Karma / link referral (perlu login)
  [4] Lihat tugas USDC aktif (tanpa login)
  [5] Keluar

YANG HARUS DIISI:
  - REF_CODE di bawah ini dengan kode referral KAMU (opsional — kosongkan
    kalau mau daftar tanpa referral). Kode referral orang lain TIDAK boleh
    diisi di sini kalau kamu mau dapat komisi sendiri.
  - Kalau daftar manual, pakai email ASLI kamu supaya bisa reset password.

SYARAT JUJUR (hasil probe 27 Nov 2026):
  - Tugas USDC (0.1 USDC/tugas) HANYA bisa dikerjakan kalau akun X kamu
    umur 100+ hari, 40+ followers, 20+ tweet, 30+ following.
    Akun X baru TIDAK bisa mengerjakan tugas USDC.
  - Min WD 0.01 USDC, fee 0, dibayar USDC di jaringan Base (FluxaPay).
  - Karma (bonus daftar +20, check-in +3/hari) BUKAN USDC dan TIDAK bisa
    ditukar jadi USDC — Karma dipakai buat fee submit tugas (5 Karma).
  - Komisi referral 33% dari fee platform — hanya jalan kalau referralmu
    menyelesaikan tugas USDC yang didanai customer.
  - Chesto membatasi 2 akun baru per jaringan/hari — jangan daftar
    banyak akun dari 1 IP yang sama dalam sehari.

Dibuat: 27 Nov 2026. Bukan skrip resmi Chesto. Pakai dengan risiko sendiri.
"""
import json
import random
import re
import string
import sys
import time
import uuid

import requests

BASE = "https://chesto.ai"
API = BASE + "/api"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# === ISI KODE REFERRAL KAMU DI SINI (contoh: "u_abcdefghij"). Kosong = tanpa ref.
REF_CODE = ""

# Email temp (mail.tm) — hanya untuk akun percobaan. Untuk akun utama,
# daftar manual di https://chesto.ai/register pakai email asli kamu.
MAILTM_DOMAIN = "euploading.com"


def chesto(method, path, token=None, **kw):
    h = {"User-Agent": UA, "Accept": "application/json",
         "Content-Type": "application/json", "Origin": BASE,
         "Referer": BASE + "/register"}
    if token:
        h["Authorization"] = "Bearer " + token
    r = requests.request(method, API + path, headers=h, timeout=30, **kw)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"_raw": r.text[:300]}


def mailtm_create():
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"kx{rnd}@{MAILTM_DOMAIN}"
    pw = "Mt" + uuid.uuid4().hex[:10] + "9!"
    r = requests.post("https://api.mail.tm/accounts",
                      json={"address": email, "password": pw}, timeout=20)
    if r.status_code != 201:
        print("mail.tm gagal:", r.status_code, r.text[:200])
        return None, None
    r = requests.post("https://api.mail.tm/token",
                      json={"address": email, "password": pw}, timeout=20)
    return email, r.json().get("token")


def mailtm_read_verify(mtoken, tries=24, wait=5):
    """Baca email verifikasi Chesto dari inbox mail.tm, kembalikan token."""
    for i in range(tries):
        time.sleep(wait)
        try:
            rr = requests.get("https://api.mail.tm/messages",
                              headers={"Authorization": "Bearer " + mtoken},
                              timeout=20)
            msgs = rr.json().get("hydra:member", [])
        except Exception as e:
            print("poll err:", e)
            continue
        if msgs:
            d = requests.get("https://api.mail.tm/messages/" + msgs[0]["id"],
                             headers={"Authorization": "Bearer " + mtoken},
                             timeout=20).json()
            txt = re.sub(r"<[^>]+>", " ",
                         str(d.get("text") or "") + " " + str(d.get("html") or ""))
            m = re.search(r"/verify\?token=([^\s\"'<>]+)", txt)
            if m:
                return m.group(1)
            print("email masuk tapi token tidak ketemu:", d.get("subject"))
            return None
        print(f"menunggu email verifikasi... ({i + 1}/{tries})")
    return None


def daftar_baru():
    print("\n== DAFTAR AKUN BARU (email temp otomatis) ==")
    email, mtoken = mailtm_create()
    if not email:
        return
    pw = "Ch" + uuid.uuid4().hex[:10] + "9!"
    print("email:", email)
    body = {"email": email, "password": pw}
    if REF_CODE:
        body["referralCode"] = REF_CODE
    st, j = chesto("POST", "/auth/register", json=body)
    print("register:", st, json.dumps(j, ensure_ascii=False)[:300])
    if st not in (200, 201):
        print("GAGAL daftar (mungkin limit 2 akun/jaringan/hari). Coba besok / ganti jaringan.")
        return
    print("menunggu email verifikasi...")
    token = mailtm_read_verify(mtoken)
    if not token:
        print("Email verifikasi tidak datang. Coba kirim ulang dari web.")
        print("SIMPAN: email =", email, "| password =", pw)
        return
    st, j = chesto("GET", f"/auth/verify/{token}/preview")
    print("verify preview:", st, json.dumps(j)[:200])
    st, j = chesto("POST", f"/auth/verify/{token}/complete", json={"password": pw})
    print("verify complete:", st, json.dumps(j, ensure_ascii=False)[:300])
    if st != 200:
        print("Verifikasi gagal — token sekali pakai, kirim ulang verifikasi dari web.")
        print("SIMPAN: email =", email, "| password =", pw)
        return
    st, j = chesto("POST", "/auth/login", json={"email": email, "password": pw})
    print("login:", st)
    if st == 200:
        print("BERHASIL! uid/ref:", j.get("uid"), "| ref link:",
              f"{BASE}/register?ref={j.get('referralCode')}")
        print("Karma awal:", j.get("karma"), "| saldo USDC:", j.get("balance"))
    print("SIMPAN BAIK-BAIK: email =", email, "| password =", pw)


def login_interaktif():
    email = input("Email Chesto: ").strip()
    pw = input("Password: ").strip()
    st, j = chesto("POST", "/auth/login", json={"email": email, "password": pw})
    if st != 200 or not j.get("token"):
        print("Login gagal:", st, json.dumps(j)[:200])
        return None
    print("Login OK, uid:", j.get("uid"))
    return j["token"]


def checkin_dan_bonus():
    print("\n== CHECK-IN HARIAN + WELCOME BONUS ==")
    tok = login_interaktif()
    if not tok:
        return
    st, j = chesto("POST", "/auth/claim-welcome-bonus", token=tok, json={})
    print("welcome bonus:", st, json.dumps(j)[:200])
    st, j = chesto("POST", "/auth/checkin", token=tok, json={})
    print("check-in:", st, json.dumps(j)[:200])
    st, j = chesto("GET", "/auth/me", token=tok)
    print("karma sekarang:", j.get("karma"), "| saldo:", j.get("balance"))


def cek_akun():
    print("\n== CEK AKUN ==")
    tok = login_interaktif()
    if not tok:
        return
    st, j = chesto("GET", "/auth/me", token=tok)
    print("uid:", j.get("uid"), "| email:", j.get("email"))
    print("karma:", j.get("karma"), "| saldo USDC:", j.get("balance"))
    print("terverifikasi:", j.get("isVerified"))
    st, j = chesto("GET", "/auth/referral-stats", token=tok)
    print("kode ref:", j.get("referralCode"),
          "| link:", f"{BASE}/register?ref={j.get('referralCode')}")
    print("jumlah referral:", j.get("referralCount"))
    print("komisi:", json.dumps(j.get("commissionPolicy"), ensure_ascii=False))
    st, j = chesto("GET", "/users/withdraw/preview?amount=0.1", token=tok)
    print("preview WD 0.1 USDC:", json.dumps(j, ensure_ascii=False))


def lihat_tugas():
    print("\n== TUGAS USDC AKTIF (tanpa login) ==")
    st, j = chesto("GET", "/tasks?limit=100")
    if not isinstance(j, list):
        print("gagal ambil tugas:", st, str(j)[:200])
        return
    for t in j:
        ar = t.get("accountRequirements", {})
        print(f"- {t.get('title')} | {t.get('reward')} USDC | {t.get('status')}"
              f" | X: {ar.get('minFollowers')}+ followers, {ar.get('minAgeDays')}+ hari,"
              f" {ar.get('minTweets')}+ tweet")
    print("\nTotal tugas:", len(j),
          "| yang bayar USDC tanpa syarat X: TIDAK ADA (semua butuh akun X).")


def main():
    print("=" * 52)
    print("CHESTO AI — daftar + check-in (versi bersih)")
    print("Gratis. Min WD 0.01 USDC, fee 0. Butuh akun X")
    print("100+ hari / 40+ followers untuk tugas USDC.")
    print("=" * 52)
    while True:
        print("\n[1] Daftar akun baru")
        print("[2] Check-in harian + klaim welcome bonus")
        print("[3] Cek saldo / Karma / link referral")
        print("[4] Lihat tugas USDC aktif")
        print("[5] Keluar")
        p = input("➤ PILIH MENU » ").strip()
        if p == "1":
            daftar_baru()
        elif p == "2":
            checkin_dan_bonus()
        elif p == "3":
            cek_akun()
        elif p == "4":
            lihat_tugas()
        elif p == "5":
            print("Sampai jumpa.")
            sys.exit(0)
        else:
            print("Pilihan tidak ada, coba lagi.")


if __name__ == "__main__":
    main()
