#!/usr/bin/env python3
"""MASABOX — Bot Stars Gratis (versi untuk umum).

GRATIS, tanpa deposit, tanpa top-up, tanpa connect wallet.
Earn: bonus daftar 1 Star + 2 Star tiap teman yang daftar pakai link kamu.
Min WD: 25 Stars, WD via username Telegram (payout BELUM terbukti).

Cara pakai:
  1. pip install telethon
  2. Ambil API_ID + API_HASH kamu di https://my.telegram.org/apps
  3. Isi API_ID dan API_HASH di bawah, lalu jalankan:
     python3 masabox_umum.py
  4. Login pertama kali: masukkan nomor HP Telegram kamu + kode
     yang dikirim Telegram (file sesi masabox.session tersimpan
     di folder yang sama — JANGAN dibagikan ke siapa pun).
  5. Skrip akan: /start pakai ref Tim Konoha, join 10 channel,
     klik Claim. Lalu skrip TANYA dulu sebelum verifikasi HP:
     ketik y kalau kamu setuju nomor HP akun Telegram kamu
     dibagikan ke @MasaBoxes_Bot (sama seperti mengetuk tombol
     "Share Profile" di aplikasi Telegram). Ketik n untuk
     berhenti dan verifikasi manual dari aplikasi (ketuk tombol
     "Share Profile" di chat bot).

Dibagikan gratis oleh Tim Konoha — silakan dipakai & dibagikan.
"""
import asyncio
import sys

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputMediaContact

# ======= ISI BAGIAN INI =======
API_ID = 0  # contoh: 12345678 (angka, dari my.telegram.org/apps)
API_HASH = "ISI_API_HASH_KAMU"  # contoh: "0123456789abcdef0123456789abcdef"
# ==============================

BOT = "MasaBoxes_Bot"
REF = ""  # isi dengan ID Telegram kamu (referrer)
INVITES = ["KJg729S3sfBmYWI1", "pwjn6u7nsNc2Mjhl", "MSObJe3k1M80MjY9",
           "i2J9aMdzsBE5YjVl", "4LRsqGrC7pJkOGRl", "fpqwArAaLr1jMDM1",
           "xcHtRN5aayAzMDg1", "F2jYhNNUSQc0ZWVl", "8jIBkb0sq1EyOGY0",
           "E0VIJnfLbOo3MjE1"]
PUBLIC_CHANNEL = "Forestotc"


async def main():
    if not API_ID or API_HASH in ("ISI_API_HASH_KAMU", ""):
        print("Isi dulu API_ID dan API_HASH di bagian atas skrip.")
        sys.exit(1)
    client = TelegramClient("masabox", API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    print("Login sebagai:", me.username or me.first_name, "| id:", me.id)
    bot = await client.get_entity(BOT)
    await client.send_message(bot, "/start " + REF)
    print("Terkirim /start, ref Konoha.")
    await asyncio.sleep(5)
    for h in INVITES:
        try:
            await client(ImportChatInviteRequest(h))
            print("Join OK:", h)
        except FloodWaitError as e:
            print("FloodWait %s detik di %s — tunggu lalu lanjut" % (e.seconds, h))
            await asyncio.sleep(min(e.seconds, 300))
        except Exception as e:
            if "already a participant" in str(e):
                print("Sudah join:", h)
            else:
                print("Join gagal %s: %s" % (h, str(e)[:100]))
        await asyncio.sleep(15)
    try:
        await client.join_channel(PUBLIC_CHANNEL)
        print("Join OK: @Forestotc")
    except Exception as e:
        print("Join @Forestotc:", str(e)[:100])
    await asyncio.sleep(5)
    msgs = await client.get_messages(bot, limit=1)
    try:
        await msgs[0].click(text="🔒 Claim")
        print("Claim diklik.")
    except Exception as e:
        print("Klik Claim gagal (coba manual di aplikasi):", str(e)[:100])
    await asyncio.sleep(8)
    latest = (await client.get_messages(bot, limit=1))[0]
    if "Verification Required" not in (latest.message or ""):
        print("Tidak ada permintaan verifikasi — cek menu bot di aplikasi.")
    else:
        print()
        print("Bot minta verifikasi nomor HP (tombol Share Profile).")
        print("Skrip bisa mengirim nomor HP akun kamu sendiri ke bot")
        print("(persis seperti mengetuk Share Profile di aplikasi).")
        jawab = input("Lanjut kirim nomor HP kamu ke bot? (y/n): ").strip().lower()
        if jawab == "y":
            phone = me.phone
            phone_plus = phone if phone.startswith("+") else "+" + phone
            await client.send_message(
                bot,
                file=InputMediaContact(phone_number=phone_plus,
                                       first_name=me.first_name or "",
                                       last_name=me.last_name or "", vcard=""),
                reply_to=latest.id)
            print("Kontak terkirim. Tunggu balasan bot...")
            await asyncio.sleep(10)
            after = (await client.get_messages(bot, limit=1))[0]
            print("Bot:", (after.message or "")[:200])
        else:
            print("Berhenti. Verifikasi manual: buka chat bot di aplikasi")
            print("Telegram dan ketuk tombol Share Profile.")
    await client.send_message(bot, "Account")
    await asyncio.sleep(5)
    acc = (await client.get_messages(bot, limit=1))[0]
    print("----")
    print(acc.message or "(tidak ada balasan)")
    print("----")
    print("Link referral kamu ada di menu Referral (ketik Referral di bot).")
    await client.disconnect()


asyncio.run(main())
