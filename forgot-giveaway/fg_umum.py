#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FORGOT GIVEAWAY — skrip umum (untuk dipakai orang lain, 1 akun).
Giveaway harian Telegram gratis: kerjakan tugas = tiket, 1 tiket = 1 undian.
Tanpa deposit, tanpa wallet berisi dana, tanpa WD otomatis.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon requests
  2. Ambil API_ID + API_HASH di https://my.telegram.org/apps
  3. Isi bagian KONFIG di bawah (API_ID, API_HASH; REF_CODE = kode referral
     pengundang, mis. ref_1234567890 — boleh kosong, kalau kosong daftar tanpa ref)
  4. Jalankan:  python3 fg_umum.py
     - login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
     - pilih menu di dalam skrip (daftar, kerjakan tugas, ikut giveaway, cek saldo)

YANG DIDAPAT (hasil probe 27 Nov 2026):
  - Daftar gratis: /start bot, gabung @AirdropForgot, verifikasi
  - 3 tugas join channel = 7 tiket gratis
    (@AirdropForgot +2, @ForgotDisscussion +3, @DeskaOfficial +2)
  - Giveaway tiap hari, 10 pemenang, hadiah Rp2.000-Rp15.000/pemenang
    (dipotong fee 15% saat menang), undian transparan (seed hash)
  - Undang teman = 1 tiket per referral terdaftar
  - Min WD: Rp10.000 ke DANA/SeaBank (fee 15%, ACC manual admin).
    Di bawah Rp10.000 (min Rp1.000) cuma bisa via DM admin @Ibehh_yaeilah.
  - USDT tidak aktif (WD USDT dimatikan admin saat probe).

CATATAN JUJUR — BACA DULU:
  - PAYOUT BELUM TERBUKTI (27 Nov 2026): belum ada yang menang + WD dari
    tim kami saat skrip ini ditulis. Undian #11 (19:00 WIB) sudah jalan,
    10 pemenang diumumkan di Mini App. Menang itu undian, bukan pasti.
  - Giveaway #9 (Rp100.000, 10 pemenang) diundi 27 Nov 22:00 WIB,
    #10 (Rp20.000, gratis) 22:15 WIB. Cek hasilnya di Mini App.
  - Beli tiket di toko (Rp300 + fee Rp100/tiket) TIDAK disarankan —
    skrip ini TIDAK PERNAH beli tiket, cuma pakai tiket gratis.
  - File sesi (fg_umum.session) JANGAN dibagikan ke siapa pun.
  - Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
"""

import asyncio
import json
import urllib.parse
import urllib.request
import urllib.error

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest

# ============================== KONFIG — ISI DULU ==============================
API_ID = 0          # <-- isi: angka dari https://my.telegram.org/apps
API_HASH = ""       # <-- isi: string dari https://my.telegram.org/apps
REF_CODE = ""       # <-- opsional: kode referral pengundang (mis. ref_1234567890)

BOT = "ForgotGiveawayApp"
WEBVIEW_URL = "https://goonexplore.my.id/forgot/"
API = "https://goonexplore.my.id/forgot/api"
CHANNELS = ["AirdropForgot", "DeskaOfficial", "ForgotDisscussion"]
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
SESSION = "fg_umum.session"


def api(path, initdata, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={"x-telegram-init-data": initdata,
                 "content-type": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode(errors="ignore"))
        except Exception:
            return {"ok": False, "error": "http_%d" % e.code}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def get_initdata(client):
    bot = await client.get_entity(BOT)
    r = await client(RequestWebViewRequest(peer=bot, bot=bot, url=WEBVIEW_URL,
                                           platform="android", from_bot_menu=False))
    frag = urllib.parse.urlparse(r.url).fragment
    return urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]


async def daftar(client):
    """[1] Daftar + verifikasi + join 3 channel tugas."""
    bot = await client.get_entity(BOT)
    start = "/start " + REF_CODE if REF_CODE else "/start"
    await client.send_message(bot, start)
    await asyncio.sleep(3)
    for ch in CHANNELS:
        try:
            await client(JoinChannelRequest(await client.get_entity(ch)))
            print("  join @%s OK" % ch)
        except Exception as e:
            print("  join @%s GAGAL: %s" % (ch, str(e)[:120]))
    await asyncio.sleep(2)
    async for m in client.iter_messages(bot, limit=5):
        if not m.reply_markup:
            continue
        done = False
        for ri, row in enumerate(m.reply_markup.rows):
            for ci, b in enumerate(row.buttons):
                if "Joined" in (getattr(b, "text", "") or ""):
                    try:
                        await m.click(ri, ci)
                        print("  tombol verifikasi diklik")
                    except Exception as e:
                        print("  klik verifikasi gagal:", str(e)[:120])
                    done = True
                    break
            if done:
                break
        if done:
            break
    await asyncio.sleep(3)
    initdata = await get_initdata(client)
    me = api("/me", initdata) if initdata else {}
    u = (me.get("data") or {}).get("user", {})
    print("  terdaftar: %s | tiket: %s | saldo: Rp%s | verified: %s"
          % (u.get("username"), u.get("tickets"), u.get("balanceIdr"), u.get("verified")))
    return initdata


def kerjakan_tugas(initdata):
    """[2] Klaim 3 tugas join channel (7 tiket)."""
    total = 0
    for tid in (7, 8, 9):
        r = api("/tasks/%d/join" % tid, initdata, method="POST", body={})
        if r.get("ok"):
            tk = (r.get("data") or {}).get("tickets") or []
            total += len(tk)
            print("  tugas %d OK: +%d tiket %s" % (tid, len(tk), tk))
        else:
            print("  tugas %d gagal: %s" % (tid, r.get("error")))
    print("  total tiket baru: %d" % total)


def ikut_giveaway(initdata):
    """[3] Lihat giveaway aktif + ikut (tiket / gratis)."""
    g = api("/giveaways", initdata)
    items = ((g.get("data") or {}).get("giveaways") or [])
    aktif = [x for x in items if x.get("status") == "scheduled"]
    if not aktif:
        print("  tidak ada giveaway aktif saat ini")
        return
    for x in aktif:
        print("  [%d] %s — Rp%s/pemenang x%d, draw %s, mode %s, entri saya %s"
              % (x["id"], x["title"], x["prizeAmount"], x["winnersCount"],
                 x["drawAt"], x["joinMode"], x.get("myEntries")))
    tk = api("/tickets", initdata)
    print("  tiket tersedia: %s" % ((tk.get("data") or {}).get("available")))
    for x in aktif:
        n = 1
        if x["joinMode"] == "ticket":
            try:
                n = int(input("  ikut [%d] %s pakai berapa tiket? (0 = lewati) "
                              % (x["id"], x["title"])).strip() or "0")
            except (ValueError, EOFError):
                n = 0
        if n <= 0:
            continue
        r = api("/giveaways/%d/enter" % x["id"], initdata, method="POST", body={"count": n})
        if r.get("ok"):
            print("  masuk [%d]: %s entri, sisa tiket %s"
                  % (x["id"], (r.get("data") or {}).get("entered"), (r.get("data") or {}).get("ticketsLeft")))
        else:
            print("  masuk [%d] gagal: %s" % (x["id"], r.get("error")))


def cek_status(initdata):
    """[4] Cek saldo, tiket, referral, WD."""
    me = api("/me", initdata)
    u = (me.get("data") or {}).get("user", {})
    ref = api("/referral", initdata)
    print("  saldo: Rp%s | tiket: %s | menang total: Rp%s | WD total: Rp%s"
          % (u.get("balanceIdr"), u.get("tickets"), u.get("totalWonIdr"), u.get("totalWithdrawnIdr")))
    print("  referral: %s orang, %s tiket | link: %s"
          % ((ref.get("data") or {}).get("count"), (ref.get("data") or {}).get("ticketsEarned"),
             (ref.get("data") or {}).get("link")))
    print("  min WD: Rp10.000 ke DANA/SeaBank (fee 15%, ACC manual admin)")


async def main():
    if not API_ID or not API_HASH:
        print("ISI DULU API_ID + API_HASH di bagian KONFIG (https://my.telegram.org/apps)")
        return
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("Login Telegram dulu (nomor HP + kode OTP):")
        phone = input("  nomor HP (+62...): ").strip()
        await client.send_code_request(phone)
        code = input("  kode OTP: ").strip()
        await client.sign_in(phone, code)
    me = await client.get_me()
    print("Login sebagai: %s (@%s)" % (me.first_name, me.username))
    initdata = None
    while True:
        print("\n==== FORGOT GIVEAWAY ====")
        print("[1] Daftar + verifikasi (sekali saja)")
        print("[2] Kerjakan 3 tugas (7 tiket gratis)")
        print("[3] Ikut giveaway (tiket / gratis)")
        print("[4] Cek saldo + tiket + referral")
        print("[0] Keluar")
        pilih = input("➤ PILIH MENU » ").strip()
        if pilih == "1":
            initdata = await daftar(client)
        elif pilih == "2":
            if not initdata:
                initdata = await get_initdata(client)
            kerjakan_tugas(initdata)
        elif pilih == "3":
            if not initdata:
                initdata = await get_initdata(client)
            ikut_giveaway(initdata)
        elif pilih == "4":
            if not initdata:
                initdata = await get_initdata(client)
            cek_status(initdata)
        elif pilih == "0":
            break
        else:
            print("  pilihan tidak dikenal")
    await client.disconnect()
    print("Selesai. Semoga menang!")


if __name__ == "__main__":
    asyncio.run(main())
