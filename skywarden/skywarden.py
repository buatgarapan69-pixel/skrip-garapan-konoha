#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKYWARDEN (@SkywardenxBot) — skrip umum 1 akun (bukan fleet).
Mining app TON: buka kapal, mining SKYW, klaim tugas, collect harian.
GRATIS: tanpa deposit, tanpa top-up. WD butuh wallet TON + aktivasi
0,062 GRAM sekali (bayar dari wallet kamu sendiri, BUKAN dari skrip).

CARA PAKAI (Termux):
  1. pip install telethon
  2. Ambil API_ID + API_HASH di https://my.telegram.org
  3. Isi API_ID / API_HASH di bawah (atau export env SKY_API_ID,
     SKY_API_HASH), lalu:  python3 skywarden.py
  4. Pilih menu di dalam skrip. Sesi Telegram tersimpan lokal
     sebagai skywarden_akun.session — JANGAN dibagikan ke siapa pun.

REFERRAL: kalau daftar lewat link teman, isi REF_CODE dengan kode
ref_... dari linknya (contoh: ref_abc123). Kosongkan kalau tidak ada.
Link referral KAMU akan tampil di menu (buat dibagikan ke teman).

Perhatian: payout BELUM TERBUKTI oleh kami (channel proyek klaim ada
payout). Min WD 500 SKYW = 0,5 GRAM (TON), WD dikonfirmasi admin.
Jangan deposit/top-up kalau belum yakin.
"""
import asyncio
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputUser

BOT_USERNAME = "SkywardenxBot"
WEBAPP_URL = "https://skywarden-game.icu/"
ORIGIN = "https://skywarden-game.icu"
CHANNEL = "skywardenchannel"
CHAT = "skywardenchat"

API_ID = int(os.environ.get("SKY_API_ID", "0") or 0)
API_HASH = os.environ.get("SKY_API_HASH", "")
SESSION_NAME = os.environ.get("SKY_SESSION", "skywarden_akun")
REF_CODE = os.environ.get("SKY_REF_CODE", "")  # contoh: ref_abc123, kosong = tanpa ref

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")


def http_get(url, headers, timeout=30):
    req = urllib.request.Request(url, headers=headers, method="GET")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:2000]
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def http_post(url, payload, headers, timeout=30):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:2000]
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


class Sky:
    def __init__(self):
        self.client = None
        self.init_data = None
        self.device_id = str(uuid.uuid4())
        self.headers = None

    async def connect(self):
        if not API_ID or not API_HASH:
            print("ISI DULU API_ID + API_HASH (lihat komentar di atas skrip).")
            return False
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await self.client.connect()
        if not await self.client.is_user_authorized():
            print("Login dulu: kirim kode OTP yang masuk ke Telegram kamu.")
            phone = input("Nomor HP (cth +62xxx): ").strip()
            await self.client.send_code_request(phone)
            code = input("Kode OTP: ").strip()
            try:
                await self.client.sign_in(phone, code)
            except Exception as e:
                print("Login gagal:", e)
                return False
        me = await self.client.get_me()
        print(f"Login sebagai @{me.username} (id {me.id})")
        return True

    async def open_app(self):
        """Buka Mini App + ambil initData (dipakai sebagai auth API)."""
        bot = await self.client.get_entity(BOT_USERNAME)
        kwargs = dict(peer=bot,
                      app=InputBotAppShortName(
                          bot_id=InputUser(bot.id, bot.access_hash),
                          short_name="sky"),
                      platform="android")
        if REF_CODE:
            kwargs["start_param"] = REF_CODE
        res = await self.client(RequestAppWebViewRequest(**kwargs))
        frag = urllib.parse.urlparse(res.url).fragment
        data = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        if not data:
            print("Gagal ambil initData dari WebApp.")
            return False
        # Pakai apa adanya (percent-encoded) — aman untuk header HTTP.
        self.init_data = data
        self.headers = {"User-Agent": UA, "X-Device-Id": self.device_id,
                        "Content-Type": "application/json",
                        "X-Telegram-Init-Data": self.init_data,
                        "Origin": ORIGIN, "Referer": ORIGIN + "/"}
        return True

    def api_get(self, path):
        return http_get(ORIGIN + path, self.headers)

    def api_post(self, path, payload):
        p = dict(payload)
        p["idempotency_key"] = str(uuid.uuid4())
        return http_post(ORIGIN + path, p, self.headers)

    async def join_communities(self):
        for ch in (CHANNEL, CHAT):
            try:
                ent = await self.client.get_entity(ch)
                await self.client(JoinChannelRequest(ent))
                print(f"Join @{ch}: OK")
            except Exception as e:
                print(f"Join @{ch}: gagal ({e})")
            await asyncio.sleep(1)

    def do_tasks(self):
        """Mark + claim tugas channel/chat, lalu klaim task referral yg ready."""
        for kind in ("channel", "chat"):
            st, _ = self.api_post("/api/tasks/mark", {"kind": kind})
            print(f"Tugas {kind}: mark {st}")
            asyncio.sleep(1)
        st, rb = self.api_get("/api/tasks")
        if st != 200:
            print("Gagal baca daftar tugas:", st)
            return
        try:
            tasks = json.loads(rb).get("tasks", [])
        except Exception:
            tasks = []
        for tk in tasks:
            if tk.get("status") == 1:
                st2, rb2 = self.api_post("/api/tasks/claim", {"kind": tk["kind"]})
                try:
                    reward = json.loads(rb2).get("reward", "?")
                except Exception:
                    reward = "?"
                print(f"Klaim {tk['kind']}: {st2} (+{reward} SKYW)")
                asyncio.sleep(1)

    def state(self):
        st, rb = self.api_get("/api/state")
        if st != 200:
            print("Gagal baca state:", st, (rb or "")[:200])
            return None
        try:
            s = json.loads(rb)
        except Exception:
            print("State tidak bisa dibaca.")
            return None
        print(f"SKYW: {s.get('skyw')} (spend-only: {s.get('spend_only_skyw')}, "
              f"bisa WD: {s.get('withdrawable_skyw')})")
        print(f"Mining: {s.get('rate_day')} SKYW/hari, kapal dibuka: "
              f"{s.get('ships_opened')}/{s.get('ships_total')}")
        print(f"Min WD: 500 SKYW = 0,5 GRAM. Link referral kamu:")
        print(f"  {s.get('ref_link')}")
        print(f"Teman diundang: {s.get('invited')}")
        return s

    def buy_first_ship(self):
        s = self.state()
        if not s:
            return
        ship1 = s["ships"][0]
        if ship1.get("opened"):
            print("Kapal 1 sudah dibuka.")
            return
        if s.get("spend_only_skyw", 0) < 1000:
            print(f"SKYW spend-only {s.get('spend_only_skyw')} < 1000, "
                  "belum bisa beli kapal 1. Kerjakan tugas + undang teman dulu.")
            return
        st, rb = self.api_post("/api/ship/buy",
                               {"ship_id": 1, "expected_step": -1,
                                "expected_quantity": 0})
        print("Beli kapal 1:", st, (rb or "")[:200])

    def collect(self):
        st, rb = self.api_post("/api/collect", {})
        try:
            gain = json.loads(rb).get("gain", "?")
        except Exception:
            gain = "?"
        print(f"Collect mining: {st} (dapat +{gain} SKYW)")

    async def close(self):
        if self.client:
            await self.client.disconnect()


def menu():
    print("=" * 40)
    print("SKYWARDEN — 1 akun")
    print("=" * 40)
    print("[1] Daftar + kerjakan tugas (channel/chat)")
    print("[2] Klaim task referral yg ready")
    print("[3] Beli kapal pertama (1.000 SKYW)")
    print("[4] Collect hasil mining")
    print("[5] Cek saldo + link referral")
    print("[6] Semua langkah (1-5) sekaligus")
    print("[0] Keluar")
    return input("PILIH MENU » ").strip()


async def main():
    sky = Sky()
    if not await sky.connect():
        return
    if not await sky.open_app():
        await sky.close()
        return
    while True:
        pilih = menu()
        if pilih == "0":
            break
        elif pilih == "1":
            await sky.join_communities()
            sky.do_tasks()
        elif pilih == "2":
            sky.do_tasks()
        elif pilih == "3":
            sky.buy_first_ship()
        elif pilih == "4":
            sky.collect()
        elif pilih == "5":
            sky.state()
        elif pilih == "6":
            await sky.join_communities()
            sky.do_tasks()
            sky.buy_first_ship()
            sky.collect()
            sky.state()
        else:
            print("Pilihan tidak ada.")
    await sky.close()
    print("Selesai.")


if __name__ == "__main__":
    asyncio.run(main())
