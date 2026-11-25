import os
import sys
import time
import random
import shutil
import platform
from datetime import datetime

# ==================================
#       MARKAS TIM KONOHA
#         CYBER EDITION
# ==================================

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

def clear():
    os.system("clear")

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
    print(R + "\n  [*] " + W + text + RESET)
    frames = ["[■□□□□□□□□□]", "[■■□□□□□□□□]",
              "[■■■□□□□□□□]", "[■■■■□□□□□□]",
              "[■■■■■□□□□□]", "[■■■■■■□□□□]",
              "[■■■■■■■□□□]", "[■■■■■■■■□□]",
              "[■■■■■■■■■□]", "[■■■■■■■■■■]"]

    for frame in frames:
        print("\r  " + RED + frame + RESET, end="", flush=True)
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
    center("HACKER BY ADMIN KONOHA", RED)
    center("[ DARK CYBER NETWORK ]", GRAY)
    print()
    line()

def startup():
    banner()
    loading("INITIALIZING CYBER TERMINAL")
    loading("LOADING KONOHA INTERFACE")
    loading("CHECKING LOCAL SYSTEM")
    slow("\n  [✓] SYSTEM READY", G)
    time.sleep(0.5)

def system_info():
    banner()
    center("SYSTEM INFORMATION", RED)
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
        print(f"  {R}[+]{RESET} {W}{key:<12}{RESET}: {G}{value}{RESET}")
        time.sleep(0.15)

    line()
    input("\n  Tekan ENTER untuk kembali...")

def tools_menu():
    banner()
    center("CYBER TOOLKIT", RED)
    line()

    options = [
        "Python Script Development",
        "Linux Command Learning",
        "Network Security Basics",
        "File Management",
        "Termux Customization"
    ]

    for i, item in enumerate(options, 1):
        print(f"  {RED}[{i}]{RESET} {W}{item}{RESET}")

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
    slow("\n  GOODBYE, MEMBER KONOHA ☠", RED)
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
            f"  {GRAY}DEVICE: {platform.machine()}"
            f"   DATE: {now.strftime('%d-%m-%Y')}{RESET}"
        )

        line()

        center("MAIN MENU", RED)
        print()

        menu = [
            ("01", "SYSTEM INFORMATION"),
            ("02", "CYBER TOOLKIT"),
            ("03", "LAPORAN DARURAT"),
            ("04", "CHANNEL INFORMATION"),
            ("05", "EXIT TERMINAL")
        ]

        for number, name in menu:
            print(f"  {RED}[{number}]{RESET}  {W}{name}{RESET}")
            time.sleep(0.06)

        print()
        line()

        choice = input(
            f"\n  {G}➤ PILIH MENU {RED}» {W}"
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
            exit_program()

        else:
            slow("\n  [!] MENU TIDAK DIKENALI!", R)
            time.sleep(1)

try:
    main()

except KeyboardInterrupt:
    print(RESET + "\n\n  [!] TERMINAL DIHENTIKAN." + R)
    print("  HACKER BY ADMIN KONOHA ☠" + RESET)
