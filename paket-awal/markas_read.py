#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
markas_read.py — baca N pesan terakhir CHANNEL Markas Tim Konoha (4343223926).
Ganti 8 helper baca Markas one-shot (bitton_markas_check, dinoqr_markas_check,
kageveil_markas_check, markas_last_check_2000, markas_latest_20261123_1645,
mtonga_markas_read, read_markas_20261123_1654, apex_markas_read_20261122).

Pakai:
  python markas_read.py --n 5                  # 5 pesan terakhir (teks)
  python markas_read.py --n 10 --cari LAPORAN  # filter berisi "LAPORAN"
  python markas_read.py --n 3 --json            # output JSON (untuk skrip lain)
  python markas_read.py --n 1 --akun Naruto    # baca sebagai akun lain

Baca sebagai Iruka secara default (akun baca, bukan Naruto — supaya tidak
mengganggu sesi kirim). Sesi disalin dulu ke /tmp (workaround session-lock).
"""

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/root/hatake/tools")
from apicred import resolve as resolve_creds
from tgsession import load_session
from telethon import TelegramClient

# ---------------------------------------------------------------- warna v15 (template patokan — MENYALA, bukan kalem)
R     = "\033[91m"          # merah darah
RED   = "\033[38;5;196m"    # banner merah
W     = "\033[1;38;5;231m"  # putih terang
G     = "\033[1;38;5;46m"   # hijau menyala
Y     = "\033[93m"          # kuning emas danger
C     = "\033[1;38;5;27m"   # biru tua
GRAY  = "\033[38;5;240m"    # abu gelap
RESET = "\033[0m"

MARKAS_CH = 4343223926


async def read_markas(n, akun, cari=None):
    src = Path(f"/root/hatake/session/{akun}.session")
    tmp = Path(f"/tmp/markas_read_{akun}.session")
    shutil.copy2(src, tmp)
    api_id, api_hash = resolve_creds(akun)
    client = TelegramClient(str(tmp.with_suffix("")), api_id, api_hash)
    await client.start()
    out = []
    try:
        async for m in client.iter_messages(MARKAS_CH, limit=n):
            txt = m.message or ""
            if cari and cari.lower() not in txt.lower():
                continue
            reply_to = None
            if m.reply_to:
                reply_to = getattr(m.reply_to, "reply_to_msg_id", None)
            out.append({
                "id": m.id,
                "date": m.date.isoformat() if m.date else None,
                "reply_to": reply_to,
                "text": txt,
            })
    finally:
        await client.disconnect()
    return out


def main():
    p = argparse.ArgumentParser(
        prog="markas_read.py",
        description="Baca N pesan terakhir CHANNEL Markas Tim Konoha.")
    p.add_argument("--n", type=int, default=5, help="jumlah pesan (default 5)")
    p.add_argument("--cari", help="filter: hanya pesan yang mengandung teks ini")
    p.add_argument("--json", action="store_true", help="output JSON (bukan teks)")
    p.add_argument("--akun", default="Iruka", help="akun pembaca (default Iruka)")
    p.add_argument("--full", action="store_true", help="tampilkan teks lengkap (default: 600 karakter)")
    args = p.parse_args()

    msgs = asyncio.run(read_markas(args.n, args.akun, args.cari))
    if args.json:
        print(json.dumps(msgs, ensure_ascii=False, indent=1))
        return 0
    if not msgs:
        print(f"{Y}[!] Tidak ada pesan yang cocok.{RESET}")
        return 0
    for m in msgs:
        txt = m["text"]
        if not args.full and len(txt) > 600:
            txt = txt[:600] + "…"
        print(f"{C}msg {m['id']}{RESET}  {GRAY}{m['date']}"
              f"{'  reply→' + str(m['reply_to']) if m['reply_to'] else ''}{RESET}")
        print(txt)
        print(f"{GRAY}{'─' * 40}{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
