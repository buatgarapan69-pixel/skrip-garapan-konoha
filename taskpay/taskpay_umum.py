#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASKPAY (@TaskPayWalletbot) — skrip umum 1 akun.
Mini App Lovable + Supabase: auth via initData Telegram + fingerprint device,
klaim iklan interstitial 0,001 USDT (maks 10/hari), cek saldo + referral.
GRATIS saja: tanpa deposit, tanpa top-up, tanpa withdraw otomatis.

CARA PAKAI:
1. pip install telethon requests
2. Isi API_ID + API_HASH dari https://my.telegram.org (akun Telegram kamu)
3. SESSION_NAME = nama file session Telethon kamu (tanpa .session)
4. REF_CODE = kode referral kamu (angka ID Telegram pengundang) — kosongkan
   kalau daftar tanpa referral. Contoh: REF_CODE = "<ID_TELEGRAM_PENGUNDANG>"
5. python3 taskpay_umum.py

CARA KERJA (hasil reverse engineering Mini App, 28 Nov 2026):
- Buka Mini App TaskPayWalletbot, ambil initData (tgWebAppData) via Telethon.
- Auth ke server function /_serverFn/<id-auth> (TanStack Start, body seroval).
- Fingerprint device = SHA-256 dari UA + bahasa + CPU/RAM + layar + zona
  waktu + canvas. HARUS stabil per akun (server menolak device ganda).
- Klaim interstitial: POST /_serverFn/<id-claim> {initData, fingerprint}.
  Server TIDAK verifikasi iklan ditonton (klaim langsung dikredit).
  Jeda beberapa detik antar klaim, maks 10/hari.
- Klaim AdsGram (0,002 USDT, 5/hari) TIDAK bisa via API — server menolak
  (UNAUTHORIZED) kalau iklan tidak ditonton beneran di WebView.
- Referral 0,05 USDT dibayar kalau teman join 2 channel + selesaikan
  5 tugas. Daftar tugas saat probe kosong — kualifikasi bisa tertunda.
- Min WD 0,10 USDT (BEP-20), maks 2 WD/hari. WD TIDAK otomatis di skrip
  ini — ajukan manual dari Mini App kalau saldo sudah >= 0,10 USDT.
- Payout platform TERBUKTI on-chain (WD 0,10 USDT cair, cek channel
  @TaskWalletPayment). WD kamu sendiri tetap harus dibuktikan.

PERINGATAN:
- 1 akun = 1 device fingerprint + 1 IP. Jangan jalankan banyak akun dari
  1 IP tanpa proxy residensial beda per akun — server memblokir device
  ganda (alasan "device", akun pertama yang menang).
- Jangan pakai skrip ini untuk akun utama + 30 akun kloning dari IP yang
  sama tanpa memahami risikonya.
"""
import asyncio
import base64
import hashlib
import itertools
import json
import random
import sys
import urllib.parse

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser

# ============================== ISI DULU ==============================
API_ID = 0  # <-- isi: API ID dari https://my.telegram.org
API_HASH = ""  # <-- isi: API HASH dari https://my.telegram.org
SESSION_NAME = ""  # <-- isi: nama file session Telethon kamu (tanpa .session)
REF_CODE = ""  # <-- isi: ID Telegram pengundang (angka), atau "" kalau tanpa ref
# ======================================================================

BOT = "TaskPayWalletbot"
APP = "https://taskpaywallet.lovable.app"
# ID server function (dari bundle JS Mini App https://taskpaywallet.lovable.app/)
AUTH_FN = "2673fad9d98c301ee8a668c1a9d1a13b13008b6459bb3437378d70c0ab9d897b"
USER_FN = "bfc8ec2339572b6bbf4e5412d6956769e70c4db445bb81edd7cb521bc493b03c"
CLAIM_FN = "cebb24feba4b8dd75111b818af6c5d102c33e75225664e17cf9e3161ef804356"
TASKS_FN = "37c4419c6a6ec037e65e9a2cab521bdb14be385fe875357129e9186ea8f0c1a1"
REFERRAL_FN = "10d5719f946ed1ff06a06fb59bb1aec6138ffed988a380191dcacafe221404e0"

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

_counter = itertools.count()


def fingerprint(seed_text):
    """Fingerprint device deterministik (stabil per akun)."""
    seed = int(hashlib.sha256(seed_text.encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    canvas = ("data:image/png;base64," +
              base64.b64encode(("fp-taskpay-" + seed_text).encode()).decode())
    parts = [UA, "en", str(rnd.choice([4, 6, 8])), str(rnd.choice([4, 6, 8])),
             "1080x2400x24", "Asia/Jakarta", canvas]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def enc(v):
    """Encode satu nilai ke format seroval-JSON (yang dipakai TanStack Start)."""
    if v is None:
        return {"t": 2, "s": 1}
    if v is True:
        return {"t": 2, "s": 2}
    if v is False:
        return {"t": 2, "s": 3}
    if isinstance(v, (int, float)):
        return {"t": 0, "s": v}
    if isinstance(v, str):
        return {"t": 1, "s": v}
    if isinstance(v, list):
        i = next(_counter)
        return {"t": 9, "i": i, "a": [enc(x) for x in v], "o": 0}
    if isinstance(v, dict):
        i = next(_counter)
        return {"t": 10, "i": i,
                "p": {"k": list(v.keys()), "v": [enc(x) for x in v.values()]}, "o": 0}
    raise ValueError(type(v))


def seroval_body(data):
    global _counter
    _counter = itertools.count()
    return json.dumps({"t": enc({"data": data})}, separators=(",", ":"))


def dec(node):
    if not isinstance(node, dict) or "t" not in node:
        return node
    t = node["t"]
    if t == 0:
        return node.get("s")
    if t == 1:
        return node.get("s")
    if t == 2:
        return {0: None, 1: None, 2: True, 3: False}.get(node.get("s"))
    if t == 9:
        return [dec(x) for x in node.get("a", [])]
    if t in (10, 11):
        p = node.get("p", {})
        return {k: dec(v) for k, v in zip(p.get("k", []), p.get("v", []))}
    if t == 25:
        return {"_error": dec(node.get("s"))}
    return {"_unknown_t": t}


def api(fn_id, data, ua=UA):
    r = requests.post(APP + "/_serverFn/" + fn_id, data=seroval_body(data),
                      headers={"x-tsr-serverFn": "true", "accept": "application/json",
                               "content-type": "application/json", "User-Agent": ua,
                               "Origin": APP, "Referer": APP + "/"}, timeout=25)
    try:
        d = dec(json.loads(r.text))
        if isinstance(d, dict) and "result" in d:
            d = d["result"]
    except Exception:
        d = {"_raw": r.text[:300]}
    return {"status": r.status_code, "result": d}


async def get_initdata():
    """Join 2 channel wajib + /start (pakai ref kalau ada) + ambil initData."""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH,
                            device_model="Google Pixel 7", system_version="Android 13",
                            lang_code="en")
    await client.connect()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.id, me.username)
        bot = await client.get_entity(BOT)
        try:
            await client(UnblockRequest(id=InputPeerUser(bot.id, bot.access_hash)))
        except Exception:
            pass
        for ch in ("TaskPayWallet", "TaskWalletPayment"):
            try:
                await client(JoinChannelRequest(await client.get_entity(ch)))
                print("Join channel:", ch)
            except Exception as e:
                print("Join gagal:", ch, repr(e)[:120])
            await asyncio.sleep(2)
        start = f"/start ref_{REF_CODE}" if REF_CODE else "/start"
        await client.send_message(bot, start)
        await asyncio.sleep(10)
        # Klik tombol Verify kalau muncul
        last = None
        async for m in client.iter_messages(bot, limit=1):
            last = m
        if last and last.reply_markup:
            for ri, row in enumerate(last.reply_markup.rows):
                for bi, b in enumerate(row.buttons):
                    if "Verify" in (b.text or ""):
                        try:
                            print("Verify:", str(await last.click(ri, bi))[:150])
                        except Exception as e:
                            print("Verify gagal:", repr(e)[:120])
                        break
        await asyncio.sleep(3)
        kw = {"start_param": f"ref_{REF_CODE}"} if REF_CODE else {}
        r = await client(RequestAppWebViewRequest(
            peer=InputPeerUser(bot.id, bot.access_hash),
            app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash),
                                     short_name="app"),
            platform="android", **kw))
        frag = urllib.parse.urlparse(r.url).fragment
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        return me.id, initdata
    finally:
        await client.disconnect()


async def main():
    if not API_ID or not API_HASH or not SESSION_NAME:
        print("ISI DULU API_ID, API_HASH, dan SESSION_NAME di atas.")
        sys.exit(1)
    tg_id, initdata = await get_initdata()
    if not initdata:
        print("Gagal ambil initData — buka Mini App manual sekali dari Telegram.")
        sys.exit(1)
    fp = fingerprint(str(tg_id))
    sp = f"ref_{REF_CODE}" if REF_CODE else None
    auth = api(AUTH_FN, {"initData": initdata, "fingerprint": fp, "startParam": sp})
    print("Auth:", auth["status"], json.dumps(auth["result"], ensure_ascii=False)[:300])
    if not (isinstance(auth["result"], dict) and auth["result"].get("ok")):
        print("Auth gagal — mungkin belum join channel / device diblokir.")
        print("Alasan server:", auth["result"])
        sys.exit(1)
    user = api(USER_FN, {"initData": initdata, "fingerprint": fp})
    u = user["result"] if isinstance(user["result"], dict) else {}
    print("Saldo awal:", u.get("balance"), "| Min WD:", u.get("min_withdrawal"),
          "| Tugas selesai:", u.get("tasks_completed"))
    tasks = api(TASKS_FN, {"initData": initdata, "fingerprint": fp})
    tl = tasks["result"] if isinstance(tasks["result"], list) else []
    print("Daftar tugas tersedia:", len(tl))
    if tl:
        print("ADA TUGAS BARU — selesaikan manual dari Mini App (klaim tugas",
              "channel butuh verifikasi membership, belum tentu bisa via API).")
    claimed = 0
    for _ in range(10):
        m = api(CLAIM_FN, {"initData": initdata, "fingerprint": fp})
        mr = m["result"] if isinstance(m["result"], dict) else {}
        if mr.get("ok") and mr.get("credited"):
            claimed += 1
            print(f"Klaim {claimed}: +{mr['credited']} USDT (pakai {mr['used']}/{mr['limit']})")
            await asyncio.sleep(8)
        else:
            print("Klaim berhenti:", mr.get("error") or m)
            break
    user2 = api(USER_FN, {"initData": initdata, "fingerprint": fp})
    u2 = user2["result"] if isinstance(user2["result"], dict) else {}
    print("Saldo akhir:", u2.get("balance"), "| Total earn:", u2.get("total_earned"))
    ref = api(REFERRAL_FN, {"initData": initdata, "fingerprint": fp})
    rr = ref["result"] if isinstance(ref["result"], dict) else {}
    print("Referral: total", rr.get("total"), "| qualified", rr.get("qualified"),
          "| earned", rr.get("total_earned"))
    print("SELESAI. Klaim interstitial:", claimed, "x 0,001 USDT.")


asyncio.run(main())
