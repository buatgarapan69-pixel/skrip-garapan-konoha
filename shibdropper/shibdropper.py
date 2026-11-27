#!/usr/bin/env python3
"""
SHIBDropperBot (@SHIBDropperBot) — skrip gratis untuk 1 akun Telegram.
Mini App SHIB di BNB Smart Chain (BEP20): bonus daftar 10.000 SHIB,
per referral 5.000 SHIB, min WD 20.000 SHIB + 2 referral terverifikasi.
Payout BELUM TERBUKTI (WD Naruto 27 Nov 2026 TERKENDALA — server menolak
alamat wallet yang sudah dipakai akun lain; 1 alamat = 1 akun).

CARA ISI (wajib, tanpa ini skrip tidak jalan):
  1. API_ID + API_HASH: ambil gratis di https://my.telegram.org
     (login -> API development -> buat app, salin angkanya ke bawah).
  2. SESSION_NAME: nama file sesi Telethon, mis. "akun_saya".
     Saat pertama jalan, Telethon minta nomor HP + kode OTP
     dari Telegram (ketik di terminal). File .session JANGAN
     dibagikan ke siapa pun — itu kunci akunmu.
  3. WALLET_ADDRESS: alamat BEP20 MILIKMU SENDIRI (0x...).
     WAJIB alamat yang BELUM PERNAH dipakai di bot ini
     (server menolak alamat yang sudah terdaftar akun lain).
     JANGAN pakai alamat orang lain. Boleh dikosongkan ("")
     kalau cuma mau daftar + ambil link referral dulu.
  4. REF_CODE: (opsional) kode referral pengundang, mis. "7590298679".
     Kosongkan ("") kalau daftar tanpa pengundang.
  5. PROXY: (opsional) proxy HTTP kamu, format
     "http://user:pass@host:port". Kosongkan ("") kalau tidak ada.

CARA PAKAI (Termux / Linux):
  pip install telethon requests faker
  python3 shibdropper.py
  -> pilih menu di dalam skrip (1 perintah, semua di dalam).

YANG DILAKUKAN SKRIP (gratis, tanpa deposit):
  [1] Probe: /start bot, cek respons + ambil link Mini App.
  [2] Daftar: join 3 channel, buka Mini App, auth, captcha
      logo-match (jeda manusiawi), onboard, klaim bonus.
  [3] Simpan wallet BEP20 kamu (kalau diisi) + cek saldo.
  [4] Tampilkan link referral MILIKMU + saldo.
  [5] Cek status WD (tidak mengajukan WD otomatis).

PERINGATAN:
  - JANGAN PERNAH memasukkan private key / seed phrase ke skrip ini.
  - Skrip ini TIDAK meminta uang, TIDAK deposit, TIDAK WD otomatis.
  - Kalau bot minta deposit/fee sebelum bisa earn, BERHENTI — itu
    ciri scam/fee-gate. Lapor ke admin channel garapanmu.
  - WD di bot ini menarik SELURUH saldo (tidak ada pilihan jumlah),
    dan saldo + referral yang dipakai WD dipotong permanen saat
    submit meski request ditolak. Jadi JANGAN submit WD sebelum
    yakin payout-nya terbukti.

Dibuat Tim Konoha, 27 Nov 2026. Gratis, tanpa garansi cuan.
"""
import asyncio
import json
import random
import secrets
import sys
import time
import urllib.parse

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest

# ===================== ISI BAGIAN INI =====================
API_ID = 0            # <-- ISI: angka API ID dari my.telegram.org
API_HASH = ""         # <-- ISI: API hash dari my.telegram.org
SESSION_NAME = ""     # <-- ISI: nama sesi, mis. "akun_saya"
WALLET_ADDRESS = ""   # <-- ISI: alamat BEP20 milikmu (0x...), "" kalau belum
REF_CODE = ""         # <-- ISI: kode referral pengundang (opsional)
PROXY = ""            # <-- ISI: proxy HTTP (opsional), "" kalau tidak ada
# ==========================================================

BOT = "SHIBDropperBot"
URL = "https://bep20.usdtbnbreward.live/shiba"
BASE = "https://bep20.usdtbnbreward.live"
CHANNELS = ["SHIBDropper", "SHIBDropperPay", "HexAirdropOfficial"]
MODELS = ["Pixel 7", "Pixel 8", "SM-A536B", "Redmi Note 11", "SM-G991B"]
UAS = [
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
]

BANNER = r"""
  ____  _   _ ___ ____  ____
 / ___|| | | |_ _| __ )|  _ \
 \___ \| |_| || ||  _ \| | | |
  ___) |  _  || || |_) | |_| |
 |____/|_| |_|___|____/|____/
 SHIBDropper — gratis, tanpa deposit
"""


def cek_config():
    if not API_ID or not API_HASH or not SESSION_NAME:
        print("ISI DULU API_ID, API_HASH, SESSION_NAME di atas skrip.")
        print("API_ID/API_HASH gratis di https://my.telegram.org")
        sys.exit(1)


def api_call(sess, method, path, body=None):
    r = sess.request(method, BASE + "/shiba/api" + path, json=body, timeout=30)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"_raw": r.text[:500]}


async def get_initdata():
    client = TelegramClient(SESSION_NAME, int(API_ID), str(API_HASH))
    await client.start()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.id, "@" + (me.username or "-"))
        ent = await client.get_entity(BOT)
        print("Bot:", ent.id, "@" + ent.username,
              "| scam:", ent.scam, "| fake:", ent.fake,
              "| verified:", ent.verified)
        start = "/start " + REF_CODE if REF_CODE else "/start"
        await client.send_message(ent, start)
        print("Terkirim:", start)
        await asyncio.sleep(3)
        for ch in CHANNELS:
            try:
                await client(JoinChannelRequest(ch))
                print("Join channel:", ch)
            except Exception as e:
                print("Gagal join", ch, ":", repr(e)[:100])
            await asyncio.sleep(1)
        wv = await client(RequestWebViewRequest(
            peer=ent, bot=ent, platform="android", from_bot_menu=False,
            url=URL, start_param=REF_CODE or None))
        init = urllib.parse.parse_qs(
            urllib.parse.urlparse(wv.url).fragment
        ).get("tgWebAppData", [None])[0]
        return init
    finally:
        await client.disconnect()


def daftar(init_data):
    ua = random.choice(UAS)
    model = random.choice(MODELS)
    device_id = secrets.token_hex(32)
    s = requests.Session()
    if PROXY:
        s.proxies = {"http": PROXY, "https": PROXY}
    s.headers.update({
        "User-Agent": ua, "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": BASE, "Referer": BASE + "/shiba/",
    })
    s.cookies.set("shiba_device", device_id,
                  domain="bep20.usdtbnbreward.live", path="/shiba/")
    st, auth = api_call(s, "POST", "/auth",
                        {"init_data": init_data, "device_id": device_id})
    print("Auth:", st)
    if st != 200:
        print("Auth gagal:", auth)
        return
    print("Saldo awal:", auth.get("balance"),
          "| onboarded:", auth.get("onboarded"))
    print("Min WD:", auth.get("minimum"),
          "| referral butuh:", auth.get("required_refs"))
    st, cap = api_call(s, "GET", "/captcha")
    if st == 200 and cap.get("nonce"):
        print("Captcha nonce didapat, menunggu 7-12 detik...")
        time.sleep(random.uniform(7, 12))
        st, cap2 = api_call(s, "POST", "/captcha",
                            {"nonce": cap["nonce"], "progress": 100})
        print("Captcha:", st, cap2)
        if st != 200:
            print("Captcha gagal. Coba lagi nanti (jangan spam).")
            return
    st, ob = api_call(s, "POST", "/onboard",
                      {"device_id": device_id, "device_model": model})
    print("Onboard:", st, ob)
    st, me = api_call(s, "GET", "/me")
    if st == 200:
        print("Saldo:", me.get("balance"), "SHIB")
        print("Link referral kamu:", me.get("referral_link"))
        if WALLET_ADDRESS:
            st, w = api_call(s, "PUT", "/wallet",
                             {"address": WALLET_ADDRESS})
            print("Simpan wallet:", st, w)
            if st == 200:
                print("Wallet tersimpan. Cek saldo lagi:")
                st, me2 = api_call(s, "GET", "/me")
                print("Saldo:", me2.get("balance"),
                      "| wallet:", me2.get("wallet"))
        else:
            print("Wallet belum diisi — simpan nanti di menu akun bot.")
    print("SELESAI. Sebar link referral-mu buat nambah saldo.")


def cek_status(init_data):
    ua = random.choice(UAS)
    device_id = secrets.token_hex(32)
    s = requests.Session()
    if PROXY:
        s.proxies = {"http": PROXY, "https": PROXY}
    s.headers.update({
        "User-Agent": ua, "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": BASE, "Referer": BASE + "/shiba/",
    })
    s.cookies.set("shiba_device", device_id,
                  domain="bep20.usdtbnbreward.live", path="/shiba/")
    st, auth = api_call(s, "POST", "/auth",
                        {"init_data": init_data, "device_id": device_id})
    if st != 200:
        print("Auth gagal:", auth)
        return
    print("Saldo:", auth.get("balance"), "| tersedia:", auth.get("available"))
    print("Total referral:", auth.get("total_refs"),
          "| terverifikasi:", auth.get("verified_refs"))
    print("Min WD:", auth.get("minimum"),
          "| referral butuh:", auth.get("required_refs"))
    print("Wallet:", auth.get("wallet") or "(belum disimpan)")
    print("Link referral:", auth.get("referral_link"))
    st, wd = api_call(s, "GET", "/withdrawals")
    print("Riwayat WD:", json.dumps(wd, ensure_ascii=False)[:1000])


def menu():
    print(BANNER)
    print("[1] Probe bot (cek respons saja)")
    print("[2] Daftar + klaim bonus + simpan wallet")
    print("[3] Cek saldo + status WD")
    print("[0] Keluar")
    return input("➤ PILIH MENU » ").strip()


async def main():
    cek_config()
    while True:
        pilih = menu()
        if pilih == "0":
            print("Keluar.")
            break
        if pilih not in ("1", "2", "3"):
            print("Pilihan tidak ada, coba lagi.")
            continue
        init = await get_initdata()
        if not init:
            print("Gagal ambil initData Mini App. Bot mungkin mati.")
            continue
        if pilih == "1":
            print("Bot RESPONS. Mini App hidup, initData didapat.")
            print("Lanjut menu [2] buat daftar.")
        elif pilih == "2":
            await asyncio.to_thread(daftar, init)
        elif pilih == "3":
            await asyncio.to_thread(cek_status, init)
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDibatalkan.")
