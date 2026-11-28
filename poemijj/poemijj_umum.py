#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POEMIJJ (@poemijjbot, "Breguet-Mall") — skrip umum 1 akun (tugas harian gratis).
GRATIS, tanpa deposit, tanpa top-up. Buat dipakai orang lain.

CARA PAKAI (Termux / Linux):
  1. pip install telethon requests
  2. Isi API_ID dan API_HASH di bawah (dari https://my.telegram.org,
     login pakai akun Telegram kamu sendiri).
  3. Isi SESSION_NAME dengan nama file session Telethon kamu
     (mis. "akun_saya" -> file akun_saya.session di folder yang sama).
     Saat pertama jalan, Telethon minta login (nomor HP + kode OTP).
  4. Jalankan:  python3 poemijj_umum.py
  5. Skrip akan: buka @poemijjbot, ambil initData Mini App,
     login ke API, ambil tugas harian gratis VIP0 lalu selesaikan.
     Semua GRATIS. JANGAN deposit / beli VIP sebelum ada bukti WD.

YANG DILAKUKAN SKRIP (semua terverifikasi 28 Nov 2026):
  - Daftar gratis via bot, Mini App di niuke6ed.com.
  - VIP0 gratis: 1 tugas/hari, komisi $1 USDT per tugas.
  - Min WD 5 USDT via TRC20/BEP20/USDC/ETH (fee WD 14%).
  - Butuh ±5 hari grind gratis sampai min WD. Payout BELUM TERBUKTI.
  - VIP berbayar $9-$18888 (VIP1 $9 = $5/hari dst) — JANGAN beli
    sebelum ada bukti ada orang yang WD-nya landing.
  - Komisi referral HANYA dari deposit teman (10%/3%/1%),
    bukan dari tugas gratis teman.
  - Server kadang timeout — kalau gagal, coba lagi beberapa menit
    kemudian, JANGAN spam request.
  - JANGAN pakai banyak akun dari 1 IP: pakai 1 akun = 1 IP,
    atau proxy residensial beda per akun. Skrip ini untuk 1 akun saja.

REFERRAL (opsional, isi punyamu sendiri):
  Link ref kamu: https://t.me/poemijjbot?start=invite_code_<KODE_KAMU>
  Kode invite kamu ada di menu Invite di Mini App (6 huruf).
"""
import asyncio
import json
import sys
import urllib.parse

import requests

# ---- ISI PUNYAMU (jangan share file ini kalau sudah terisi) ----
API_ID = 0          # contoh: 12345678  (angka, dari my.telegram.org)
API_HASH = ""       # contoh: "abcdef..." (dari my.telegram.org)
SESSION_NAME = "akun_saya"   # tanpa .session
# -----------------------------------------------------------------

BOT = "poemijjbot"
WEBAPP_URL = "https://www.niuke6ed.com/?botname=poemijjbot#/"
BASE = "https://api.niuke6ed.com/api"
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")


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
        frag = urllib.parse.urlparse(r.url).fragment.lstrip("/").lstrip("?")
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        if not initdata:
            raise RuntimeError("initData tidak didapat dari WebView")
        return urllib.parse.unquote(initdata)
    finally:
        await client.disconnect()


def main():
    if not API_ID or not API_HASH:
        print("[!] Isi dulu API_ID dan API_HASH di dalam skrip (my.telegram.org).")
        sys.exit(1)
    initdata = asyncio.run(get_initdata())
    print(f"[+] initData didapat (panjang {len(initdata)})")

    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Origin": "https://www.niuke6ed.com",
                      "Referer": WEBAPP_URL, "Content-Type": "application/json"})
    r = s.post(BASE + "/user/tg",
               json={"init_data": initdata, "botname": "poemijjbot"}, timeout=30)
    lj = r.json()
    token = (lj.get("data") or {}).get("token")
    if not token:
        print("[!] Login gagal:", json.dumps(lj, ensure_ascii=False)[:300])
        sys.exit(1)
    print("[+] Login API OK")
    s.headers.update({"Authorization": "Bearer " + token})

    u = s.get(BASE + "/user/user_info", timeout=30).json().get("data", {})
    print(f"[+] State awal: level {u.get('level_name')}, "
          f"saldo komisi {u.get('brokerage_money')} USDT, "
          f"kode invite {u.get('invitation_code')}, "
          f"pendapatan/hari ${u.get('income')}")

    d = s.get(BASE + "/task/distribute", timeout=30).json()
    print("[+] Ambil tugas:", json.dumps(d, ensure_ascii=False)[:200])
    tl = s.get(BASE + "/task/list", timeout=30).json()
    tasks = tl.get("data", [])
    if tasks:
        tid = tasks[0]["id"]
        done = s.get(BASE + f"/task/do_task/{tid}", timeout=30).json()
        print("[+] Selesaikan tugas:", json.dumps(done, ensure_ascii=False)[:200])
    else:
        print("[+] Tidak ada tugas hari ini (mungkin sudah diklaim).")

    u2 = s.get(BASE + "/user/user_info", timeout=30).json().get("data", {})
    print(f"[+] State akhir: saldo komisi {u2.get('brokerage_money')} USDT")
    print("[+] Selesai. Jalankan lagi besok untuk tugas harian gratis.")
    print("[!] Ingat: min WD 5 USDT, fee 14%. JANGAN deposit sebelum payout terbukti.")


if __name__ == "__main__":
    main()
