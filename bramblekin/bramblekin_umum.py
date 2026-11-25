#!/usr/bin/env python3
"""BRAMBLEKIN — skrip umum (publik, tanpa kredensial).

Game mining BRAM di Telegram. Token BRAM sudah trade di STON.fi.
Gratis, tanpa deposit.
- Bot: @bramblekinbot
- Earn: Daily Coin 10 BRAM/hari + storage pasif ~10 BRAM/hari.
  Referral 5%/3%/1% (3 level).
- Min WD live: 3000 BRAM. Payout BELUM terbukti cair.
- Token: EQDwlhwuzUncNTLRxUtVUWsU1wQky43sbt72hn7m8LS_k-Nh (STON.fi)

CARA PAKAI — 1 PERINTAH:
  python3 bramblekin_umum.py
Lalu pilih menu di dalam:
  [1] Daftar pakai referral (opsional) + buka WebApp
  [2] Cek saldo + referral
  [3] Klaim Daily Coin + storage
  [4] Cek info Withdraw (min WD)
  [5] Keluar

KREDENSIAL (milikmu sendiri, TIDAK ada di skrip ini):
  1. Buka https://my.telegram.org -> API development tools -> buat app.
  2. Buat file apicred.json di folder yang sama, isinya:
     {"api_id": 12345678, "api_hash": "abc123..."}
  3. Jalankan skrip, masukkan nomor HP + kode login Telegram saat diminta.
  Sesi login tersimpan lokal (bramblekin_session.session) — JANGAN disebar.

REFERRAL (opsional):
  Isi REF_CODE di bawah dengan kode referral temanmu (tanpa awalan "ref_"),
  atau kosongkan "" untuk daftar tanpa referral. Link referral kamu sendiri
  muncul di menu [2] setelah daftar.

PENTING — VERIFIKASI WALLET (di HP, gratis, bukan deposit):
  Tap / tanam / kunjungi channel di dalam game saat ini butuh verifikasi
  wallet TonConnect (server balas 503 kalau belum terverifikasi).
  Caranya: buka WebApp BRAMBLEKIN di HP, ketuk "Connect Wallet", hubungkan
  wallet TON kamu (Tonkeeper) dan tanda tangani proof — gratis, TIDAK
  perlu kirim dana ke mana pun. Daily Coin + klaim storage jalan TANPA
  verifikasi wallet.

PERINGATAN: gratis 100%. Jangan pernah deposit (tugas "Pополнить"/top-up
5000/10000 BRAM = MODAL, jangan dikerjakan), jangan bayar verifikasi apa
pun, jangan hubungkan wallet berisi dana besar. Grind lambat: ~20 BRAM/hari,
min WD 3000 BRAM = ~150 hari tanpa referral. Satu perangkat = satu akun.
"""
import asyncio
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

try:
    from telethon import TelegramClient
    from telethon.tl.functions.messages import RequestAppWebViewRequest
    from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser
except ImportError:
    print("Telethon belum terpasang. Jalankan: pip install telethon")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
BOT = "bramblekinbot"
BASE = "https://bramblekin.icu"
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")
REF_CODE = ""  # isi kode referral temanmu kalau ada, contoh: "isi-kode-referral-temanmu"
SESSION = os.path.join(HERE, "bramblekin_session.session")


def load_creds():
    path = os.path.join(HERE, "apicred.json")
    if not os.path.exists(path):
        print("apicred.json tidak ada. Buat dulu (lihat docstring di atas).")
        sys.exit(1)
    with open(path) as f:
        c = json.load(f)
    return c["api_id"], c["api_hash"]


def api(path, initdata, body=None):
    req = urllib.request.Request(
        BASE + path, method="POST" if body is not None else "GET",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json",
                 "X-Telegram-Init-Data": initdata, "User-Agent": UA,
                 "Origin": "https://bramblekin.icu",
                 "Referer": "https://bramblekin.icu/"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}
    except Exception as e:
        return None, {"error": str(e)[:200]}


async def get_initdata():
    """Login Telegram (sekali), /start, lalu ambil initData WebApp."""
    api_id, api_hash = load_creds()
    client = TelegramClient(SESSION, api_id, api_hash)
    await client.start()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.username or me.first_name, "id:", me.id)
        bot = await client.get_entity(BOT)
        param = ("ref_" + REF_CODE) if REF_CODE else ""
        await client.send_message(bot, "/start " + param if param else "/start")
        await asyncio.sleep(5)
        r = await client(RequestAppWebViewRequest(
            peer=InputPeerUser(bot.id, bot.access_hash),
            app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash),
                                     short_name="bram"),
            platform="android"))
        frag = urllib.parse.urlparse(r.url).fragment
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        return urllib.parse.unquote(initdata)
    finally:
        await client.disconnect()


def menu():
    print()
    print("=== BRAMBLEKIN (gratis) ===")
    print("[1] Daftar + buka WebApp")
    print("[2] Cek saldo + referral")
    print("[3] Klaim Daily Coin + storage")
    print("[4] Cek info Withdraw (min WD)")
    print("[5] Keluar")
    return input("PILIH MENU » ").strip()


async def main():
    initdata = None
    while True:
        pilih = menu()
        if pilih == "5":
            print("Keluar.")
            break
        if pilih == "1":
            initdata = await get_initdata()
            st, s = api("/api/state", initdata)
            if st == 200:
                print("Saldo BRAM:", s.get("bram"), "| Daily rate:", s.get("daily_rate"))
                print("Link referral kamu:", s.get("ref_link"))
            else:
                print("Gagal ambil state:", st, s)
        elif pilih in ("2", "3", "4"):
            if not initdata:
                print("Pilih [1] dulu untuk login + ambil WebApp.")
                continue
            if pilih == "2":
                st, s = api("/api/state", initdata)
                if st == 200:
                    print("Saldo BRAM:", s.get("bram"), "| Storage:", s.get("storage"))
                    print("Level:", s.get("level"), "| Invited:", s.get("invited"))
                    print("Min WD:", s.get("withdraw_min"), "BRAM")
                    print("Link referral kamu:", s.get("ref_link"))
                    st2, ref = api("/api/referrals", initdata)
                    if st2 == 200:
                        for line in ref.get("lines", []):
                            print(f"  Level {line['level']}: {line['percent']}% — {line['players']} pemain")
                else:
                    print("Gagal:", st, s)
            elif pilih == "3":
                st, dc = api("/api/daily-coin", initdata, {})
                print("Daily Coin:", st, dc.get("amount", dc))
                st, cl = api("/api/claim", initdata, {})
                print("Klaim storage:", st, cl.get("amount", cl))
                st, s = api("/api/state", initdata)
                if st == 200:
                    print("Saldo BRAM sekarang:", s.get("bram"))
            elif pilih == "4":
                st, s = api("/api/state", initdata)
                if st == 200:
                    print("Saldo BRAM:", s.get("bram"))
                    print("Min WD:", s.get("withdraw_min"), "BRAM")
                    print("Wallet terhubung:", s.get("wallet_address") or "(belum)")
                    print("WD butuh alamat wallet TON + saldo >= min WD.")
                    print("Payout BELUM terbukti cair — jangan berharap cepat.")
                else:
                    print("Gagal:", st, s)
        else:
            print("Pilihan tidak dikenal.")


asyncio.run(main())
