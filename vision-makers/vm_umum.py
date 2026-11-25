#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISION MAKERS — skrip umum (untuk dipakai orang lain, 1 akun).
Gratis 100%: Mini App AITECH, kumpulin poin, boost peluang airdrop VMKS.
Tanpa deposit, tanpa wallet berisi dana, tanpa WD.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon requests
  2. Ambil API_ID + API_HASH di https://my.telegram.org/apps
  3. Isi bagian KONFIG di bawah (REF_CODE = kode referral pengundang,
     mis. ref_xxxx — boleh kosong, kalau kosong daftar tanpa ref)
  4. Jalankan:  python3 vm_umum.py
     - login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
     - skrip /start bot, join 2 channel tugas, daftar, klaim Daily Box,
       tap 10x, mulai tugas gratis, lalu tampilkan saldo + link referral kamu
  5. Klaim harian (Daily Box + tap):
       python3 vm_umum.py --claim

YANG DIDAPAT (hasil probe 25 Nov 2026):
  - Daily Box hari 1: +10.000 koin (naik tiap hari, hari 7 ada chest)
  - Tap Tap: 1 koin per tap, energi 300
  - Tugas: join TG + whitelist + follow X/Medium, masing-masing 5.000 koin
    (catatan: saat probe, klaim tugas balik 400 — reward belum masuk,
    kemungkinan butuh verifikasi server; daily + tap sudah terbukti masuk)
  - Undang teman: 5.000 koin per teman (terverifikasi masuk)
  - Level naik dari koin: bonus passive income + combo + energi

CATATAN:
  - File sesi (vm_umum.session) JANGAN dibagikan ke siapa pun.
  - Airdrop VMKS belum dibuka, Min WD BELUM ADA — payout BELUM TERBUKTI.
    Poin yang dikumpulin buat boost peluang airdrop.
  - Bonus referral 3% HANYA kalau referral kamu investasi di ICO Vision
    Makers — jangan ajak orang investasi kalau tidak paham risikonya.
  - Shop di dalam app jual Energy Cell berbayar (USDT/TON) — TIDAK WAJIB,
    jangan beli kalau cuma mau gratisan.
  - Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
"""

import argparse
import asyncio
import json
import sys
import time
import urllib.parse

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser

# ============================== KONFIG — ISI DULU ==============================
API_ID = 0          # <-- isi: angka dari https://my.telegram.org/apps
API_HASH = ""       # <-- isi: string dari https://my.telegram.org/apps
REF_CODE = ""       # <-- opsional: kode referral pengundang (mis. ref_xxxx), boleh kosong
# ===============================================================================

BOT = "AITech_Agents_bot"
BASE = "https://api.tapaitech.io"
UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36")
TASK_IDS = (23, 24, 67, 69)  # join TG, join chat, whitelist, Medium


def api_headers(initdata):
    return {"User-Agent": UA, "Content-Type": "application/json",
            "Accept": "application/json", "Origin": "https://app.tapaitech.io",
            "Referer": "https://app.tapaitech.io/", "InitData": initdata}


def call(method, path, headers, body=None):
    try:
        r = requests.request(method, BASE + path, headers=headers, json=body, timeout=30)
        try:
            return {"status": r.status_code, "body": r.json()}
        except Exception:
            return {"status": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"status": None, "error": "%s: %s" % (type(e).__name__, str(e)[:150])}


async def get_initdata():
    """Buka Mini App bot, ambil initData (bukti registrasi lewat Telegram)."""
    client = TelegramClient("vm_umum", API_ID, API_HASH)
    await client.start()
    try:
        me = await client.get_me()
        bot = await client.get_entity(BOT)
        start = "/start " + REF_CODE if REF_CODE else "/start"
        await client.send_message(bot, start)
        await asyncio.sleep(5)
        r = await client(RequestAppWebViewRequest(
            peer=InputPeerUser(bot.id, bot.access_hash),
            app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash),
                                     short_name="app"),
            platform="android", start_param=REF_CODE or None))
        frag = urllib.parse.urlparse(r.url).fragment
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        for ch in ("aitechagenthub", "AITECHAgentChat"):
            try:
                await client(JoinChannelRequest(await client.get_entity(ch)))
                print("[+] Join", ch)
            except Exception as e:
                print("[!] Join", ch, "gagal:", str(e)[:100])
            await asyncio.sleep(1)
        return me, initdata
    finally:
        await client.disconnect()


def do_claim(headers):
    out = {}
    d = call("POST", "/api/v1/users/registerlogin", headers, {})
    out["registerlogin"] = d.get("status")
    det = call("POST", "/api/v1/users/details", headers, {})
    if isinstance(det.get("body"), dict):
        out["inviteLink"] = det["body"].get("inviteLink")
        out["level"] = det["body"].get("level")
    day = call("GET", "/api/v1/dailyrewards", headers)
    day_id = None
    try:
        for wk in day["body"]["weeks"]:
            for dy in wk:
                if dy.get("status") == 1:
                    day_id = dy.get("dayId")
                    break
    except Exception:
        pass
    if day_id:
        out["daily_claim"] = call("POST", "/api/v1/dailyrewards/%d/claim" % day_id,
                                  headers, {}).get("status")
    else:
        out["daily_claim"] = "sudah diklaim / belum waktunya"
    out["tap"] = call("POST", "/api/v1/balance/increase", headers,
                      {"clicksAmount": 10}).get("status")
    for tid in TASK_IDS:
        call("POST", "/api/v1/tasks/%d/start" % tid, headers, {})
        time.sleep(1)
        out["task_%d_claim" % tid] = call(
            "POST", "/api/v1/tasks/%d/claim" % tid, headers, {}).get("status")
        time.sleep(1)
    bal = call("GET", "/api/v1/balance", headers)
    out["balance"] = bal.get("body")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", action="store_true", help="klaim harian saja")
    args = ap.parse_args()
    if not API_ID or not API_HASH:
        print("ISI DULU API_ID + API_HASH di bagian KONFIG (lihat atas file).")
        print("Ambil di https://my.telegram.org/apps")
        sys.exit(1)
    me, initdata = asyncio.run(get_initdata())
    if not initdata:
        print("Gagal ambil initData dari Mini App. Coba lagi.")
        sys.exit(1)
    print("[+] Login sebagai:", me.username, me.id)
    res = do_claim(api_headers(initdata))
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("Saldo koin:", (res.get("balance") or {}).get("coins"))
    if res.get("inviteLink"):
        print("Link referral kamu:", res["inviteLink"])


if __name__ == "__main__":
    main()
