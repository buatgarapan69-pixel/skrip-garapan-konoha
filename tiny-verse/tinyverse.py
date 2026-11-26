#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TINY VERSE — skrip garapan buat orang lain (disanitasi).
Rawat galaksi 3D, panen stardust tiap 4-8 jam, kejar snapshot $TINY.

CARA PAKAI (Termux / Linux):
  1. pip install telethon requests
  2. Buat file config.txt di folder yang sama, isinya 2 baris:
       baris 1: API ID kamu (angka, dari https://my.telegram.org)
       baris 2: API HASH kamu
  3. Buat folder sessions/ di folder yang sama, taruh file .session
     kamu di dalamnya (1 file = 1 akun Telegram).
  4. Jalankan:  python3 tinyverse.py
     Pilih menu di dalam skrip (daftar + klaim / klaim harian).
  5. Saat diminta, paste LINK REFERRAL kamu sendiri, contoh:
       https://t.me/tverse?startapp=galaxy-KODEGALAXIMU
     (ambil dari dalam Mini App @tverse: menu Invites > copy link.
     Kalau kosong, akun tetap daftar TANPA referral — tetap jalan.)

YANG DILAKUKAN SKRIP (per akun):
  - Buka Mini App @tverse, login ke server TinyVerse
  - Buat galaksi pertama (gratis, dapat 1.000 stars)
  - Panen stardust yang sudah terkumpul (gratis)
  - Join channel @tvappchannel + grup @tverseapp (award community)
  - Tampilkan: member id, galaksi, stars, saldo stardust

CATATAN JUJUR (baca dulu):
  - Ini BUKAN WD instan. $TINY belum TGE; yang dikejar adalah
    snapshot Q4 2026 - Q1 2027 (55% supply untuk stargazer aktif).
    Belum ada yang terbukti cair — jangan harap duit cepat.
  - Referral: atribusi referral TinyVerse HANYA jalan kalau temanmu
    buka link referral LEWAT APLIKASI Telegram resmi (tap link
    startapp di HP). Lewat skrip/Telethon, referral TIDAK kehitung
    (sudah dibuktikan: 5 metode dicoba, invites tetap 0). Jadi
    sebar link referralmu ke orang beneran, jangan andalkan fleet.
  - GRATIS saja: skrip ini TIDAK top-up, TIDAK deposit, TIDAK
    hubungkan wallet berisi dana, TIDAK beli boost/stars.
  - 1 sesi Telethon = 1 akun, 1 IP. Jangan jalankan sesi yang sama
    dari 2 tempat/IP bersamaan — sesi bisa MATI permanen.

Dibuat oleh Tim Konoha — gratis, silakan dipakai & dibagikan.
Repo: https://github.com/buatgarapan69-pixel/skrip-garapan-konoha
"""

import asyncio
import glob
import hashlib
import json
import os
import random
import sys
import time
import uuid
from urllib.parse import parse_qs, urlparse

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest, StartBotRequest

BOT = "tverse"
BOT_ID = 7631205793
APP_URL = "https://app.tinyverse.pro/"
API = "https://api.tinyverse.pro"
SESSIONS_DIR = "sessions"
CONFIG_FILE = "config.txt"

DEVICES = ["SM-A546B", "Pixel 7", "Pixel 8", "SM-S918B", "RMX3700", "M2101K6G",
           "SM-G991B", "Pixel 6", "OnePlus 11", "SM-A536B", "Redmi Note 12",
           "SM-G998B", "Pixel 7a", "CPH2451", "SM-A715F", "Pixel 8 Pro",
           "2201117TG", "SM-S911B", "V2238", "Pixel 6a", "SM-A528B", "23127PN0CG"]
ANDROID_VERS = ["12", "13", "14", "13", "14", "12", "13", "14", "13", "12"]


def ua_for(name):
    rnd = random.Random(hashlib.sha256(name.encode()).hexdigest())
    dev = rnd.choice(DEVICES)
    av = rnd.choice(ANDROID_VERS)
    chrome = rnd.randint(118, 131)
    return (f"Mozilla/5.0 (Linux; Android {av}; {dev}) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{chrome}.0.0.0 Mobile Safari/537.36")


def device_id_for(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "tinyverse:" + name.lower()))


class TinyApi:
    """Klien HTTP ke api.tinyverse.pro (POST JSON, Bearer token)."""

    def __init__(self, name, my_ua=None):
        self.s = requests.Session()
        self.s.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": my_ua or ua_for(name),
            "X-Device-Id": device_id_for(name),
            "Referer": APP_URL,
            "Origin": "https://app.tinyverse.pro",
            "X-App-Version": "2.5.14",
        })

    def call(self, path, body=None):
        h = {"X-Request-Id": time.strftime("%H%M%S") + "-" + uuid.uuid4().hex[:12]}
        try:
            r = self.s.post(API + "/" + path, json=body or {}, headers=h, timeout=30)
            try:
                return r.status_code, r.json()
            except Exception:
                return r.status_code, {"_raw": r.text[:300]}
        except Exception as e:  # noqa: BLE001
            return 0, {"_error": f"{type(e).__name__}: {e}"}

    def set_token(self, token):
        self.s.headers["Authorization"] = "Bearer " + token


def unwrap(d):
    if isinstance(d, dict) and "response" in d:
        return d["response"]
    return d


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"File {CONFIG_FILE} tidak ditemukan.")
        print("Buat config.txt (2 baris): API ID, lalu API HASH.")
        print("API ID + API HASH diambil dari https://my.telegram.org")
        return None, None
    lines = [x.strip() for x in open(CONFIG_FILE, encoding="utf-8") if x.strip()]
    if len(lines) < 2:
        print("Isi config.txt kurang lengkap (butuh 2 baris).")
        return None, None
    try:
        return int(lines[0]), lines[1]
    except ValueError:
        print("Baris 1 config.txt harus angka (API ID).")
        return None, None


def parse_ref_link(text):
    """Ambil start_param dari link referral TinyVerse.

    Mendukung: https://t.me/tverse?startapp=galaxy-XXXX
    (link invite dari dalam Mini App) atau kode polos.
    """
    text = (text or "").strip()
    if not text:
        return None
    m = None
    import re
    m = re.search(r"startapp=([A-Za-z0-9_\-]+)", text)
    if m:
        return m.group(1)
    m = re.search(r"start=([A-Za-z0-9_\-]+)", text)
    if m:
        return m.group(1)
    if text.startswith("galaxy-"):
        return text
    return None


async def get_init_data(client, start_param):
    """Buka Mini App @tverse, kembalikan initData Telegram."""
    bot = await client.get_entity(BOT)
    if start_param:
        try:
            await client(StartBotRequest(bot=bot, peer=bot, start_param=start_param))
        except Exception:
            pass
        await asyncio.sleep(1)
        try:
            await client.send_message(bot, "/start " + start_param)
        except Exception:
            pass
        await asyncio.sleep(2)
    wv = await client(RequestWebViewRequest(
        peer=bot, bot=bot, platform="android",
        from_bot_menu=False, url=APP_URL,
        start_param=start_param or None))
    frag = urlparse(wv.url).fragment
    return parse_qs(frag).get("tgWebAppData", [None])[0]


async def process_session(api_id, api_hash, session_path, start_param, klaim_saja=False):
    name = os.path.splitext(os.path.basename(session_path))[0]
    res = {"sesi": name, "status": "?"}
    import shutil
    import tempfile
    tmp_base = os.path.join(tempfile.gettempdir(), f"tiny_share_{name}")
    tmp_file = tmp_base + ".session"
    shutil.copy2(session_path, tmp_file)
    client = TelegramClient(tmp_base, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            res["status"] = "SESI MATI (tidak login) — hapus / login ulang"
            await client.disconnect()
            return res
        me = await client.get_me()
        res["nama"] = f"{me.first_name or ''} (@{me.username})" if me.username else (me.first_name or str(me.id))
        res["telegram_id"] = me.id

        init = await get_init_data(client, start_param)
        if not init:
            res["status"] = "GAGAL: tidak dapat initData dari Mini App"
            return res

        # Join channel (best-effort, award community)
        for ch in ["tvappchannel", "tverseapp"]:
            try:
                ent = await client.get_entity(ch)
                await client(JoinChannelRequest(ent))
            except Exception:
                pass
            await asyncio.sleep(1)
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        try:
            os.unlink(tmp_file)
        except Exception:
            pass

    api = TinyApi(name)
    st, auth = await asyncio.to_thread(
        api.call, "auth/telegram/webapp", {"bot_id": BOT_ID, "data": init})
    if st != 200 or not isinstance(auth, dict) or "error" in auth:
        res["status"] = f"GAGAL: login server ditolak (HTTP {st}): {str(auth)[:120]}"
        return res
    prof = unwrap(auth)
    res["member_id"] = prof.get("member_id")
    res["ref_code"] = prof.get("ref_code")
    if prof.get("token"):
        api.set_token(prof["token"])
    st, d = await asyncio.to_thread(api.call, "user/info")
    info = unwrap(d)
    counter = (info or {}).get("counter") or {}
    if not counter.get("galaxy"):
        if klaim_saja:
            res["status"] = "BELUM PUNYA GALAKSI — jalankan menu 1 dulu"
            return res
        st, d = await asyncio.to_thread(api.call, "begin/create")
        bc = unwrap(d)
        if isinstance(bc, dict) and "error" in bc:
            res["status"] = f"GAGAL: begin/create ditolak: {str(bc)[:120]}"
            return res
        res["galaksi_baru"] = True
        await asyncio.sleep(1)
    st, d = await asyncio.to_thread(api.call, "collect/dust")
    cl = unwrap(d)
    if isinstance(cl, dict) and "error" in cl:
        res["klaim_dust"] = f"gagal: {str(cl)[:100]}"
    else:
        res["klaim_dust"] = cl.get("dust", 0) if isinstance(cl, dict) else cl
    await asyncio.sleep(1)
    st, d = await asyncio.to_thread(api.call, "user/info")
    fin = unwrap(d)
    res["galaksi"] = ((fin or {}).get("counter") or {}).get("galaxy")
    res["stars"] = ((fin or {}).get("counter") or {}).get("stars")
    res["stardust"] = ((fin or {}).get("wallet") or [{}])[0].get("value") if (fin or {}).get("wallet") else None
    res["status"] = "OK"
    return res


async def run_all(api_id, api_hash, start_param, klaim_saja):
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.session")))
    if not files:
        print(f'Tidak ada file .session di folder "{SESSIONS_DIR}/".')
        return
    print(f"Ditemukan {len(files)} sesi.")
    ok = 0
    for f in files:
        r = await process_session(api_id, api_hash, f, start_param, klaim_saja)
        print(f"[{r['sesi']}] {r['status']}", end="")
        if r["status"] == "OK":
            ok += 1
            print(f" | {r.get('nama')} | galaksi: {r.get('galaksi')} | "
                  f"stars: {r.get('stars')} | stardust: {r.get('stardust')} | "
                  f"klaim: {r.get('klaim_dust')}")
        else:
            print()
        await asyncio.sleep(2)
    print(f"\nBerhasil: {ok}/{len(files)} akun")
    print("Jalankan lagi tiap 4-8 jam buat panen stardust.")


def menu():
    api_id, api_hash = load_config()
    if not api_id:
        return
    print("=" * 55)
    print("  TINY VERSE — rawat galaksi, panen stardust ($TINY)")
    print("=" * 55)
    print("[1] Daftar + buat galaksi + klaim (semua sesi)")
    print("[2] Klaim dust harian saja (semua sesi)")
    print("[3] Keluar")
    pilih = input("➤ PILIH MENU » ").strip()
    if pilih == "1":
        ref = input("Paste link referral kamu (Enter = tanpa referral): ").strip()
        sp = parse_ref_link(ref)
        print("Kode referral:", sp or "(tanpa referral)")
        asyncio.run(run_all(api_id, api_hash, sp, klaim_saja=False))
    elif pilih == "2":
        asyncio.run(run_all(api_id, api_hash, None, klaim_saja=True))
    else:
        print("Keluar.")


if __name__ == "__main__":
    menu()
