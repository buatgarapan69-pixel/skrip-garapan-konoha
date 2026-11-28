#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRADORA (@TradoraTopbot) — skrip umum 1 akun (check-in + spin + claim).
GRATIS, tanpa deposit, tanpa top-up. Buat dipakai orang lain.

CARA PAKAI (Termux / Linux):
  1. pip install telethon
  2. Isi API_ID dan API_HASH di bawah (dari https://my.telegram.org,
     login pakai akun Telegram kamu sendiri).
  3. Isi SESSION_NAME dengan nama file session Telethon kamu
     (mis. "akun_saya" -> file akun_saya.session di folder yang sama).
     Saat pertama jalan, Telethon minta login (nomor HP + kode OTP).
  4. Jalankan:  python3 tradora_umum.py
  5. Skrip akan: buka @TradoraTopbot, ambil initData Mini App,
     lalu check-in harian + spin 3x + claim profit mining.
     Semua GRATIS. JANGAN deposit / beli TA sebelum ada bukti WD.

YANG DILAKUKAN SKRIP (semua terverifikasi 28 Nov 2026):
  - Daftar gratis: dapat 100 TA starter, mining $0,02/hari.
  - Check-in harian: hari 1 +2 TA, hari 2 +0,001 USDT, hari 3+ +1 TA.
  - Spin harian 3x: hadiah USDT/TA (spin 1: 0,01 USDT, spin 2: 10 TA).
  - Claim: pindahkan profit mining ke saldo USDT.
  - Min WD 0,1 USDT via BSC (BEP20). WD mode MANUAL (bukan instan).
  - Butuh ±4-5 hari grind gratis sampai min WD. Payout BELUM TERBUKTI.
  - Server Mini App kadang down (500/502) — kalau gagal, coba lagi
    beberapa menit kemudian, JANGAN spam request.
  - JANGAN pakai banyak akun dari 1 IP: server mendeteksi multi-akun
    (akun kena flag = tombol claim disembunyikan). 1 akun = 1 IP.

REFERRAL (opsional, isi punyamu sendiri):
  Link ref kamu: https://t.me/TradoraTopbot?start=ref_<ID_TELEGRAM_KAMU>
  Reward: +3 TA tiap teman + 10% komisi dari pembelian tim.
"""
import asyncio
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

# ---- ISI PUNYAMU (jangan share file ini kalau sudah terisi) ----
API_ID = 0          # contoh: 12345678  (angka, dari my.telegram.org)
API_HASH = ""       # contoh: "abcdef..." (dari my.telegram.org)
SESSION_NAME = "akun_saya"   # tanpa .session
# -----------------------------------------------------------------

BOT = "TradoraTopbot"
WEBAPP_URL = "https://jt5vtqx8qqy0lcur6amhpm0l.179.197.255.88.sslip.io/"
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")


def api(method, path, initdata, body=None):
    url = WEBAPP_URL.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-Tg-Init-Data", initdata)
    req.add_header("User-Agent", UA)
    req.add_header("Content-Type", "application/json")
    req.add_header("Referer", WEBAPP_URL)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"status": r.status, "body": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode()[:300]}
    except Exception as e:
        return {"error": repr(e)}


async def get_initdata():
    from telethon import TelegramClient
    from telethon.tl.functions.messages import RequestWebViewRequest
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    try:
        me = await client.get_me()
        print(f"[+] Login sebagai: {me.first_name} (@{me.username}, id {me.id})")
        bot = await client.get_entity(BOT)
        r = await client(RequestWebViewRequest(peer=bot, bot=bot,
                                               platform="android",
                                               from_bot_menu=False,
                                               url=WEBAPP_URL))
        frag = urllib.parse.urlparse(r.url).fragment
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        if not initdata:
            raise RuntimeError("initData tidak didapat dari WebView")
        return urllib.parse.unquote(initdata), str(me.id)
    finally:
        await client.disconnect()


def main():
    if not API_ID or not API_HASH:
        print("[!] Isi dulu API_ID dan API_HASH di dalam skrip (my.telegram.org).")
        sys.exit(1)
    initdata, uid = asyncio.run(get_initdata())
    print(f"[+] initData didapat (panjang {len(initdata)})")

    u = api("GET", f"/api/user/{uid}", initdata)
    user = (u.get("body") or {}).get("user")
    if not user:
        print("[!] Gagal baca state user:", json.dumps(u, ensure_ascii=False)[:300])
        print("    Server mungkin lagi down — coba lagi beberapa menit lagi.")
        sys.exit(1)
    print(f"[+] State awal: {user['taBalance']} TA, "
          f"{user['usdtBalance']} USDT, mining ${user['dailyEarnings']}/hari, "
          f"spin tersisa {user['drawAttempts']}, "
          f"multi-akun={user['isMultiAccount']}, banned={user['isBanned']}")
    if user["isMultiAccount"] or user["isBanned"]:
        print("[!] Akun kena flag multi-akun/banned — berhenti, jangan lanjut.")
        sys.exit(1)

    c = api("POST", f"/api/user/{uid}/checkin", initdata)
    print("[+] Check-in:", json.dumps(c.get("body") or c, ensure_ascii=False)[:200])

    for i in (1, 2, 3):
        s = api("POST", f"/api/user/{uid}/spin", initdata)
        b = s.get("body") or {}
        print(f"[+] Spin {i}:", b.get("label") or json.dumps(s, ensure_ascii=False)[:200])
        if not b.get("ok"):
            break

    cl = api("POST", f"/api/user/{uid}/claim", initdata)
    print("[+] Claim:", json.dumps(cl.get("body") or cl, ensure_ascii=False)[:200])

    u2 = api("GET", f"/api/user/{uid}", initdata)
    user2 = (u2.get("body") or {}).get("user") or {}
    print(f"[+] State akhir: {user2.get('taBalance')} TA, "
          f"{user2.get('usdtBalance')} USDT, "
          f"spin tersisa {user2.get('drawAttempts')}")
    print("[+] Selesai. Jalankan lagi besok untuk check-in + spin harian.")


if __name__ == "__main__":
    main()
