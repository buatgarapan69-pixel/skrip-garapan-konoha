#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINI MICRO — garapan gratis (versi untuk orang lain, BERSIH).

Apa ini: bot Telegram @MiniMicroAiBot — saldo mining USDT 2%/hari,
gift box gratis, tugas join bot, referral. Min WD $0,01 USDT (BEP-20),
gratis sampai total $0,10 tanpa deposit; setelah itu deposit min $3.
Tanpa deposit, tanpa KYC. Payout PERTAMA BELUM terbukti (penulis naskah
ini baru sampai saldo USDT $0,0057 — WD menyusul).

CARA PAKAI (Termux / PC, Python 3.10+):
  1. pip install telethon
  2. Ambil API ID + API HASH di https://my.telegram.org (gratis).
  3. Isi API_ID, API_HASH, dan REF_LINK di bawah.
     REF_LINK = link referral KAMU SENDIRI, contoh:
       https://t.me/MiniMicroAiBot/Trade?startapp=123456789
     (123456789 = Telegram ID kamu. Kalau belum punya, daftar dulu
     lewat link teman, lalu ambil link referral kamu dari menu Friends.)
  4. Isi WD_ADDRESS dengan alamat BEP-20 (BNB Smart Chain) KAMU.
  5. Jalankan: python minimicro_gratis.py
     Login Telegram pertama kali akan minta nomor + kode OTP.
  6. Skrip ini TIDAK deposit, TIDAK top-up, TIDAK kirim dana.
     WD hanya jalan kalau saldo USDT kamu sudah >= $0,01.

YANG DILAKUKAN SKRIP (akun kamu saja, 1 akun):
  - /start + buka Mini App MiniMicroAiBot (pakai REF_LINK kamu)
  - Buka gift box gratis pertama (isi acak 1-5 koin; 100 koin = $1)
  - Klaim tugas yang tersedia (mis. join bot, $0,005/tugas)
  - Klaim hasil mining (2%/hari dari saldo koin kamu)
  - Kalau USDT >= $0,01: ajukan WD ke WD_ADDRESS (BEP-20)

CATATAN:
  - 1 akun = 1 HP/akun Telegram. Jangan jalankan banyak akun dari
    1 perangkat/IP yang sama — server punya deteksi perangkat ganda
    (fingerprint) dan bisa membekukan saldo.
  - Gift box ada jeda rate-limit server (~1 menit per box).
  - File .session yang dibuat skrip ini JANGAN dibagikan ke siapa pun.

Dibagikan gratis oleh Tim Konoha. Bukan ajakan deposit.
"""

import asyncio
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error

# ===================== ISI DI SINI =====================
API_ID = 0          # <-- isi: angka API ID dari https://my.telegram.org
API_HASH = ""       # <-- isi: API HASH dari https://my.telegram.org
REF_LINK = ""       # <-- isi: link referral KAMU, mis. https://t.me/MiniMicroAiBot/Trade?startapp=123456789
WD_ADDRESS = ""     # <-- isi: alamat BEP-20 (0x...) KAMU untuk WD USDT
# =======================================================

BOT = "MiniMicroAiBot"
APP_SHORT = "Trade"
BASE = "https://minimicroai.lovable.app"

# Server function ID (hash dari bundle JS publik aplikasi — stabil selama
# aplikasi tidak update; kalau suatu hari semua call gagal, ambil ulang
# dari file JS di https://minimicroai.lovable.app/assets/index-*.js).
FN_ME = "0d9e2e371b4bab4da7a71b5a2efcd0149c27f48dc15192cfdee2a995d5f6947e"
FN_GIFT = "21aff4856aa0147739b66c3269611c49fd8dd342144e4973589515477e97c95b"
FN_CLAIM = "bcb8e269d7f337068c7424538a77cd77e7013594ec5c8849925e8ca5b7cbe06c"
FN_TASKS = "b7dbe24e78781e17e1917bbb44450ff203aeadf2fe583087c9322715b1acbb58"
FN_CLAIM_TASK = "492e631710e8720355a9a835d804e87383267cdab9bec8f1c3373a25ce3fe3f4"
FN_WITHDRAW = "dc056b47c189103b348fcd294c028989d8ec8e13d8d465a8b303d73cff895f7e"

# ---------- Seroval codec (format body API TanStack Start) ----------
def _enc(value, counter):
    if isinstance(value, bool):
        return {"t": 2, "s": 2 if value else 3}
    if value is None:
        return {"t": 2, "s": 0}
    if isinstance(value, (int, float)):
        return {"t": 0, "s": value}
    if isinstance(value, str):
        return {"t": 1, "s": value}
    if isinstance(value, list):
        i = counter[0]; counter[0] += 1
        return {"t": 9, "i": i, "a": [_enc(x, counter) for x in value], "o": 0}
    if isinstance(value, dict):
        i = counter[0]; counter[0] += 1
        ks = list(value.keys())
        return {"t": 10, "i": i, "p": {"k": ks, "v": [_enc(value[k], counter) for k in ks]}, "o": 0}
    raise TypeError("tipe tidak didukung: %r" % type(value))

def seroval_body(data):
    counter = [0]
    return json.dumps({"t": _enc({"data": data}, counter), "f": 127, "m": []}).encode()

_SPEC = {0: None, 1: None, 2: True, 3: False}
def _dec(n):
    if not isinstance(n, dict) or "t" not in n:
        return n
    t = n["t"]
    if t in (0, 1):
        return n["s"]
    if t == 2:
        return _SPEC[n["s"]]
    if t == 9:
        return [_dec(x) for x in (n.get("a") or [])]
    if t in (10, 11):
        p = n.get("p") or {"k": [], "v": []}
        return {k: _dec(v) for k, v in zip(p["k"], p["v"])}
    return n

def api(fn_id, data, ua):
    req = urllib.request.Request(
        BASE + "/_serverFn/" + fn_id, data=seroval_body(data), method="POST",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "x-tsr-serverFn": "true",
                 "User-Agent": ua, "Origin": BASE, "Referer": BASE + "/"})
    proxy = os.environ.get("MINIMICRO_PROXY")  # opsional, mis. http://user:pass@host:port
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})) if proxy else urllib.request.build_opener()
    try:
        with opener.open(req, timeout=40) as r:
            return _dec(json.loads(r.read().decode("utf-8", "ignore")))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read()[:300].decode("utf-8", "ignore")}

# ---------- identitas perangkat (fingerprint, 1 perangkat = 1 nilai) ----------
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
FP_PARTS = [UA, "Linux armv8l", "8", "8", "1080", "2400", "24", "2.625",
            "Asia/Jakarta", "Google Inc. (ARM)|ANGLE (ARM, Mali-G710 MC10, OpenGL ES 3.0)", "5"]
FP = hashlib.sha256("~".join(FP_PARTS).encode()).hexdigest()

async def get_initdata():
    from telethon import TelegramClient
    from telethon.tl.functions.messages import RequestAppWebViewRequest
    from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser
    from urllib.parse import urlparse, parse_qs
    start = REF_LINK.rsplit("startapp=", 1)[-1] if "startapp=" in REF_LINK else ""
    client = TelegramClient("minimicro", API_ID, API_HASH)
    await client.connect()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.id, me.username)
        bot = await client.get_entity(BOT)
        peer = InputPeerUser(bot.id, bot.access_hash)
        await client.send_message(peer, "/start " + start if start else "/start")
        await asyncio.sleep(2)
        res = await client(RequestAppWebViewRequest(
            peer=peer,
            app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash), short_name=APP_SHORT),
            platform="android", start_param=start))
        frag = urlparse(res.url).fragment
        q = parse_qs(frag)
        initdata = q.get("tgWebAppData", [None])[0]
        if not initdata:
            initdata = parse_qs(urlparse(res.url).query).get("tgWebAppData", [None])[0]
        return initdata
    finally:
        await client.disconnect()

def main():
    if not API_ID or not API_HASH or not REF_LINK:
        print("Isi dulu API_ID, API_HASH, dan REF_LINK di bagian atas skrip.")
        sys.exit(1)
    import uuid
    initdata = asyncio.run(get_initdata())
    if not initdata:
        print("Gagal ambil initData dari Mini App.")
        sys.exit(1)
    me = api(FN_ME, {"initData": initdata, "fp": FP}, UA)
    if not isinstance(me, dict) or "result" not in me:
        print("Gagal login ke server Mini Micro:", json.dumps(me)[:300])
        sys.exit(1)
    m, s = me["result"]["me"], me["result"]["settings"]
    print("Saldo koin: %s (= $%.2f) | USDT: %s | Gift box: %s | Teman: %s" %
          (m["coins"], m["coins"] / s["coinRate"], m["usdt"], m["giftBoxes"], me["result"]["invited"]))
    print("Min WD: $%s | Gratis s.d. $%s tanpa deposit | Fee: %s" %
          (s["minWithdrawal"], s["freeWithdrawalCap"], s["feeValue"]))
    if m.get("banned"):
        print("Akun ini DIBLOKIR server:", m.get("banReason"))
        sys.exit(1)
    # Gift box gratis pertama (dan sisanya kalau ada)
    if m["giftBoxes"] > 0 or m.get("lastGiftAt") is None:
        g = api(FN_GIFT, {"initData": initdata, "requestId": str(uuid.uuid4())}, UA)
        print("Gift box:", json.dumps(g.get("result", g))[:200])
    # Tugas
    tl = api(FN_TASKS, {"initData": initdata}, UA)
    for t in (tl.get("result", {}).get("tasks") or []):
        c = api(FN_CLAIM_TASK, {"initData": initdata, "id": t["id"]}, UA)
        print("Tugas %s ($%s): %s" % (t.get("title"), t.get("reward"), json.dumps(c.get("result", c))[:200]))
    # Klaim mining
    cl = api(FN_CLAIM, {"initData": initdata, "requestId": str(uuid.uuid4())}, UA)
    print("Klaim mining:", json.dumps(cl.get("result", cl))[:200])
    me2 = api(FN_ME, {"initData": initdata, "fp": FP}, UA)
    m2, s2 = me2["result"]["me"], me2["result"]["settings"]
    print("Sesudah klaim — koin: %s | USDT: %s" % (m2["coins"], m2["usdt"]))
    # WD kalau sudah cukup
    free_left = max(0, s2["freeWithdrawalCap"] - m2["withdrawnOrPending"])
    cap = m2["usdt"] if m2["totalDeposit"] > 0 else min(m2["usdt"], free_left)
    if m2["usdt"] >= s2["minWithdrawal"] and cap >= s2["minWithdrawal"] and WD_ADDRESS.startswith("0x"):
        amount = int(cap * 10000) / 10000
        wd = api(FN_WITHDRAW, {"initData": initdata, "chain": "bsc", "asset": "USDT",
                               "address": WD_ADDRESS, "amount": amount}, UA)
        print("WD $%s ke %s: %s" % (amount, WD_ADDRESS, json.dumps(wd.get("result", wd))[:300]))
    else:
        print("Belum bisa WD (butuh USDT >= $%s; sekarang $%s). Mining lagi besok." %
              (s2["minWithdrawal"], m2["usdt"]))

if __name__ == "__main__":
    main()
