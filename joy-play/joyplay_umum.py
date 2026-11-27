#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JOY PLAY — skrip umum (versi publik, tanpa data pribadi).
Bot Telegram @joyplayappbot: undang teman Rp500/orang, Mystery Box gratis
tiap hari Rp100-Rp600, min WD Rp10.000 ke DANA/OVO/GoPay/ShopeePay/Bank/Pulsa.
WD manual admin maks 1x24 jam. Payout BELUM terbukti — garap gratis saja,
jangan deposit, jangan hubungkan wallet berisi dana.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon requests
  2. Ambil API_ID + API_HASH di https://my.telegram.org
  3. export TG_API_ID=123456 TG_API_HASH=abcdef... (atau isi di bawah)
  4. (Opsional) isi REF_CODE dengan kode referral temanmu, misal
     REF_CODE = "ref_1234567890" — kosongkan kalau daftar tanpa referral.
  5. python3 joyplay_umum.py — pilih menu di dalam skrip.

Menu:
  [1] Daftar + verifikasi + buka Mystery Box (sekali jalan)
  [2] Cek saldo / status akun
  [3] Keluar

Skrip ini TIDAK berisi session, token, password, atau referral siapa pun.
Semua data akun dibaca dari session Telethon milikmu sendiri.
"""
import asyncio
import json
import os
import sys
import urllib.parse
import urllib.request

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.types import InputPeerUser

BOT = "joyplayappbot"
CHANNEL = "joyplayapp"
WEBVIEW_URL = "https://panelmamzzpanel8412.buyervps.my.id/joyplay"
API = "https://panelmamzzpanel8412.buyervps.my.id/joy-api"

API_ID = int(os.environ.get("TG_API_ID", "0") or 0)
API_HASH = os.environ.get("TG_API_HASH", "")
SESSION = os.environ.get("TG_SESSION", "joyplay")
# Isi dengan kode referral (contoh: "ref_1234567890") atau "" untuk tanpa referral.
REF_CODE = os.environ.get("JOYPLAY_REF", "")

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")


def api(path, init_data, extra=None):
    body = {"initData": init_data}
    if extra:
        body.update(extra)
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


async def get_init_data(client, bot):
    r = await client(RequestWebViewRequest(
        peer=InputPeerUser(bot.id, bot.access_hash),
        bot=InputPeerUser(bot.id, bot.access_hash),
        url=WEBVIEW_URL, platform="android", from_bot_menu=True))
    frag = urllib.parse.urlparse(r.url).fragment
    return urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]


async def daftar():
    if not API_ID or not API_HASH:
        print("Isi dulu TG_API_ID + TG_API_HASH (lihat header skrip).")
        return
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.id, me.username)
        bot = await client.get_entity(BOT)
        start = "/start " + REF_CODE if REF_CODE else "/start"
        await client.send_message(bot, start)
        await asyncio.sleep(5)
        ch = await client.get_entity(CHANNEL)
        try:
            await client(JoinChannelRequest(ch))
            print("Gabung channel @%s: OK" % CHANNEL)
        except Exception as e:
            print("Gabung channel gagal:", str(e)[:120])
        init_data = await get_init_data(client, bot)
        if not init_data:
            print("Gagal ambil initData WebView.")
            return
        st = api("/state", init_data)
        print("Status awal:", json.dumps(st.get("state", st), ensure_ascii=False))
        v = api("/verify", init_data)
        print("Verifikasi:", v.get("message") or v)
        b = api("/box", init_data)
        print("Mystery Box:", "OK +Rp%d" % b["prize"] if b.get("ok") else b)
        st = api("/state", init_data)
        u = st.get("state", {}).get("user", {})
        print("Saldo akhir: Rp%d | Teman terverifikasi: %d | Pending: %d"
              % (u.get("balance", 0), u.get("invites", 0), u.get("pending", 0)))
        print("Link referral kamu:", st.get("state", {}).get("ref_link"))
    finally:
        await client.disconnect()


async def cek():
    if not API_ID or not API_HASH:
        print("Isi dulu TG_API_ID + TG_API_HASH (lihat header skrip).")
        return
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    try:
        bot = await client.get_entity(BOT)
        init_data = await get_init_data(client, bot)
        if not init_data:
            print("Gagal ambil initData WebView.")
            return
        st = api("/state", init_data)
        u = st.get("state", {}).get("user", {})
        c = st.get("state", {}).get("config", {})
        print("Saldo: Rp%d | Teman: %d | Pending: %d | Min WD: Rp%d"
              % (u.get("balance", 0), u.get("invites", 0),
                 u.get("pending", 0), c.get("min_wd", 0)))
        print("Box hari ini:", "sudah dibuka" if st.get("state", {}).get("box", {}).get("claimed_today") else "tersedia")
        print("Link referral kamu:", st.get("state", {}).get("ref_link"))
    finally:
        await client.disconnect()


def menu():
    while True:
        print("\n===== JOY PLAY =====")
        print("[1] Daftar + verifikasi + buka Mystery Box")
        print("[2] Cek saldo / status akun")
        print("[3] Keluar")
        p = input("➤ PILIH MENU » ").strip()
        if p == "1":
            asyncio.run(daftar())
        elif p == "2":
            asyncio.run(cek())
        elif p == "3":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak dikenal.")


if __name__ == "__main__":
    menu()
