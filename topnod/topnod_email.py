#!/usr/bin/env python3
"""
topnod_email.py — Temp email buat TopNod, SATU perintah, pilih opsi di dalam.
Jalanin:  python topnod_email.py
SUMBER EMAIL: generator.email (BUKAN tempmail.world).
  - TopNod kirim OTP ke <nama>@<domain> — inbox-nya dihost generator.email.
# Contoh alamat: <alamat-email-sementara-Anda>
# (pakai domain email sementara apa saja)
  - Cara baca: GET https://generator.email/<email> (HTML inbox, server-side).
  - OTP TopNod ada di subject: "Your verification code: 390237" (6 digit).
  - TIDAK perlu akun/token — alamat email apa aja di domain yang didukung
    langsung punya inbox.
  - CATATAN: generator.email kadang 503/rate-limit (apalagi dari IP datacenter).
    Skrip sudah retry otomatis + jeda 10 detik tiap poll. Paling stabil
    dijalankan dari HP (Termux, IP seluler) — bukan dari VPS.
BEDANYA DARI SKRIP LAMA (tempmail_termux.py / msg 2184):
  - Sumber email generator.email (yang TEMBUS TopNod), bukan tempmail.world.
  - Setelah OTP ketemu, email TIDAK dihapus, TIDAK ganti otomatis.
  - Semua OTP disimpan ke file (bisa dibaca ulang kapan aja).
  - Semua opsi ada di MENU dalam skrip — satu perintah, gak perlu hafal flag.
"""
import re
import json
import time
import subprocess
import sys
import os
import random
import string
import http.cookiejar
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

EMAIL_FILE = Path.home() / ".topnod_email.json"
OTP_FILE   = Path.home() / ".topnod_otps.json"
GEN = "https://generator.email"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# Domain temp email yang dipakai buat TopNod (disinkron sama register script).
# JANGAN pakai: mriscanner.live, euploading.com, supplementwiki.org,
# airdropnusantara.xyz (throttled).
DOMAINS = [
    "webinarmoa.com", "appcloudmurah.email", "maillasd1.trade", "samvix.life",
    "lcould.kr", "arkoo.site", "senacloud.email", "maizystore.me", "makoli.site",
    "lokoiat.top", "phubt.com", "omg-greatfood.com", "zelia.uk", "ahrixthinh.net",
    "contactpage.online", "automizely.info", "ccategoryk.com", "hkvtop.us",
    "sadove.shop", "vipregclone.click", "megahazzam.online", "vntechhub.online",
    "insiderecholink.com", "leviacerman.store", "ryuucn.com", "milljack.com",
]

# ── Skema warna DANGER HACKER v15 ─────────────────────────────────────────────
RED    = "\033[91m"
DRED   = "\033[31m"
GOLD   = "\033[93m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner():
    try:
        w = os.get_terminal_size().columns
    except Exception:
        w = 80
    w = max(40, min(w, 80))
    print(f"{BOLD}{RED}{'#' * w}{RESET}")
    print(f"{BOLD}{RED}  EMAIL TOPNOD — GENERATOR.EMAIL{RESET}")
    print(f"{RED}  ☠ HACKER BY ADMIN KONOHA ☠{RESET}")
    print(f"{GOLD}  ⚠ EMAIL TETAP — OTP TERSIMPAN ⚠{RESET}")
    print(f"{BOLD}{RED}{'#' * w}{RESET}")

def clear():
    os.system("clear")

# ── Clipboard ─────────────────────────────────────────────────────────────────
def clip(text):
    for cmd in (
        ["termux-clipboard-set", text],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ):
        try:
            if cmd[0] in ("xclip", "xsel"):
                subprocess.run(cmd, input=text.encode(), check=True, timeout=3)
            else:
                subprocess.run(cmd, check=True, timeout=3)
            return True
        except Exception:
            continue
    return False

# ── Email aktif (TIDAK pernah dihapus otomatis) ───────────────────────────────
def save_email(email):
    EMAIL_FILE.write_text(json.dumps({"email": email}))

def load_email():
    if not EMAIL_FILE.exists():
        return None
    try:
        return json.loads(EMAIL_FILE.read_text()).get("email")
    except Exception:
        return None

def clear_email():
    # HANYA dipanggil kalau user pilih "Ganti email" di menu.
    EMAIL_FILE.unlink(missing_ok=True)

# ── OTP log (biar bisa dibaca ulang) ─────────────────────────────────────────
def load_otps():
    if not OTP_FILE.exists():
        return []
    try:
        return json.loads(OTP_FILE.read_text())
    except Exception:
        return []

def save_otp(email, otp, ts):
    log = load_otps()
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email": email,
        "otp": otp,
        "topnod_time": ts,
    }
    if any(e.get("otp") == otp and e.get("email") == email for e in log):
        return False
    log.append(entry)
    OTP_FILE.write_text(json.dumps(log, indent=2))
    return True

# ── generator.email — baca inbox + OTP TopNod ────────────────────────────────
# Subject TopNod + timestamp UTC di daftar pesan HTML.
OTP_RE = re.compile(
    r"Your verification code:\s*(\d{6})</div>"
    r'<div class="g8r time_div_45g45gg">([^<]+)</div>')
OTP_SIMPLE_RE = re.compile(r"Your verification code:\s*(\d{6})")
# Buat deteksi pesan baru (bukan cuma OTP) — tampilkan subject-nya.
SUBJECT_RE = re.compile(r'<div class="g8r subject_div_45g45gg">([^<]+)</div>')

def fetch_inbox(email, retries=3):
    """Ambil HTML inbox generator.email. Return (html) atau None kalau gagal.
    Retry 3x karena generator.email kadang 503 (flaky, terutama dari IP datacenter)."""
    for attempt in range(retries):
        try:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            req = urllib.request.Request(
                GEN + "/" + email,
                headers={"User-Agent": UA,
                         "Accept": "text/html,application/xhtml+xml",
                         "Accept-Language": "en-US,en;q=0.9"})
            with opener.open(req, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            if attempt < retries - 1:
                time.sleep(5 + attempt * 3)
    return None

def extract_otp(html):
    """Ambil OTP TopNod terbaru dari HTML inbox. Return (otp, timestamp) / (None, None)."""
    if not html:
        return None, None
    pairs = OTP_RE.findall(html)
    if pairs:
        pairs.sort(key=lambda p: p[1], reverse=True)
        return pairs[0][0], pairs[0][1]
    m = OTP_SIMPLE_RE.search(html)
    if m:
        return m.group(1), None
    return None, None

def extract_subjects(html):
    if not html:
        return []
    return SUBJECT_RE.findall(html)

# ── Bikin email ───────────────────────────────────────────────────────────────
def random_name(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def make_email():
    """Bikin email baru: user ketik nama (kosong = acak) + pilih domain."""
    print(f"\n{YELLOW}Nama email (contoh: konoha12). Kosong = acak.{RESET}")
    try:
        name = input(f"{BOLD}{RED}Nama: {RESET}").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return None
    if not name:
        name = "konoha" + "".join(random.choices(string.digits, k=2))
    name = re.sub(r"[^a-z0-9._-]", "", name) or random_name()
    print(f"\n{YELLOW}Pilih domain (Enter = acak dari {len(DOMAINS)} domain):{RESET}")
    for i, d in enumerate(DOMAINS, 1):
        print(f"  {RED}[{i}]{RESET} {d}")
    try:
        pick = input(f"{BOLD}{RED}Domain [1-{len(DOMAINS)} / Enter]: {RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    if pick.isdigit() and 1 <= int(pick) <= len(DOMAINS):
        dom = DOMAINS[int(pick) - 1]
    else:
        dom = random.choice(DOMAINS)
    email = f"{name}@{dom}"
    save_email(email)
    return email

# ── Aksi menu ─────────────────────────────────────────────────────────────────
def show_current_email():
    email = load_email()
    if email:
        print(f"\n{BOLD}{RED}[*]{RESET} Email aktif : {BOLD}{GOLD}{email}{RESET}")
        print(f"{YELLOW}[*] Inbox: {GEN}/{email}{RESET}")
        clip(email)
        print(f"{YELLOW}[*] Email disalin ke clipboard.{RESET}")
    else:
        print(f"\n{DRED}[-] Belum ada email. Pilih [1] buat bikin email baru.{RESET}")

def show_otps():
    log = load_otps()
    if not log:
        print(f"\n{DRED}[-] Belum ada OTP tersimpan.{RESET}")
        return
    print(f"\n{BOLD}{RED}══ DAFTAR OTP TERSIMPAN ══{RESET}")
    for e in log:
        print(f"{GOLD}[{e.get('time')}] {e.get('otp')}{RESET}  {YELLOW}| {e.get('email')}{RESET}")
    print(f"{BOLD}{RED}Total: {len(log)} OTP{RESET}")

def change_email():
    old = load_email()
    clear_email()
    print(f"{YELLOW}[!] Email lama dibuang: {old or '-'}{RESET}")
    print(f"{YELLOW}[*] OTP lama TETAP tersimpan (cek menu [3]).{RESET}")
    email = make_email()
    if email:
        print(f"\n{BOLD}{RED}[*]{RESET} Email baru : {BOLD}{GOLD}{email}{RESET}")
        clip(email)
        print(f"{YELLOW}[*] Email disalin ke clipboard.{RESET}")
    return email

def monitor():
    """Pantau inbox generator.email. Ctrl+C = balik ke menu (email + OTP tetap)."""
    email = load_email()
    if not email:
        print(f"{RED}[+] Belum ada email — bikin dulu.{RESET}")
        email = make_email()
        if not email:
            return
    print(f"\n{BOLD}{RED}[*]{RESET} Email aktif : {BOLD}{GOLD}{email}{RESET}")
    print(f"{YELLOW}[*] Inbox: {GEN}/{email}{RESET}")
    print(f"{YELLOW}[*] Email ini TETAP — tidak akan ganti/hapus otomatis.{RESET}")
    print(f"{YELLOW}[*] OTP tersimpan di {OTP_FILE}.{RESET}")
    print(f"{RED}{'─' * 50}{RESET}")
    print(f"{YELLOW}Menunggu OTP TopNod... (Ctrl+C = balik ke menu){RESET}\n")
    clip(email)
    seen = set()
    # Tandai OTP yang sudah ada biar tidak diumumkan ulang.
    html0 = fetch_inbox(email)
    otp0, _ = extract_otp(html0)
    if otp0:
        seen.add(otp0)
    try:
        while True:
            html = fetch_inbox(email)
            if html is None:
                print(f"{DRED}[-] Gagal ambil inbox (jaringan?). Coba lagi 10 detik...{RESET}")
                time.sleep(10)
                continue
            otp, ts = extract_otp(html)
            if otp and otp not in seen:
                seen.add(otp)
                saved = save_otp(email, otp, ts)
                print(f"\n{BOLD}{GOLD}{'═' * 50}{RESET}")
                print(f"{BOLD}{GOLD}  OTP TOPNOD TERDETEKSI!{RESET}")
                print(f"  Email   : {email}")
                if ts:
                    print(f"  Waktu   : {ts}")
                print(f"\n  {BOLD}{GOLD}  {otp}  {RESET}")
                print(f"{BOLD}{GOLD}{'═' * 50}{RESET}")
                clip(otp)
                if saved:
                    print(f"{GOLD}[+] OTP disalin ke clipboard + TERSIMPAN.{RESET}")
                else:
                    print(f"{YELLOW}[*] OTP disalin ke clipboard (sudah pernah tersimpan).{RESET}")
                print(f"{YELLOW}[*] Email TETAP {email} — lanjut pantau, tidak ganti otomatis.{RESET}\n")
                # *** TIDAK ada hapus email / ganti otomatis di sini. ***
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[*] Balik ke menu. Email + OTP tetap tersimpan.{RESET}")
        return

# ── Menu utama ────────────────────────────────────────────────────────────────
def menu():
    email = load_email()
    print(f"\n{BOLD}{RED}══ MENU ══{RESET}")
    if email:
        print(f"{YELLOW}Email aktif: {BOLD}{GOLD}{email}{RESET}")
    else:
        print(f"{YELLOW}Email aktif: {DRED}(belum ada){RESET}")
    print(f"{RED}[1]{RESET} Pantau inbox (tunggu OTP TopNod)")
    print(f"{RED}[2]{RESET} Ganti email baru")
    print(f"{RED}[3]{RESET} Lihat OTP tersimpan")
    print(f"{RED}[4]{RESET} Lihat email aktif")
    print(f"{RED}[5]{RESET} Keluar")
    try:
        return input(f"{BOLD}{RED}Pilih [1-5]: {RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return "5"

def main():
    clear()
    banner()
    print(f"{YELLOW}Satu perintah: python topnod_email.py — sumber generator.email (tembus TopNod).{RESET}")
    while True:
        choice = menu()
        if choice == "1":
            monitor()
        elif choice == "2":
            change_email()
        elif choice == "3":
            show_otps()
        elif choice == "4":
            show_current_email()
        elif choice == "5":
            print(f"\n{YELLOW}[*] Keluar. Email + OTP tetap tersimpan — jalanin lagi kapan aja.{RESET}")
            sys.exit(0)
        else:
            print(f"{DRED}[-] Pilihan tidak dikenal. Pilih 1-5.{RESET}")
        try:
            input(f"\n{YELLOW}Tekan Enter buat balik ke menu...{RESET}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}[*] Keluar.{RESET}")
            sys.exit(0)
        clear()
        banner()

if __name__ == "__main__":
    main()
