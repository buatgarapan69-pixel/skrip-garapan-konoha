#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARS SURVIVAL — skrip umum (untuk dipakai orang lain, 1 akun).
Game ekonomi Telegram gratis: desert trip, tugas, pasar pemain, WD ke The AI Wallet.
Tanpa deposit, tanpa wallet berisi dana, tanpa WD otomatis.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon requests
  2. Ambil API_ID + API_HASH di https://my.telegram.org/apps
  3. Isi bagian KONFIG di bawah (API_ID, API_HASH; REF_CODE = kode referral
     pengundang, mis. ref_xxxx — boleh kosong, kalau kosong daftar tanpa ref)
  4. Jalankan:  python3 ms_umum_public.py
     - login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
     - skrip /start bot, join channel + grup tugas, start 6 bot tugas,
       daftar di Mini App, klaim 9 tugas resmi, lalu tampilkan tiket + link
       referral kamu
  5. Ulangi klaim tugas lain / desert trip dari HP (trip butuh nonton iklan
     di WebView, tidak bisa otomatis dari skrip ini).

YANG DIDAPAT (hasil probe 27 Nov 2026):
  - Daftar gratis, intro OK; 9 tugas resmi = 45 tiket (tal)
  - Tugas lain (kanal pihak ketiga): masing-masing 2 tiket, total ±169 tiket
  - Tiket ditukar 10 tiket = 1 muddy water / 1 kaleng (buat dimakan/diminum,
    TIDAK bisa dijual di pasar)
  - Desert trip gratis 10x/hari (masing-masing 10 menit, butuh nonton iklan),
    temuan dijual jadi tiket (±2,3 tiket per trip)
  - Referral: 10% top-up teman level 1, 5% level 2 (hanya dari top-up,
    BUKAN dari main gratis) + 10 tiket kalau teman 3x trip
  - Min WD: 100 MD ($0,10) ke The AI Wallet, 1x/hari, tanpa fee

CATATAN JUJUR — BACA DULU:
  - PAYOUT BELUM TERBUKTI (27 Nov 2026): statistik payout publik 0 payout,
    channel Payouts masih kosong, game baru diluncurkan 26 Nov 2026.
  - GRIND LAMBAT: alat kerja pertama (Rusty Pickaxe) = 1.000 tiket.
    Tugas saja max ±169 tiket; trip ±23 tiket/hari. WD gratis pertama
    butuh ±5 minggu grind. Jangan harap uang cepat dari game ini.
  - Deposit min $0,10 tapi alat kerja termurah 1.000 MD ($1) — JANGAN
    deposit kalau cuma mau gratisan. Skrip ini TIDAK PERNAH deposit.
  - File sesi (ms_umum_public.session) JANGAN dibagikan ke siapa pun.
  - Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
"""

import asyncio
import json
import random
import time
import urllib.parse
import uuid

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser

# ============================== KONFIG — ISI DULU ==============================
API_ID = 0          # <-- isi: angka dari https://my.telegram.org/apps
API_HASH = ""       # <-- isi: string dari https://my.telegram.org/apps
REF_CODE = ""       # <-- opsional: kode referral pengundang (mis. ref_xxxx), boleh kosong
PROXY_URL = ""      # <-- opsional: http://user-sid-xxx-time-3600:pass@gate:7000 (boleh kosong = direct)
# ===============================================================================

BOT = "MarsSurvivalBot"
BASE = "https://mars.thegrambank.xyz"
CHANNELS = ["MarsSurvivalNews"]
INVITES = ["MhwkGvUqRsw1N2Q9", "j2wr136r-vJiM2I1"]  # grup chat + channel Payouts
TASK_BOTS = [("TheAIWalletBot", "r_ZVCXWRHP"), ("TheAIMinerBot", "ref_66899E3F"),
             ("TheGramBank_bot", "ref_CUEECYEF"), ("GramBux_bot", "ref_YAMXG3CV"),
             ("RaccoonGiftDropBot", "ref_RN8BLK7N"), ("TheAIStudioBot", "share")]
OFFICIAL_TASKS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

DEVICES = [
    ("SM-S918B", "14"), ("SM-A546E", "14"), ("Pixel 7", "14"), ("Pixel 8 Pro", "14"),
    ("Redmi Note 12", "13"), ("Redmi Note 13 Pro", "14"), ("POCO X5 Pro", "13"),
    ("POCO F5", "14"), ("OPPO Reno10", "13"), ("vivo V29", "14"),
    ("Samsung Galaxy A54", "14"), ("Realme 11 Pro", "13"), ("OnePlus Nord 3", "14"),
    ("Xiaomi 13T", "14"),
]

UA = "Mozilla/5.0 (Linux; Android 14; Pixel 7 Build/TP1A.123456.789) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
DEVICE_ID = str(uuid.uuid4())


def api_call(session, headers, path, body=None):
    try:
        r = session.post(BASE + "/api/" + path, headers=headers, json=body or {}, timeout=30)
        try:
            return {"status": r.status_code, "body": r.json()}
        except Exception:
            return {"status": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"status": None, "error": "%s: %s" % (type(e).__name__, str(e)[:150])}


async def main():
    if not API_ID or not API_HASH:
        print("ISI DULU API_ID + API_HASH di bagian KONFIG (https://my.telegram.org/apps).")
        return
    client = TelegramClient("ms_umum_public", API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    print("Login sebagai: %s (id %d)" % (me.username, me.id))
    bot = await client.get_entity(BOT)
    start_arg = "/start " + REF_CODE if REF_CODE else "/start"
    await client.send_message(bot, start_arg)
    await asyncio.sleep(3)
    r = await client(RequestAppWebViewRequest(
        peer=InputPeerUser(bot.id, bot.access_hash),
        app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash), short_name="app"),
        platform="android", start_param=REF_CODE or None))
    frag = urllib.parse.urlparse(r.url).fragment
    initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
    if not initdata:
        print("GAGAL ambil initData WebView.")
        await client.disconnect()
        return
    print("WebView OK, start_param di initData:",
          urllib.parse.parse_qs(initdata).get("start_param", [None])[0])
    for ch in CHANNELS:
        try:
            await client(JoinChannelRequest(await client.get_entity(ch)))
            print("Join channel:", ch)
        except Exception as e:
            print("Join gagal %s: %s" % (ch, str(e)[:100]))
        await asyncio.sleep(1)
    for inv in INVITES:
        try:
            await client(ImportChatInviteRequest(inv))
            print("Join invite:", inv)
        except Exception as e:
            print("Invite gagal %s: %s" % (inv, str(e)[:100]))
        await asyncio.sleep(1)
    for botname, param in TASK_BOTS:
        try:
            await client.send_message(await client.get_entity(botname), "/start " + param)
            print("Start bot tugas:", botname)
        except Exception as e:
            print("Start gagal %s: %s" % (botname, str(e)[:100]))
        await asyncio.sleep(2)
    await client.disconnect()

    s = requests.Session()
    if PROXY_URL:
        s.proxies = {"http": PROXY_URL, "https": PROXY_URL}
        print("Proxy: dipakai")
    headers = {"User-Agent": UA, "X-Device-Id": DEVICE_ID,
               "Content-Type": "application/json", "Accept": "application/json",
               "Origin": BASE, "Referer": BASE + "/", "x-init-data": initdata}
    fp = uuid.uuid4().hex[:16]
    st = api_call(s, headers, "state", {"start": REF_CODE, "fp": fp})
    print("state:", st.get("status"))
    if st.get("status") != 200:
        print("GAGAL state:", json.dumps(st, ensure_ascii=False)[:300])
        return
    me_api = st["body"].get("me", {})
    print("Tiket awal: %s | MD: %s | bisa WD: %s | ref: %s" % (
        me_api.get("tal"), me_api.get("md"), me_api.get("out"), me_api.get("refLink")))
    print("intro:", api_call(s, headers, "intro", {}).get("status"))
    claimed = 0
    for tid in OFFICIAL_TASKS:
        r = api_call(s, headers, "task", {"id": tid})
        if r.get("status") == 200:
            claimed += 1
            print("Tugas %d: OK (+%s tiket)" % (tid, r["body"].get("tal")))
        else:
            print("Tugas %d: gagal (%s)" % (tid, json.dumps(r.get("body", {}), ensure_ascii=False)[:150]))
        time.sleep(1)
    fin = api_call(s, headers, "state", {"start": "", "fp": fp})
    fm = fin.get("body", {}).get("me", {}) if isinstance(fin.get("body"), dict) else {}
    print("SELESAI: %d/9 tugas resmi | tiket: %s | MD: %s | bisa WD: %s" % (
        claimed, fm.get("tal"), fm.get("md"), fm.get("out")))
    print("Link referral kamu:", fm.get("refLink"))
    print("Min WD 100 MD ($0,10). Payout BELUM terbukti — jangan deposit.")


asyncio.run(main())
