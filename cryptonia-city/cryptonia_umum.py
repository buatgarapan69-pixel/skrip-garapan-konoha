#!/usr/bin/env python3
"""CRYPTONIA CITY — Pelacak Misi & CXP (versi untuk umum).

GRATIS, tanpa deposit. Daftar pakai email + kode OTP di:
  https://cryptoniacity.com

Skrip ini PELACAK misi, bukan auto-claim: misi X / Telegram /
posting dikerjakan manual di situsnya (Lounge), lalu ditandai
selesai di sini supaya total CXP kamu kehitung.

Target: 10.000 CXP menuju early access (gelombang berikut
Senin 30 Nov 2026 08:00). Cap maks 200.000 CXP/orang.
Misi harian reset tiap 00:00 UTC.
Min WD: BELUM ADA — tombol Convert CXP masih Coming soon,
jadi kumpulin CXP dulu. Wallet Hedera (Batch 1) baru bisa
diklaim setelah 3 tugas lounge berbeda.

Referral: teman yang daftar pakai kode kamu +200 CXP,
kamu +500 CXP saat teman memenuhi syarat (maks 50 undangan
berhadiah). Kode referral kamu ada di halaman Invite situsnya.

Cara pakai:
  python3 cryptonia_umum.py          (menu interaktif)
  python3 cryptonia_umum.py status   (lihat progres saja)

Progres tersimpan di cryptonia_progress.json (file yang sama
dibuat otomatis di folder skrip ini).

Dibagikan gratis oleh Tim Konoha — silakan dipakai & dibagikan.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path(__file__).with_name("cryptonia_progress.json")
TARGET = 10000

# (kode, nama misi, CXP, jenis) — jenis: sekali / harian / sosial
MISSIONS = [
    ("x-hubungkan", "Hubungkan akun X", 200, "sekali"),
    ("x-follow", "Follow Cryptonia City di X", 300, "sekali"),
    ("tg-komunitas", "Gabung komunitas Telegram", 300, "sekali"),
    ("tg-berita", "Gabung channel berita Telegram", 300, "sekali"),
    ("tg-og", "Telegram OG", 1000, "sekali"),
    ("lihat-city", "Lihat sekilas City", 200, "sekali"),
    ("daily-posting", "Posting CityDAILY", 100, "harian"),
    ("daily-umur", "Kartu umur Telegram", 100, "harian"),
    ("daily-phonia", "Spot Phonia", 150, "harian"),
    ("daily-chat", "Percakapan Telegram", 150, "harian"),
    ("daily-notifx", "Notifikasi X", 150, "harian"),
    ("daily-like5", "Like & repost 5 post X", 150, "harian"),
    ("partner-10k", "Airdrop partner $10.000", 500, "sosial"),
    ("discord", "Gabung Discord", 150, "sosial"),
    ("tiktok", "Follow TikTok", 150, "sosial"),
    ("youtube", "Subscribe YouTube", 300, "sosial"),
    ("tag-3", "Tag 3 teman", 150, "sosial"),
    ("like-pin", "Like & repost post pin", 150, "sosial"),
]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"done_once": [], "done_daily": {}, "invite_code": ""}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def total_cxp(state):
    total = 0
    by_code = {m[0]: m for m in MISSIONS}
    for code in state["done_once"]:
        if code in by_code:
            total += by_code[code][2]
    for _day, codes in state["done_daily"].items():
        for code in codes:
            if code in by_code:
                total += by_code[code][2]
    return total


def show_status(state):
    total = total_cxp(state)
    print("=" * 40)
    print("CRYPTONIA CITY — progres CXP kamu")
    print("=" * 40)
    print("Total CXP : %d / %d (%.1f%%)" % (total, TARGET, min(100.0, total / TARGET * 100)))
    print("Sisa      : %d CXP lagi menuju early access" % max(0, TARGET - total))
    print("Kode ref  : %s" % (state["invite_code"] or "(belum diisi — lihat halaman Invite)"))
    print()
    print("Misi sekali (selesai %d/6):" % len(state["done_once"]))
    for code, name, cxp, kind in MISSIONS:
        if kind != "sekali":
            continue
        mark = "[x]" if code in state["done_once"] else "[ ]"
        print("  %s %-14s +%-5d %s" % (mark, code, cxp, name))
    print("Misi harian hari ini (%s, selesai %d/6):" % (today(), len(state["done_daily"].get(today(), []))))
    done_today = state["done_daily"].get(today(), [])
    for code, name, cxp, kind in MISSIONS:
        if kind != "harian":
            continue
        mark = "[x]" if code in done_today else "[ ]"
        print("  %s %-14s +%-5d %s" % (mark, code, cxp, name))
    print("Misi sosial (selesai %d/6):" % sum(1 for m in MISSIONS if m[3] == "sosial" and m[0] in state["done_once"]))
    for code, name, cxp, kind in MISSIONS:
        if kind != "sosial":
            continue
        mark = "[x]" if code in state["done_once"] else "[ ]"
        print("  %s %-14s +%-5d %s" % (mark, code, cxp, name))
    print()
    print("Catatan: Convert CXP masih Coming soon (belum bisa WD).")
    print("Misi harian reset tiap 00:00 UTC.")


def menu():
    state = load_state()
    while True:
        print()
        print("===== CRYPTONIA CITY =====")
        print("CXP kamu: %d / %d" % (total_cxp(state), TARGET))
        print("[1] Lihat semua misi + progres")
        print("[2] Tandai misi selesai")
        print("[3] Isi kode referral kamu")
        print("[0] Keluar")
        choice = input("Pilih: ").strip()
        if choice == "0":
            print("Sampai jumpa — gas kumpulin CXP!")
            return
        if choice == "1":
            show_status(state)
            continue
        if choice == "3":
            code = input("Kode referral kamu (mis. CITY-XXXX): ").strip()
            state["invite_code"] = code
            save_state(state)
            print("Kode referral disimpan.")
            continue
        if choice == "2":
            show_status(state)
            code = input("Kode misi yang selesai (mis. x-follow): ").strip()
            by_code = {m[0]: m for m in MISSIONS}
            if code not in by_code:
                print("Kode misi tidak dikenal.")
                continue
            _c, _n, _x, kind = by_code[code]
            if kind == "harian":
                day = today()
                done = state["done_daily"].setdefault(day, [])
                if code in done:
                    print("Misi ini sudah ditandai hari ini.")
                else:
                    done.append(code)
                    save_state(state)
                    print("Ditandai selesai (+%d CXP)." % _x)
            else:
                if code in state["done_once"]:
                    print("Misi ini sudah ditandai selesai.")
                else:
                    state["done_once"].append(code)
                    save_state(state)
                    print("Ditandai selesai (+%d CXP)." % _x)
            continue
        print("Pilihan tidak dikenal.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_status(load_state())
    else:
        menu()
