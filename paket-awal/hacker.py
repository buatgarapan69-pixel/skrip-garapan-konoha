#!/usr/bin/env python3
"""hacker.py v10 — MARKAS TIM KONOHA • CYBER EDITION.
Skrip terminal interaktif Markas (kode dasar kiriman user 20 Nov 18:49 WIB)
+ STATUS LIVE channel & grup via Telethon (fitur asli hacker.py).
Banner FIGlet KONOHA (merah), animasi loading, efek ketik, menu utama.

Jalankan:  python3 hacker.py
Diletakkan di folder tools (sejajar session/), session dir
terdeteksi otomatis (sessionutama/ / ../session/ / session/).
"""
import asyncio
import os
import platform
import random
import re
import shutil
import sys
import time
from datetime import datetime

# ==================================
#       MARKAS TIM KONOHA
#         CYBER EDITION
# ==================================
# SKEMA WARNA (user 20 Nov 18:55 WIB):
#   MERAH + KUNING = DANGER (banner KONOHA, garis, laporan darurat,
#                            warning [!], error, prioritas tinggi)
#   HIJAU + BIRU   = HACKER (system online, loading, menu, prompt,
#                            info, ID, sukses/DONE)
#   HITAM + PUTIH  = seperlunya (latar hitam, teks/label utama putih)

R = "\033[91m"
RED = "\033[38;5;196m"
DRED = "\033[38;5;124m"
W = "\033[97m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
M = "\033[95m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

WIDTH = min(shutil.get_terminal_size((80, 24)).columns, 85)
MAXW = 46  # lebar konten aman buat layar HP (Termius)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def line(char="━", color=RED):
    print(color + char * WIDTH + RESET)


def center(text, color=R):
    print(color + text.center(WIDTH) + RESET)


def slow(text, color=W, delay=0.018):
    for char in text:
        print(color + char + RESET, end="", flush=True)
        time.sleep(delay)
    print()


def loading(text, duration=1.5):
    print(G + "\n  [*] " + W + text + RESET)
    frames = ["[■□□□□□□□□□]", "[■■□□□□□□□□]",
              "[■■■□□□□□□□]", "[■■■■□□□□□□]",
              "[■■■■■□□□□□]", "[■■■■■■□□□□]",
              "[■■■■■■■□□□]", "[■■■■■■■■□□]",
              "[■■■■■■■■■□]", "[■■■■■■■■■■]"]

    for frame in frames:
        print("\r  " + G + frame + RESET, end="", flush=True)
        time.sleep(duration / len(frames))

    print(G + "  DONE ✓" + RESET)


def banner():
    clear()

    art = [
        "██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗ ██╗  ██╗ █████╗",
        "██║ ██╔╝██╔═══██╗████╗  ██║██╔═══██╗██║  ██║██╔══██╗",
        "█████╔╝ ██║   ██║██╔██╗ ██║██║   ██║███████║███████║",
        "██╔═██╗ ██║   ██║██║╚██╗██║██║   ██║██╔══██║██╔══██║",
        "██║  ██╗╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║██║  ██║",
        "╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝"
    ]

    print()
    for row in art:
        center(row, RED)
        time.sleep(0.07)

    print()
    center("☠  MARKAS TIM KONOHA  ☠", W)
    center("HACKER BY ADMIN KONOHA", G)
    center("[ DARK CYBER NETWORK ]", C)
    print()
    line()


def startup():
    banner()
    loading("INITIALIZING CYBER TERMINAL")
    loading("LOADING KONOHA INTERFACE")
    loading("CHECKING LOCAL SYSTEM")
    slow("\n  [✓] SYSTEM READY", G)
    time.sleep(0.5)


# ══════════════════ STATUS LIVE (Telethon) ══════════════════
# Fitur asli hacker.py: status LIVE channel & grup Markas.
CHANNEL_ID = 4343223926
GROUP_ID = 3623838704


def _find_session_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [
        os.path.join(here, "sessionutama"),
        os.path.join(here, "..", "session"),
        os.path.join(here, "session"),
        os.path.join(os.path.expanduser("~"), "konoha", "session"),
        os.path.join("/root", "hatake", "session"),
    ]
    for d in cands:
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "Naruto.session")):
            return os.path.abspath(d)
    return None


def _resolve_api():
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from apicred import resolve
        return resolve("Naruto")
    except Exception:
        pass
    for p in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt"),
              os.path.join(os.path.expanduser("~"), "konoha", "tools", "config.txt")):
        try:
            with open(p) as f:
                vals = {}
                for ln in f:
                    if "=" in ln:
                        k, v = ln.strip().split("=", 1)
                        vals[k.strip()] = v.strip()
                return int(vals["API_ID"]), vals["API_HASH"]
        except Exception:
            continue
    return 0, "ISI_API_HASH_KAMU"  # isi api_id / api_hash sendiri di apicred.py atau config.txt


def _clean_preview(text, n=MAXW):
    if not text:
        return "-"
    t = text.replace("\n", " ")
    t = re.sub(r"```", "", t)
    t = re.sub(r"[═─]{3,}", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


async def _fetch_status():
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.tl.functions.messages import GetFullChatRequest
    from telethon.tl.types import InputMessagesFilterPinned

    sdir = _find_session_dir()
    if not sdir:
        return {"error": "Session Naruto tidak ditemukan."}
    api_id, api_hash = _resolve_api()
    tmp = "/tmp/hacker_naruto"
    try:
        import shutil as _sh
        _sh.copyfile(os.path.join(sdir, "Naruto.session"), tmp + ".session")
    except Exception as e:
        return {"error": f"Gagal salin session: {e}"}
    data = {}
    try:
        async with TelegramClient(tmp, api_id, api_hash) as c:
            me = await c.get_me()
            data["login"] = "@" + (me.username or str(me.id))
            for label, pid in (("channel", CHANNEL_ID), ("grup", GROUP_ID)):
                try:
                    ent = await c.get_entity(pid)
                    about = ""
                    members = "-"
                    if label == "channel":
                        full = await c(GetFullChannelRequest(ent))
                        about = full.full_chat.about or ""
                        members = full.full_chat.participants_count
                    else:
                        full = await c(GetFullChatRequest(pid))
                        about = full.full_chat.about or ""
                        members = full.full_chat.participants_count
                    pinned = []
                    async for m in c.iter_messages(ent, filter=InputMessagesFilterPinned, limit=5):
                        pinned.append(m.id)
                    recent = []
                    async for m in c.iter_messages(ent, limit=3):
                        if m.photo or m.media:
                            txt = "GAMBAR"
                        elif m.message:
                            txt = _clean_preview(m.message)
                        else:
                            txt = "-"
                        recent.append((m.id, txt))
                    data[label] = {
                        "title": getattr(ent, "title", "-"),
                        "about": about,
                        "members": members,
                        "pinned": pinned,
                        "recent": recent,
                    }
                except Exception as e:
                    data[label] = {"error": str(e)[:60]}
    except Exception as e:
        return {"error": str(e)[:80]}
    finally:
        for suf in (".session", ".session-journal"):
            try:
                os.remove(tmp + suf)
            except Exception:
                pass
    return data


def status_live():
    banner()
    center("STATUS LIVE MARKAS", G)
    line()
    print(G + "\n  [*] " + W + "Mengambil status live channel & grup..." + RESET)
    data = asyncio.run(_fetch_status())
    if data.get("error"):
        print(f"\n  {R}[-] {data['error']}{RESET}")
        input("\n  Tekan ENTER untuk kembali...")
        return
    print(f"\n  {W}Login : {G}{data.get('login', '-')}{RESET}")
    for label, emoji in (("channel", "📌"), ("grup", "👥")):
        d = data.get(label)
        if not d:
            continue
        print(f"\n  {C}{BOLD}{emoji} {label.upper()}{RESET}")
        if d.get("error"):
            print(f"  {R}[-] {d['error']}{RESET}")
            continue
        print(f"  {W}Nama   : {W}{_clean_preview(str(d['title']))}{RESET}")
        print(f"  {W}Tentang: {W}{_clean_preview(str(d['about']), MAXW - 9)}{RESET}")
        print(f"  {W}Member : {G}{d['members']}{RESET}")
        print(f"  {W}Pinned : {C}{', '.join(str(x) for x in d['pinned']) or '-'}{RESET}")
        for mid, txt in d.get("recent", []):
            print(f"  {C}#{mid} : {W}{txt}{RESET}")
    line()
    input("\n  Tekan ENTER untuk kembali...")


def system_info():
    banner()
    center("SYSTEM INFORMATION", G)
    line()

    info = [
        ("PLATFORM", platform.system()),
        ("DEVICE", platform.machine()),
        ("PYTHON", platform.python_version()),
        ("DATE", datetime.now().strftime("%d-%m-%Y")),
        ("TIME", datetime.now().strftime("%H:%M:%S")),
        ("STATUS", "TERMINAL ONLINE")
    ]

    for key, value in info:
        print(f"  {G}[+]{RESET} {W}{key:<12}{RESET}: {G}{value}{RESET}")
        time.sleep(0.15)

    line()
    input("\n  Tekan ENTER untuk kembali...")


def tools_menu():
    banner()
    center("CYBER TOOLKIT", G)
    line()

    options = [
        "Python Script Development",
        "Linux Command Learning",
        "Network Security Basics",
        "File Management",
        "Termux Customization"
    ]

    for i, item in enumerate(options, 1):
        print(f"  {G}[{i}]{RESET} {W}{item}{RESET}")

    line()
    print(C + "  TOOLKIT: EDUCATIONAL MODE" + RESET)
    input("\n  Tekan ENTER untuk kembali...")


def emergency():
    banner()
    center("LAPORAN DARURAT", RED)
    line()

    slow("  [!] MARKAS TIM KONOHA", R)
    slow("  [!] SILAKAN PERIKSA INFORMASI BERIKUT", Y)

    print()
    print(W + "  Waktu laporan : " +
          datetime.now().strftime("%d-%m-%Y %H:%M:%S") + RESET)
    print(W + "  Status        : MENUNGGU PEMERIKSAAN" + RESET)
    print(W + "  Prioritas     : TINGGI" + RESET)

    line()
    print(G + "\n  Laporan lokal berhasil ditampilkan." + RESET)
    input("\n  Tekan ENTER untuk kembali...")


def channel():
    banner()
    center("MARKAS TIM KONOHA", RED)
    line()

    print(W + """
  ☠ IDENTITAS CHANNEL ☠

  Nama     : MARKAS TIM KONOHA
  Divisi   : DARK CYBER NETWORK
  Admin    : ADMIN KONOHA

  INFORMASI:
  - Update dan pengumuman
  - Script dan tools edukasi
  - Keamanan digital
  - Laporan dan informasi server

  Motto:
  "STAY ALERT, STAY SECURE."
""" + RESET)

    line()
    input("\n  Tekan ENTER untuk kembali...")


def exit_program():
    banner()
    loading("SHUTTING DOWN TERMINAL")
    slow("\n  GOODBYE, MEMBER KONOHA ☠", G)
    print()
    sys.exit(0)


def main():
    startup()

    while True:
        banner()

        now = datetime.now()
        print(
            f"  {G}SYSTEM: ONLINE{RESET}"
            f"   {W}TIME: {now.strftime('%H:%M:%S')}{RESET}"
        )

        print(
            f"  {W}DEVICE: {platform.machine()}"
            f"   DATE: {now.strftime('%d-%m-%Y')}{RESET}"
        )

        line()

        center("MAIN MENU", G)
        print()

        menu = [
            ("01", "SYSTEM INFORMATION"),
            ("02", "CYBER TOOLKIT"),
            ("03", "LAPORAN DARURAT"),
            ("04", "CHANNEL INFORMATION"),
            ("05", "STATUS LIVE MARKAS"),
            ("06", "EXIT TERMINAL")
        ]

        for number, name in menu:
            print(f"  {G}[{number}]{RESET}  {W}{name}{RESET}")
            time.sleep(0.06)

        print()
        line()

        choice = input(
            f"\n  {G}➤ PILIH MENU {G}» {W}"
        ).strip()

        if choice == "1" or choice == "01":
            system_info()

        elif choice == "2" or choice == "02":
            tools_menu()

        elif choice == "3" or choice == "03":
            emergency()

        elif choice == "4" or choice == "04":
            channel()

        elif choice == "5" or choice == "05":
            status_live()

        elif choice == "6" or choice == "06":
            exit_program()

        else:
            slow("\n  [!] MENU TIDAK DIKENALI!", R)
            time.sleep(1)


try:
    main()

except KeyboardInterrupt:
    print(RESET + "\n\n  [!] TERMINAL DIHENTIKAN." + R)
    print(G + "  HACKER BY ADMIN KONOHA ☠" + RESET)
