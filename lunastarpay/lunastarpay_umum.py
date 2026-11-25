#!/usr/bin/env python3
"""LUNA STAR PAY BOT — skrip umum (publik, tanpa kredensial).

Bot Telegram penghasil Stars: referral + daily bonus. Gratis, tanpa deposit.
- Bot: @LUNASTARPAYBOT
- Earn: +4 Stars tiap teman join pakai link kamu. Daily Bonus tiap 24 jam.
- Min WD live: 25 Stars (max 1000). Payout BELUM terbukti cair.
- Server klaim 162 user, 75 Stars payout (tanpa bukti on-chain).

CARA PAKAI — 1 PERINTAH:
  python3 lunastarpay_umum.py
Lalu pilih menu di dalam:
  [1] Daftar + join 12 channel + ambil link verifikasi
  [2] Cek saldo + referral
  [3] Klaim Daily Bonus
  [4] Cek info Withdraw (min WD)
  [5] Keluar

PENTING — VERIFIKASI WAJIB DI HP:
  Setelah daftar + join channel, bot minta verifikasi Turnstile.
  Verifikasi TIDAK bisa lewat skrip/VPS — buka @LUNASTARPAYBOT di HP,
  ketuk "Start Verification", selesaikan Turnstile di webview Telegram.
  Setelah itu menu bot kebuka dan skrip ini bisa cek saldo/klaim bonus.

KREDENSIAL (milikmu sendiri, TIDAK ada di skrip ini):
  1. Buka https://my.telegram.org -> API development tools -> buat app.
  2. Buat file apicred.json di folder yang sama, isinya:
     {"api_id": 12345678, "api_hash": "abc123..."}
  3. Jalankan skrip, masukkan nomor HP + kode login Telegram saat diminta.
  Sesi login tersimpan lokal (luna_session.session) — JANGAN disebar.

PERINGATAN: gratis 100%. Jangan pernah deposit, jangan bayar verifikasi
apa pun, jangan hubungkan wallet berisi dana. Satu perangkat = satu akun
(bot memakai fingerprint perangkat — multi-akun dari 1 perangkat berisiko
di-flag). Jangan pakai VPN/proxy saat verifikasi.
"""
import asyncio
import json
import os
import sys
import time

try:
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError
    from telethon.tl.functions.channels import JoinChannelRequest
except ImportError:
    print("Telethon belum terpasang. Jalankan: pip install telethon")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
BOT = "LUNASTARPAYBOT"
REF_CODE = ""  # isi kode referral temanmu kalau ada (angka user id Telegram).
# Contoh: REF_CODE = "7590298679" -> daftar pakai link t.me/LUNASTARPAYBOT?start=7590298679
GATES = ["Royaltaskrpro", "Tushar_Xpe", "QuickGigsBd", "ROYALPROSH",
         "movienzone69x", "khgfxz99txbnmbvx57i", "SEELORA_X_OFFCIAL",
         "Refer_to_Refer_0", "MsNusrat112", "bd_earning_hub1",
         "USDT_LIVE_PAY", "AMIR_PRO_CRIPTO"]


def load_creds():
    p = os.path.join(HERE, "apicred.json")
    if not os.path.exists(p):
        print("apicred.json belum ada. Buat dulu (lihat docstring di atas):")
        print('  {"api_id": 12345678, "api_hash": "abc123..."}')
        print("api_id/api_hash didapat dari https://my.telegram.org")
        return None
    d = json.load(open(p))
    return d["api_id"], d["api_hash"]


async def get_client():
    creds = load_creds()
    if not creds:
        return None
    api_id, api_hash = creds
    sess = os.path.join(HERE, "luna_session")
    client = TelegramClient(sess, api_id, api_hash)
    await client.start()
    me = await client.get_me()
    print("Login sebagai: %s (@%s, id %s)" % (me.first_name, me.username, me.id))
    return client


async def read_bot_msgs(client, bot, limit=4):
    out = []
    async for m in client.iter_messages(bot, limit=limit):
        out.append(m)
    out.reverse()
    for m in out:
        print("---- %s ----" % m.id)
        print(m.message or "")
    return out


async def cmd_daftar():
    client = await get_client()
    if not client:
        return
    bot = await client.get_entity(BOT)
    start = "/start " + REF_CODE if REF_CODE else "/start"
    await client.send_message(bot, start)
    await asyncio.sleep(5)
    print("Bot menjawab:")
    await read_bot_msgs(client, bot, 3)
    print("\nJoin 12 channel gate (tunggu FloodWait kalau muncul)...")
    for u in GATES:
        try:
            ent = await client.get_entity(u)
            await client(JoinChannelRequest(ent))
            print("  join @%s OK" % u)
        except FloodWaitError as e:
            print("  @%s FloodWait %s detik — tidur..." % (u, e.seconds))
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            print("  @%s gagal: %s" % (u, type(e).__name__))
        await asyncio.sleep(5)
    # klik Complete (tombol baris terakhir pesan gate)
    last = None
    async for m in client.iter_messages(bot, limit=3):
        if m.reply_markup:
            last = m
            break
    if last:
        try:
            await last.click(len(last.reply_markup.rows) - 1, 0)
            print("Klik Complete OK.")
        except Exception as e:
            print("Klik Complete gagal: %s" % type(e).__name__)
    await asyncio.sleep(5)
    await read_bot_msgs(client, bot, 3)
    print("\nLANGKAH TERAKHIR (WAJIB DI HP):")
    print("  Buka @%s di HP -> ketuk 'Start Verification' ->" % BOT)
    print("  selesaikan Turnstile di webview Telegram. Menu kebuka kalau lolos.")
    await client.disconnect()


async def cmd_saldo():
    client = await get_client()
    if not client:
        return
    bot = await client.get_entity(BOT)
    await client.send_message(bot, "Profile")
    await asyncio.sleep(5)
    await read_bot_msgs(client, bot, 2)
    await client.send_message(bot, "Referral")
    await asyncio.sleep(5)
    await read_bot_msgs(client, bot, 2)
    await client.disconnect()


async def cmd_bonus():
    client = await get_client()
    if not client:
        return
    bot = await client.get_entity(BOT)
    await client.send_message(bot, "Daily Bonus")
    await asyncio.sleep(5)
    await read_bot_msgs(client, bot, 2)
    await client.disconnect()


async def cmd_wd():
    client = await get_client()
    if not client:
        return
    bot = await client.get_entity(BOT)
    await client.send_message(bot, "Withdraw")
    await asyncio.sleep(5)
    await read_bot_msgs(client, bot, 2)
    print("\nCatatan: skrip ini TIDAK submit withdraw — cuma baca infonya.")
    print("Withdraw baru dilakukan kalau saldo sudah >= min WD.")
    await client.disconnect()


def menu():
    print("\n===== LUNA STAR PAY BOT =====")
    print("[1] Daftar + join channel + ambil link verifikasi")
    print("[2] Cek saldo + referral")
    print("[3] Klaim Daily Bonus")
    print("[4] Cek info Withdraw (min WD)")
    print("[5] Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    while True:
        p = menu()
        if p == "1":
            asyncio.run(cmd_daftar())
        elif p == "2":
            asyncio.run(cmd_saldo())
        elif p == "3":
            asyncio.run(cmd_bonus())
        elif p == "4":
            asyncio.run(cmd_wd())
        elif p == "5":
            print("Keluar. Sampai jumpa!")
            break
        else:
            print("Pilihan tidak ada, coba lagi.")


if __name__ == "__main__":
    main()
