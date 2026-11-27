#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FEEDTON (@FEEDonTONbot) — GRAM CITIZEN card + poin FISH (1 akun, gratis).
Alur: /start + WebView initData -> auth -> terbitkan kartu citizen ->
klaim check-in/misi/box/kode harian -> spin semua -> poin FISH.
GRATIS saja: tanpa deposit, tanpa top-up, tanpa connect wallet berisi dana.

CARA PAKAI (Termux / Linux):
  pip install telethon requests
  1. Isi API_ID + API_HASH di bawah (dari https://my.telegram.org/apps).
  2. (Opsional) isi REF_CODE dengan kode invite temanmu (tanpa prefix "r_").
     Kosongkan kalau daftar tanpa ref.
  3. python3 feedton.py  ->  pilih menu, login Telegram sekali (kode OTP).
  4. Sesi tersimpan di feedton.session (JANGAN dibagikan ke siapa pun).

JUJUR: payout BELUM TERBUKTI. Poin FISH jadi bagian pool $FISH
(~$129rb, tutup 31 Des 2026); reward $FISH dikirim ke wallet TON yang
dihubungkan — connect wallet HANYA dari HP sendiri, jangan di script ini.
Batas harian: 50 spin, 250/minggu. Spin tidak bisa dibeli.
"""
import asyncio
import json
import os
import random
import secrets
import sys
import urllib.parse
import uuid

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.types import InputPeerUser, InputUser

# ============ ISI SENDIRI (jangan pakai punya orang lain) ============
API_ID = 0          # <-- isi API ID dari my.telegram.org (angka)
API_HASH = ""       # <-- isi API HASH dari my.telegram.org
REF_CODE = ""       # <-- kode invite teman (contoh: "KODE-TEMANMU"), kosong = tanpa ref
# Proxy opsional (format http://user:pass@host:port), kosong = direct:
PROXY = os.environ.get("FEEDTON_PROXY", "")
# =====================================================================

BOT = "FEEDonTONbot"
APP_URL = "https://app.tonfeed.fun/"
BASE = "https://app.tonfeed.fun"
CHANNELS = ["tonfish_tg", "tonfish_en"]
SESSION = "feedton.session"

DEVICES = [
    ("SM-S918B", "14"), ("SM-A546E", "14"), ("SM-G998B", "13"), ("Pixel 7", "14"),
    ("Pixel 8 Pro", "14"), ("Pixel 6", "13"), ("Redmi Note 12", "13"),
    ("Redmi Note 13 Pro", "14"), ("POCO X5 Pro", "13"), ("POCO F5", "14"),
    ("OPPO Reno10", "13"), ("vivo V29", "14"), ("Infinix Note 30", "13"),
    ("Samsung Galaxy A54", "14"), ("Realme 11 Pro", "13"), ("OnePlus Nord 3", "14"),
]

R = "\033[91m"; RED = "\033[38;5;196m"; Y = "\033[93m"; G = "\033[92m"
C = "\033[96m"; W = "\033[97m"; GRAY = "\033[90m"; RESET = "\033[0m"


def ua_for(name):
    r = random.Random("feedton-ua-" + name)
    dev, ver = r.choice(DEVICES)
    chrome = r.randint(118, 131)
    build = "%s Build/%s.%06d.%03d" % (dev, r.choice(["TP1A", "UP1A", "SP1A", "TQ3A"]),
                                      r.randint(100000, 999999), r.randint(1, 99))
    return ("Mozilla/5.0 (Linux; Android %s; %s) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/%d.0.0.0 Mobile Safari/537.36" % (ver, build, chrome))


def proxies():
    return {"https": PROXY, "http": PROXY} if PROXY else None


def banner():
    os.system("clear")
    print(RED + "═" * 60 + RESET)
    print(W + "  ☠ FEEDTON — GRAM CITIZEN ☠".center(60) + RESET)
    print(GRAY + "  Kartu citizen + poin FISH (gratis)".center(60) + RESET)
    print(RED + "═" * 60 + RESET)


class Feed:
    def __init__(self, initdata, ua, device_id):
        self.initdata = initdata
        self.ua = ua
        self.device_id = device_id
        self.sess = None

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = requests.Request(method, BASE + path, data=data)
        prepped = req.prepare()
        prepped.headers.update({
            "Content-Type": "application/json", "User-Agent": self.ua,
            "Accept": "application/json", "Origin": BASE, "Referer": BASE + "/",
            "X-Device-Id": self.device_id})
        if self.sess:
            prepped.headers["Authorization"] = "Bearer " + self.sess
        if method != "GET":
            prepped.headers["x-telegram-init-data"] = self.initdata
        for attempt in range(3):
            try:
                r = requests.Session().send(prepped, proxies=proxies(), timeout=30)
                try:
                    return r.status_code, r.json()
                except Exception:
                    return r.status_code, {"raw": r.text[:500]}
            except Exception as e:
                if attempt == 2:
                    return None, {"error": repr(e)[:200]}
                import time; time.sleep(4)

    def auth(self):
        body = {"initData": self.initdata}
        if REF_CODE:
            body["ref"] = REF_CODE
        st, r = self.call("POST", "/api/auth", body)
        if isinstance(r, dict) and r.get("session"):
            self.sess = r["session"]
            return True, r
        return False, r

    def issue(self):
        h = {"Content-Type": "application/json", "User-Agent": self.ua,
             "Accept": "application/json", "Origin": BASE, "Referer": BASE + "/",
             "Authorization": "Bearer " + self.sess,
             "x-telegram-init-data": self.initdata, "X-Device-Id": self.device_id}
        rr = requests.post(BASE + "/api/citizen?action=issue", json={},
                           headers=h, proxies=proxies(), timeout=120)
        dec = json.JSONDecoder()
        raw, idx, card = rr.text, 0, None
        while idx < len(raw):
            while idx < len(raw) and raw[idx] in " \n\r\t":
                idx += 1
            if idx >= len(raw):
                break
            try:
                obj, end = dec.raw_decode(raw, idx)
                idx = end
                if isinstance(obj, dict) and obj.get("type") == "result":
                    card = obj.get("card")
            except Exception:
                break
        return rr.status_code, card

    def claim_all(self):
        claims = [
            ("check-in", {"kind": "checkin"}),
            ("free-spin", {"kind": "free_spin"}),
            ("spin-piece", {"kind": "piece"}),
            ("tugas kartu", {"kind": "task", "item": "card"}),
            ("tugas channel", {"kind": "task", "item": "channel"}),
            ("tugas grup", {"kind": "task", "item": "group"}),
            ("misi visit today", {"kind": "mission", "item": "visit:today"}),
            ("misi visit feed", {"kind": "mission", "item": "visit:feed"}),
            ("misi visit me", {"kind": "mission", "item": "visit:me"}),
            ("umur akun TG", {"kind": "history", "item": "telegram_age"}),
            ("mystery box", {"kind": "box"}),
        ]
        out = {}
        for label, body in claims:
            st, r = self.call("POST", "/api/feed-tab?action=claim", body)
            ok = isinstance(r, dict) and r.get("ok")
            out[label] = {"ok": ok, "granted": (r or {}).get("granted"),
                          "state": (r or {}).get("state")}
            print(("  " + G + "✓ " if ok else "  " + R + "✕ ") + label +
                  (" +" + str(((r or {}).get("granted") or {}).get("spins", 0)) + " spin"
                   if ok else " (" + str((r or {}).get("state")) + ")") + RESET)
        return out

    def state(self):
        st, r = self.call("GET", "/api/feed-tab")
        return r if isinstance(r, dict) else {}

    def redeem_own_code(self):
        ft = self.state()
        for o in (ft.get("codes") or {}).get("own") or []:
            if o.get("unlocked") and o.get("code") and not o.get("claimed"):
                st, r = self.call("POST", "/api/feed-tab?action=redeem", {"code": o["code"]})
                print("  kode sendiri %s: %s" % (o["code"], (r or {}).get("granted")))
                return o["code"], r
        return None, None

    def spin_all(self):
        ft = self.state()
        spins = (ft.get("balance") or {}).get("spins", 0)
        if not spins:
            print(Y + "  Tidak ada spin." + RESET)
            return 0
        st, r = self.call("POST", "/api/feed-tab?action=spin",
                          {"count": spins, "nonce": secrets.token_hex(16)})
        pts = (r or {}).get("points", 0) if isinstance(r, dict) else 0
        print(G + "  Spin x%d -> +%d poin" % (spins, pts) + RESET)
        return pts


async def get_initdata(client, me):
    bot = await client.get_entity(BOT)
    start = "/start r_" + REF_CODE if REF_CODE else "/start"
    await client.send_message(bot, start)
    await asyncio.sleep(3)
    r = await client(RequestWebViewRequest(
        peer=InputPeerUser(bot.id, bot.access_hash),
        bot=InputUser(bot.id, bot.access_hash), platform="android",
        from_bot_menu=True, url=APP_URL,
        start_param=("r_" + REF_CODE) if REF_CODE else None))
    frag = urllib.parse.urlparse(r.url).fragment
    return urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]


async def join_channels(client):
    for ch in CHANNELS:
        try:
            ent = await client.get_entity(ch)
            await client(JoinChannelRequest(ent))
            print(G + "  ✓ Join @" + ch + RESET)
        except Exception as e:
            print(Y + "  ! Join @" + ch + " gagal: " + str(e)[:80] + RESET)
        await asyncio.sleep(1)


async def run_all():
    if not API_ID or not API_HASH:
        print(R + "Isi dulu API_ID + API_HASH di file ini (my.telegram.org)." + RESET)
        return
    client = TelegramClient(SESSION, int(API_ID), str(API_HASH))
    await client.start()
    try:
        me = await client.get_me()
        print(G + "Login sebagai: @" + (me.username or str(me.id)) + RESET)
        initdata = await get_initdata(client, me)
        if not initdata:
            print(R + "Gagal ambil initData WebView." + RESET)
            return
        await join_channels(client)
    finally:
        await client.disconnect()
    name = me.username or str(me.id)
    feed = Feed(initdata, ua_for(name), str(uuid.uuid5(uuid.NAMESPACE_DNS, "feedton-" + name.lower())))
    ok, auth = feed.auth()
    if not ok:
        print(R + "Auth gagal: " + json.dumps(auth, ensure_ascii=False)[:300] + RESET)
        return
    print(G + "Auth OK." + RESET)
    st, card = feed.issue()
    if not card:
        print(R + "Terbitkan kartu gagal (status %s)." % st + RESET)
        return
    print(G + "Kartu citizen #%(number)s terbit. Kode invite kamu: %(code)s" % card + RESET)
    print("Link ref kamu: https://t.me/FEEDonTONbot?startapp=r_" + card["code"])
    print(C + "\n[1] Klaim check-in + misi + box:" + RESET)
    feed.claim_all()
    feed.redeem_own_code()
    print(C + "\n[2] Spin semua:" + RESET)
    feed.spin_all()
    ft = feed.state()
    print(W + "\nSaldo: %s" % json.dumps(ft.get("balance"), ensure_ascii=False) + RESET)
    print(W + "Pool: %s" % json.dumps(ft.get("pool"), ensure_ascii=False)[:200] + RESET)
    print(GRAY + "Ingat: reward $FISH baru dibagi habis pool tutup (31 Des 2026),\n"
          "butuh connect wallet TON dari HP sendiri." + RESET)


def menu():
    while True:
        banner()
        print(R + "[01]" + RESET + W + " Jalankan FEEDTON (daftar + klaim + spin)" + RESET)
        print(R + "[02]" + RESET + W + " Keluar" + RESET)
        print(GRAY + "─" * 60 + RESET)
        try:
            p = input(G + "➤ PILIH MENU » " + RESET).strip()
        except KeyboardInterrupt:
            print("\n" + Y + "Batal." + RESET)
            break
        if p in ("1", "01"):
            asyncio.run(run_all())
            input("\nTekan Enter untuk kembali...")
        elif p in ("2", "02"):
            print(Y + "Keluar." + RESET)
            break
        else:
            print(R + "Pilihan tidak dikenal." + RESET)


if __name__ == "__main__":
    menu()
