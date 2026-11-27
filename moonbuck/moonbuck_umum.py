#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOONBUCK (@MoonBuckBOT) — skrip umum (untuk dipakai orang lain, 1 akun).
Bot Telegram gratis: undang teman + tugas + nonton iklan = USDT BEP20.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon
  2. Ambil API_ID + API_HASH di https://my.telegram.org/apps
  3. Isi bagian KONFIG di bawah (API_ID, API_HASH, WALLET, REF_CODE)
     - WALLET = alamat USDT BEP20 kamu (contoh: 0x...)
     - REF_CODE = ID Telegram pengundang (angka, mis. 1234567890).
       Boleh kosong — kalau kosong, daftar tanpa referral.
  4. Jalankan:  python3 moonbuck_umum.py
     - login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
     - pilih menu di dalam skrip (1 perintah, semua lewat menu)

YANG DIDAPAT (hasil probe Tim Konoha, 28 Nov 2026):
  - Daftar gratis: /start bot, join @airdropsons, klik Free USDT
  - Per referral: 0,2 USDT BEP20 (referral masuk begitu teman daftar + klik Free USDT)
  - Task #2 (join @pandalooker20): +0,5 USDT, verifikasi otomatis
  - Task #1 (start @SleyProductionBOT): +0,5 USDT, verifikasi SCREENSHOT MANUAL
    (bot minta kirim screenshot — skrip ini TIDAK mengerjakannya, lakukan dari HP)
  - Nonton iklan: 0,05 USDT/iklan, 20 iklan/hari (butuh WebView asli —
    skrip ini TIDAK nonton iklan otomatis, lakukan dari HP)
  - Min WD: 3 USDT | Maks WD: 5 USDT | Fee WD: 0,5 USDT (terima bersih 2,5 dari WD 3)
  - Saldo Tim Konoha saat probe: 6,3 USDT (0,5 tugas + 5,8 dari 29 referral)

CATATAN JUJUR — BACA DULU:
  - PAYOUT BELUM TERBUKTI (28 Nov 2026): WD pertama Tim Konoha (3 USDT)
    status "Waiting for approval" — payout direview manual oleh admin bot,
    belum landing saat skrip ini ditulis. Dipantau 3 hari (aturan kami:
    WD >3 hari tidak landing = kemungkinan scam, skrip dihentikan).
  - Klaim channel soal "WD instan 30 menit" BELUM terbukti; info resmi bot
    (@MoonBuckNews): payout dikirim ke admin untuk review, tidak dipungut
    biaya apa pun ("We won't ask you to pay for your withdrawal").
  - JANGAN PERNAH membayar apa pun ke bot ini (deposit/fee tambahan).
    Kalau bot minta bayaran untuk WD, BERHENTI — itu penipuan.
  - HATI-HATI: saat bot menunggu input wallet, teks apa pun (termasuk /start)
    akan disimpan sebagai alamat wallet. Kirim alamat wallet dengan benar.
  - File sesi (moonbuck_umum.session) JANGAN dibagikan ke siapa pun.
  - Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
"""
import asyncio
import json
import os
import sys

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

# ============================== KONFIG — ISI DULU ==============================
API_ID = 0            # <-- isi: angka dari https://my.telegram.org/apps
API_HASH = ""         # <-- isi: string dari https://my.telegram.org/apps
WALLET = ""           # <-- isi: alamat USDT BEP20 kamu, contoh "0x..."
REF_CODE = ""         # <-- opsional: ID Telegram pengundang (angka saja)

BOT = "MoonBuckBOT"
MUST_JOIN = "airdropsons"
TASK2_CHANNEL = "pandalooker20"
SESSION = "moonbuck_umum.session"
MIN_WD = 3.0
MAX_WD = 5.0


def rich_text(obj):
    """Isi asli pesan bot ini ada di rich_message (PageBlocks), bukan field message."""
    if obj is None:
        return ""
    cls = type(obj).__name__
    if cls == "TextPlain":
        return getattr(obj, "text", "") or ""
    if cls in ("TextBold", "TextItalic", "TextUnderline", "TextStrike",
               "TextFixed", "TextSubscript", "TextSuperscript", "TextMarked",
               "TextUrl", "TextEmail", "TextAnchor"):
        return rich_text(getattr(obj, "text", None))
    if cls == "TextCustomEmoji":
        return getattr(obj, "alt", "") or ""
    if cls == "TextConcat":
        return "".join(rich_text(t) for t in (getattr(obj, "texts", None) or []))
    if cls == "TextEmpty":
        return ""
    if cls in ("PageBlockTitle", "PageBlockSubtitle", "PageBlockHeader",
               "PageBlockSubheader", "PageBlockParagraph", "PageBlockFooter",
               "PageBlockCaption", "PageBlockAuthorDate", "PageBlockKicker"):
        return rich_text(getattr(obj, "text", None))
    if cls == "PageBlockList":
        return "\n".join("- " + rich_text(i) for i in (getattr(obj, "items", None) or []))
    if cls == "PageBlockTable":
        out = []
        t = rich_text(getattr(obj, "title", None))
        if t:
            out.append(t)
        for row in (getattr(obj, "rows", None) or []):
            cells = [rich_text(getattr(c, "text", None)) for c in (getattr(row, "cells", None) or [])]
            out.append(" | ".join(cells))
        return "\n".join(out)
    if cls == "PageBlockDivider":
        return "---"
    if cls in ("PageBlockPhoto", "PageBlockVideo", "PageBlockAnimation",
               "PageBlockEmbed", "PageBlockAudio", "PageBlockCover",
               "PageBlockSlideshow", "PageBlockCollage"):
        return "[media]"
    if cls == "RichMessage":
        return "\n".join(rich_text(b) for b in (getattr(obj, "blocks", None) or []))
    d = getattr(obj, "__dict__", None)
    if isinstance(d, dict):
        parts = []
        for k in ("text", "title", "texts", "blocks", "rows", "items", "cells"):
            if k in d and d[k] is not None:
                v = d[k]
                parts.append(" ".join(rich_text(x) for x in v) if isinstance(v, list) else rich_text(v))
        return " ".join(p for p in parts if p)
    return ""


async def read_new(client, ent, seen, limit=6):
    out = []
    async for m in client.iter_messages(ent, limit=limit):
        if m.id not in seen:
            seen.add(m.id)
            out.append(m)
    return list(reversed(out))


async def show(client, ent, seen, label):
    await asyncio.sleep(6)
    new = await read_new(client, ent, seen)
    for n in new:
        print("---", label, "---")
        print(rich_text(getattr(n, "rich_message", None)) or (n.message or ""))
    return new


async def click_inline(client, ent, seen, want):
    """Klik tombol inline `want` di pesan terbaru bot. Return True bila berhasil."""
    async for m in client.iter_messages(ent, limit=4):
        if not m.reply_markup:
            continue
        for ri, row in enumerate(m.reply_markup.rows):
            for bi, b in enumerate(row.buttons):
                if (b.text or "").strip() == want:
                    try:
                        await m.click(ri, bi)
                        return True
                    except Exception as e:
                        print("  klik gagal:", repr(e)[:150])
                        return False
    print("  tombol '%s' tidak ketemu" % want)
    return False


async def menu_text(client, bot, seen, text, label):
    await client.send_message(bot, text)
    return await show(client, bot, seen, label)


async def daftar(client, bot, seen):
    """[1] Daftar + join channel wajib + klik Free USDT."""
    print("\n[1] DAFTAR")
    start = "/start " + REF_CODE if REF_CODE else "/start"
    await client.send_message(bot, start)
    await asyncio.sleep(8)
    await read_new(client, bot, seen)
    try:
        ch = await client.get_entity(MUST_JOIN)
        await client(JoinChannelRequest(ch))
        print("  join @%s OK" % MUST_JOIN)
    except Exception as e:
        print("  join @%s gagal: %s" % (MUST_JOIN, repr(e)[:150]))
    await asyncio.sleep(2)
    if await click_inline(client, bot, seen, "Free USDT"):
        await asyncio.sleep(6)
        await show(client, bot, seen, "Menu utama")
        print("  Daftar selesai. Cek saldo via menu [2].")
    else:
        print("  Gagal klik Free USDT — buka bot manual, klik Free USDT.")


async def cek_saldo(client, bot, seen):
    """[2] Cek saldo + struktur penghasilan."""
    print("\n[2] SALDO")
    await menu_text(client, bot, seen, "Balance", "Balance")


async def cek_referral(client, bot, seen):
    """[3] Cek referral + link undangan kamu."""
    print("\n[3] REFERRAL")
    await menu_text(client, bot, seen, "Referrals", "Referrals")


async def task2(client, bot, seen):
    """[4] Task #2: join @pandalooker20 lalu Verify (+0,5 USDT)."""
    print("\n[4] TASK #2 (+0,5 USDT)")
    try:
        ch = await client.get_entity(TASK2_CHANNEL)
        await client(JoinChannelRequest(ch))
        print("  join @%s OK" % TASK2_CHANNEL)
    except Exception as e:
        print("  join gagal: %s" % repr(e)[:150])
        return
    await asyncio.sleep(2)
    await client.send_message(bot, "Tasks")
    await asyncio.sleep(6)
    await read_new(client, bot, seen)
    if await click_inline(client, bot, seen, "Partner's Community"):
        await asyncio.sleep(6)
        await read_new(client, bot, seen)
        if await click_inline(client, bot, seen, "Verify"):
            await show(client, bot, seen, "Hasil Verify Task #2")
        else:
            print("  Tombol Verify tidak ketemu — coba lagi nanti.")


async def set_wallet(client, bot, seen):
    """[5] Set wallet USDT BEP20."""
    print("\n[5] SET WALLET")
    if not WALLET:
        print("  WALLET di KONFIG masih kosong. Isi dulu, lalu jalankan lagi.")
        return
    await menu_text(client, bot, seen, "Set Wallet", "Set Wallet")
    await client.send_message(bot, WALLET)
    await show(client, bot, seen, "Hasil set wallet")


async def withdraw(client, bot, seen):
    """[6] Withdraw jumlah minimal (3 USDT, fee 0,5, terima 2,5)."""
    print("\n[6] WITHDRAW")
    if not WALLET:
        print("  Set wallet dulu via menu [5].")
        return
    res = await menu_text(client, bot, seen, "Balance", "Balance sebelum WD")
    txt = " ".join(rich_text(getattr(n, "rich_message", None)) for n in res)
    print("  Saldo saat ini (lihat di atas). Min WD 3, maks 5 USDT.")
    pil = (await asyncio.to_thread(input, "  Jumlah WD (3-5, kosongkan untuk batal): ")).strip()
    if not pil:
        print("  WD dibatalkan.")
        return
    try:
        amt = float(pil)
    except ValueError:
        print("  Jumlah tidak valid.")
        return
    if amt < MIN_WD or amt > MAX_WD:
        print("  Jumlah harus 3-5 USDT.")
        return
    await client.send_message(bot, "Withdraw")
    await asyncio.sleep(6)
    await read_new(client, bot, seen)
    await client.send_message(bot, str(int(amt)) if amt == int(amt) else str(amt))
    await show(client, bot, seen, "Hasil WD")
    print("  Catatan: WD direview manual admin (status 'Waiting for approval').")
    print("  Pantau saldo wallet %s, dan cek Balance berkala." % WALLET)


def banner():
    print("=" * 48)
    print("  MOONBUCK (@MoonBuckBOT) — skrip umum 1 akun")
    print("  0,2 USDT/referral | Task 0,5 | Min WD 3 USDT")
    print("  PAYOUT BELUM TERBUKTI — WD pertama masih review admin")
    print("=" * 48)


async def main():
    if not API_ID or not API_HASH:
        print("ISI DULU KONFIG: API_ID + API_HASH (lihat bagian atas skrip).")
        sys.exit(1)
    client = TelegramClient(SESSION, int(API_ID), str(API_HASH))
    await client.start()
    try:
        me = await client.get_me()
        print("Login sebagai: %s (@%s)" % (me.first_name, me.username))
        bot = await client.get_entity(BOT)
        seen = set()
        async for m in client.iter_messages(bot, limit=3):
            seen.add(m.id)
        while True:
            banner()
            print("  [1] Daftar (start + join + Free USDT)")
            print("  [2] Cek saldo")
            print("  [3] Cek referral + link undangan")
            print("  [4] Task #2 (+0,5 USDT, join channel)")
            print("  [5] Set wallet USDT BEP20")
            print("  [6] Withdraw (min 3, maks 5, fee 0,5)")
            print("  [7] Keluar")
            pil = (await asyncio.to_thread(input, "  Pilih menu (1-7): ")).strip()
            if pil == "1":
                await daftar(client, bot, seen)
            elif pil == "2":
                await cek_saldo(client, bot, seen)
            elif pil == "3":
                await cek_referral(client, bot, seen)
            elif pil == "4":
                await task2(client, bot, seen)
            elif pil == "5":
                await set_wallet(client, bot, seen)
            elif pil == "6":
                await withdraw(client, bot, seen)
            elif pil == "7":
                print("  Sampai jumpa.")
                break
            else:
                print("  Pilihan tidak dikenal.")
            await asyncio.to_thread(input, "  [Enter untuk lanjut]")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
