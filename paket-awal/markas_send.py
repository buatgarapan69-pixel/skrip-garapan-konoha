#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
markas_send.py — SATU perintah kirim ke CHANNEL Markas Tim Konoha (4343223926).
Ganti semua *_markas_0NN.py / *_keputusan*.py / rekap_internal_YYYYMMDD.py one-shot.

Pakai:
  python markas_send.py --laporan --judul "NAMA GARAPAN" --isi TEKS
  python markas_send.py --laporan --judul "NAMA" --file isi.txt [--nomor 72]
  python markas_send.py --keputusan --reply 494 --isi "KEPUTUSAN: SKIP
  Alasan: ...
  Status: DITUTUP"
  python markas_send.py --rekap --date 20261123 --file rekap.txt
  python markas_send.py --bebas --isi "teks bebas" [--reply ID]
  Tambah --dry-run untuk melihat hasil format TANPA mengirim.

Aturan format (wajib, pelajaran 20 Nov):
- Pesan dibungkus pagar ``` + parse_mode="markdown" (blok kode beneran).
- Baris <= 36 karakter untuk laporan/keputusan (skrip memberi peringatan kalau ada
  baris yang lebih panjang, tapi tetap mengirim).
- Nomor LAPORAN otomatis: baca pesan terakhir channel, ambil #NNN terbesar, +1.
  (--nomor untuk memaksa nomor tertentu.)
- Verifikasi: pesan terkirim dicek entities-nya mengandung MessageEntityPre
  (blok kode beneran, bukan teks literal). Hasil: msg id + link t.me/c/4343223926/<id>.
- KEPUTUSAN harus --reply ke msg LAPORAN yang diputuskan.
- Kirim sebagai Naruto (Admin Konoha). Sesi disalin dulu ke /tmp
  (workaround session-lock, seperti posting_channels.py).
"""

import argparse
import asyncio
import json
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "/root/hatake/tools")
from apicred import resolve as resolve_creds
from tgsession import load_session
from telethon import TelegramClient
from telethon.errors import FloodWaitError

# ---------------------------------------------------------------- warna v15 (template patokan — MENYALA, bukan kalem)
R     = "\033[91m"          # merah darah
RED   = "\033[38;5;196m"    # banner merah
DRED  = "\033[38;5;124m"    # merah gelap
W     = "\033[1;38;5;231m"  # putih terang
G     = "\033[1;38;5;46m"   # hijau menyala
Y     = "\033[93m"          # kuning emas danger
C     = "\033[1;38;5;27m"   # biru tua
GRAY  = "\033[38;5;240m"    # abu gelap
RESET = "\033[0m"

MARKAS_CH = 4343223926
DIV = "☠ " + "═" * 25 + " ☠"   # divider template #009 (25 ═)
WIB = timezone(timedelta(hours=7))


def now_wib():
    return datetime.now(WIB)


def header():
    return "\n".join([
        DIV,
        "  ☠ MARKAS TIM KONOHA ☠",
        "  DARK NETWORK DIVISION",
        "   ⚠ DANGER ZONE ⚠",
        DIV,
    ])


def warn_panjang(text, batas=36):
    """Peringatkan baris yang lebih dari batas (format Markas: <=36 karakter)."""
    panjang = [(i + 1, len(l), l[:50]) for i, l in enumerate(text.splitlines())
               if len(l) > batas]
    for i, n, l in panjang:
        print(f"{Y}[!] baris {i} panjang {n} karakter (> {batas}): {l}{RESET}", file=sys.stderr)
    return len(panjang)


def build_laporan(nomor, judul, isi):
    now = now_wib()
    judul_bersih = judul.strip().upper()
    body = "\n".join([
        header(),
        f"LAPORAN #{nomor:03d} — {judul_bersih}",
        now.strftime("%d %b %Y — %H:%M WIB").upper(),
        "",
        isi.strip(),
    ])
    return body


def build_keputusan(isi):
    body = "\n".join([header(), isi.strip()])
    return body


def build_rekap(isi, date=None):
    now = now_wib()
    if date:
        try:
            d = datetime.strptime(date, "%Y%m%d")
            tgl = d.strftime("%d %b %Y").upper()
        except ValueError:
            tgl = date
    else:
        tgl = now.strftime("%d %b %Y").upper()
    body = "\n".join([
        header(),
        f"REKAP INTERNAL — {tgl}",
        "",
        isi.strip(),
    ])
    return body


async def last_laporan_number():
    """Baca nomor LAPORAN terbesar dari 40 pesan terakhir channel."""
    src = Path("/root/hatake/session/Naruto.session")
    tmp = Path("/tmp/markas_send_Naruto.session")
    shutil.copy2(src, tmp)
    api_id, api_hash = resolve_creds("Naruto")
    client = TelegramClient(str(tmp.with_suffix("")), api_id, api_hash)
    await client.start()
    nomor = 0
    try:
        async for m in client.iter_messages(MARKAS_CH, limit=40):
            mm = m.message or ""
            for x in re.findall(r"LAPORAN #(\d+)", mm):
                nomor = max(nomor, int(x))
    finally:
        await client.disconnect()
    return nomor


async def send_markas(text, reply_to=None):
    """Kirim teks (sudah diformat) ke channel Markas sebagai Naruto.
    Return (msg_id, verified_bool)."""
    src = Path("/root/hatake/session/Naruto.session")
    tmp = Path("/tmp/markas_send_Naruto.session")
    shutil.copy2(src, tmp)
    api_id, api_hash = resolve_creds("Naruto")
    client = TelegramClient(str(tmp.with_suffix("")), api_id, api_hash)
    await client.start()
    try:
        payload = "```\n" + text.strip() + "\n```"
        for attempt in range(2):
            try:
                m = await client.send_message(
                    MARKAS_CH, payload, parse_mode="markdown", reply_to=reply_to)
                break
            except FloodWaitError as e:
                print(f"{Y}[!] FloodWait {e.seconds}s, tunggu...{RESET}")
                await asyncio.sleep(e.seconds + 2)
        else:
            raise RuntimeError("gagal kirim setelah 2 percobaan (FloodWait)")
        # Verifikasi: blok kode beneran (MessageEntityPre) + bukan teks literal.
        sent = await client.get_messages(MARKAS_CH, ids=m.id)
        ents = getattr(sent, "entities", None) or []
        has_pre = any(type(e).__name__ == "MessageEntityPre" for e in ents)
        msg_txt = sent.message or ""
        verified = has_pre and not msg_txt.startswith("```")
        return m.id, verified
    finally:
        await client.disconnect()


def baca_isi(args):
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.isi:
        return args.isi
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main():
    p = argparse.ArgumentParser(
        prog="markas_send.py",
        description="Kirim LAPORAN / KEPUTUSAN / REKAP ke CHANNEL Markas Tim Konoha.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--laporan", action="store_true", help="mode LAPORAN #NNN")
    g.add_argument("--keputusan", action="store_true", help="mode KEPUTUSAN (wajib --reply)")
    g.add_argument("--rekap", action="store_true", help="mode REKAP INTERNAL harian")
    g.add_argument("--bebas", action="store_true", help="mode teks bebas (tanpa template)")
    p.add_argument("--isi", metavar="TEKS", help="isi pesan (atau pakai --file / stdin)")
    p.add_argument("--judul", help="judul LAPORAN (mis. MOA PROTOCOL)")
    p.add_argument("--file", help="baca isi dari file")
    p.add_argument("--nomor", type=int, help="paksa nomor LAPORAN (default: otomatis +1)")
    p.add_argument("--reply", type=int, help="reply ke msg id (wajib untuk --keputusan)")
    p.add_argument("--date", help="tanggal rekap YYYYMMDD (default: hari ini)")
    p.add_argument("--dry-run", action="store_true", help="tampilkan hasil format, jangan kirim")
    args = p.parse_args()

    isi = baca_isi(args)
    if args.keputusan and not args.reply:
        p.error("--keputusan wajib --reply <msg id LAPORAN yang diputuskan>")
    if args.laporan and not args.judul:
        p.error("--laporan wajib --judul")

    if args.laporan:
        if args.nomor:
            nomor = args.nomor
        else:
            print(f"{GRAY}[*] Membaca nomor LAPORAN terakhir dari channel...{RESET}")
            nomor = asyncio.run(last_laporan_number()) + 1
        text = build_laporan(nomor, args.judul, isi)
        print(f"{G}[+] Nomor LAPORAN: #{nomor:03d}{RESET}")
    elif args.keputusan:
        text = build_keputusan(isi)
    elif args.rekap:
        text = build_rekap(isi, args.date)
    else:
        text = isi

    warn_panjang(text)
    if args.dry_run:
        print("```")
        print(text)
        print("```")
        print(f"{Y}[dry-run] tidak dikirim.{RESET}")
        return 0

    msg_id, verified = asyncio.run(send_markas(text, reply_to=args.reply))
    print(f"{G}[+] Terkirim ke Markas: msg {msg_id}{RESET}")
    print(f"{C}    https://t.me/c/4343223926/{msg_id}{RESET}")
    if verified:
        print(f"{G}[+] Terverifikasi: blok kode beneran (MessageEntityPre).{RESET}")
    else:
        print(f"{R}[!] PERINGATAN: entities tidak mengandung MessageEntityPre — "
              f"cek format di channel!{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
