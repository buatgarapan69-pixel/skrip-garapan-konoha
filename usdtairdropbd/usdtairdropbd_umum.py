#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USDT AIRDROP BD BOT — skrip umum (1 perintah, menu di dalam).
Bot Telegram penghasil USDT: referral 0,01 USDT/orang aktif, WD via @xRocket.

CARA PAKAI:
  1. pip install telethon
  2. Buat file apicred.json di folder yang sama (api_id/api_hash dari
     https://my.telegram.org):
       {"api_id": 12345678, "api_hash": "abc123..."}
  3. (Opsional) Isi REF_CODE di bawah dengan user id Telegram pemberi
     referral (boleh kosong — daftar tanpa referral).
  4. Jalankan:  python3 usdtairdropbd_umum.py
     Pilih menu di dalam skrip. Saat pertama jalan, masukkan nomor HP +
     kode login Telegram. Sesi tersimpan lokal — JANGAN disebar.

CATATAN JUJUR (dicek langsung 27-28 Nov 2026):
- Naruto (Admin Konoha): referral 29, saldo 0,29 USDT.
- WD: min 0,07 USDT, tax 0,03/WD, MAKS 0,07 per WD.
- Payout TERBUKTI: 4x WD @0,07 -> terima 0,04 USDT tiap WD via
  @xRocket (total 0,16 USDT landing, dicek di wallet xRocket).
- Jangan pernah deposit, jangan bayar verifikasi apa pun, jangan
  hubungkan wallet berisi dana. Satu akun Telegram = satu akun bot.
- Jangan unsubscribe channel sponsor dalam 24 jam pertama (akun
  bisa di-block bot dan reward hilang).
"""
import asyncio, json, os, re, sys, time

BOT = "UsdtAirdropBdBot"
REF_CODE = ""          # <-- ISI: user id Telegram pemberi referral (boleh kosong)
SESSION = "usdtairdropbd_session"

# ------------------------------------------------------------------ util
def load_creds():
    if not os.path.exists("apicred.json"):
        print("Buat dulu apicred.json (api_id/api_hash dari https://my.telegram.org).")
        sys.exit(1)
    d = json.load(open("apicred.json"))
    return int(d["api_id"]), str(d["api_hash"])

def dump_buttons(m):
    rows = []
    if m.reply_markup:
        for row in m.reply_markup.rows:
            rows.append([b.text for b in row.buttons])
    return rows

def sponsor_urls(msg):
    urls = []
    if msg.reply_markup:
        for row in msg.reply_markup.rows:
            for b in row.buttons:
                t = getattr(b, "type", None)
                if t is not None:
                    mm = re.search(r"url='([^']+)'", str(t))
                    if mm:
                        urls.append(mm.group(1))
    return urls

# ------------------------------------------------------------------ aksi
async def do_register(client):
    ent = await client.get_entity(BOT)
    start = f"/start {REF_CODE}" if REF_CODE else "/start"
    await client.send_message(ent, start)
    print("Mengirim", start, "...")
    await asyncio.sleep(8)
    msgs = await client.get_messages(ent, limit=3)
    for m in msgs:
        if m.photo:
            await client.download_media(m.photo, file="captcha.jpg")
            print("Captcha tersimpan: captcha.jpg — buka gambarnya, ketik kodenya.")
            ans = input("Kode captcha (3 karakter): ").strip()
            await client.send_message(ent, ans)
            await asyncio.sleep(8)
            break
    else:
        print("Tidak ada captcha foto — mungkin sudah terverifikasi. Lanjut.")
    # baca pesan sponsor terbaru
    msgs = await client.get_messages(ent, limit=3)
    urls = []
    sponsor_msg = None
    for m in msgs:
        u = sponsor_urls(m)
        if u:
            urls, sponsor_msg = u, m
            break
    print(f"Sponsor: {len(urls)} channel/grup.")
    from telethon.tl.functions.channels import JoinChannelRequest
    for u in urls:
        try:
            target = await client.get_entity(u)
            await client(JoinChannelRequest(target))
            print("  JOIN OK:", u)
        except Exception as e:
            print("  JOIN GAGAL (join manual dari HP lalu lanjut):", u, "-", type(e).__name__)
        await asyncio.sleep(2)
    input("Sudah join semua sponsor? Tekan Enter untuk lanjut... ")
    # klik tombol JOINED NOW (tombol keyboard di pesan sponsor)
    if sponsor_msg is not None:
        for row in dump_buttons(sponsor_msg):
            for t in row:
                if "JOINED" in t.upper():
                    await client.send_message(ent, t)
                    print("Mengirim tombol:", t)
                    await asyncio.sleep(8)
                    break
    msgs = await client.get_messages(ent, limit=3)
    for m in msgs:
        print("---", (m.message or "")[:500])

def menu_buttons(client, ent):
    """Ambil teks tombol menu utama dari pesan menu terakhir (posisi tetap)."""
    return None  # diisi di bawah (async helper terpisah)

async def get_menu_btns(client, ent):
    async for m in client.iter_messages(ent, limit=10):
        if m.reply_markup and m.reply_markup.rows:
            texts = [b.text for row in m.reply_markup.rows for b in row.buttons]
            if len(texts) >= 5:
                return texts
    return None

async def read_new(client, ent, seen, limit=4):
    out = []
    async for m in client.iter_messages(ent, limit=limit):
        if m.id not in seen:
            seen.add(m.id)
            out.append(m)
    return list(reversed(out))

async def do_check(client):
    ent = await client.get_entity(BOT)
    btns = await get_menu_btns(client, ent)
    if not btns:
        print("Menu belum kebuka — daftar dulu (menu 1).")
        return
    seen = set()
    async for m in client.iter_messages(ent, limit=2):
        seen.add(m.id)
    await client.send_message(ent, btns[0])  # Account
    await asyncio.sleep(8)
    for m in await read_new(client, ent, seen):
        print("---", (m.message or "")[:800])

async def do_withdraw(client):
    ent = await client.get_entity(BOT)
    btns = await get_menu_btns(client, ent)
    if not btns:
        print("Menu belum kebuka — daftar dulu (menu 1).")
        return
    seen = set()
    async for m in client.iter_messages(ent, limit=2):
        seen.add(m.id)
    await client.send_message(ent, btns[3])  # Withdraw
    await asyncio.sleep(8)
    for m in await read_new(client, ent, seen):
        print("---", (m.message or "")[:500])
    amt = input("Jumlah WD (min 0,07, maks 0,07 per WD): ").strip()
    try:
        v = float(amt)
    except ValueError:
        print("Jumlah tidak valid.")
        return
    if v < 0.07 or v > 0.07:
        print("Jumlah harus 0,07 (min = maks per WD).")
        return
    await client.send_message(ent, amt)
    await asyncio.sleep(10)
    new = await read_new(client, ent, seen)
    confirm = None
    for m in new:
        print("---", (m.message or "")[:800])
        for row in dump_buttons(m):
            for t in row:
                if t.strip().startswith("✅"):
                    confirm = t
    if not confirm:
        print("Tidak ada prompt konfirmasi — cek pesan bot di atas.")
        return
    print(f"WD {amt} USDT, tax 0,03 -> terima 0,04 USDT via @xRocket.")
    ok = input("Konfirmasi WD? ketik 'ya': ").strip().lower()
    if ok != "ya":
        print("WD dibatalkan.")
        return
    await client.send_message(ent, confirm)
    await asyncio.sleep(20)
    for m in await read_new(client, ent, seen, limit=5):
        print("---", (m.message or "")[:800])
    print("Cek penerimaan di @xRocket (wallet USDT).")

# ------------------------------------------------------------------ menu
async def main():
    from telethon import TelegramClient
    api_id, api_hash = load_creds()
    client = TelegramClient(SESSION, api_id, api_hash)
    await client.start()
    try:
        me = await client.get_me()
        print(f"Login sebagai: {me.first_name} (id {me.id})")
        while True:
            print("\n===== USDT AIRDROP BD BOT =====")
            print("[1] Daftar (captcha + join sponsor)")
            print("[2] Cek saldo / referral")
            print("[3] Withdraw (0,07 USDT, tax 0,03)")
            print("[4] Keluar")
            p = input("➤ PILIH MENU » ").strip()
            if p == "1":
                await do_register(client)
            elif p == "2":
                await do_check(client)
            elif p == "3":
                await do_withdraw(client)
            elif p == "4":
                print("Keluar.")
                break
            else:
                print("Pilihan tidak dikenal.")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
