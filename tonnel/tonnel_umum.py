#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TONEL MINNING — skrip umum (publik, tanpa kredensial).

Bot Telegram mining TONNEL (@TonnelNetworkGameBot): mining 6 jam sekali,
lucky spin harian, task react + join channel, referral.
- Bot: @TonnelNetworkGameBot — Mini App di https://tonnelnetwork.online/
- Earn: mining gratis 0,0042 TONNEL/jam (siklus 6 jam = 0,0252/siklus),
  lucky spin harian, task react +0,05 / join channel +0,1 TONNEL,
  referral +0,1 TONNEL/teman (selesai task) dan +1 TONNEL + 1 spin
  kalau teman verifikasi.
- VERIFIKASI BERBAYAR: akun harus verifikasi sekali dengan bayar 0,05 TON
  dari wallet TON yang terhubung ke bot — baru mining terbuka. Ini BUKAN
  gratisan penuh; hitung dulu sebelum bayar.
- Min WD: 10–20 TONNEL (~$2,08 pada 1 TONNEL = $0,2078) ke wallet TON
  yang terhubung. Payout BELUM terbukti cair (proyek baru, launch 26 Nov 2026).
  Perkiraan grind Naruto-only: ~0,2 TONNEL/hari → ~49 hari ke min WD.

CARA PAKAI — 1 PERINTAH:
  python3 tonnel_umum.py
Lalu pilih menu di dalam:
  [1] Daftar + login (ambil initData dari WebView bot)
  [2] Daily run (mining + spin + task + cek WD)
  [3] Cek status saja
  [4] Keluar

CARA KERJA MENU [1]:
  1. Skrip kirim /start ke bot (isi REF_CODE = user id Telegram pemberi
     referral kalau ada — boleh kosong "").
  2. Skrip buka WebView bot, ambil initData (disimpan lokal di
     tonnel_initdata.txt — JANGAN disebar ke orang lain).
  3. Login ke server, lalu hubungkan wallet TON + verifikasi 0,05 TON
     dari dalam Mini App (langkah ini manual di aplikasi Telegram).

KREDENSIAL (milikmu sendiri, TIDAK ada di skrip ini):
  1. Buka https://my.telegram.org -> API development tools -> buat app.
  2. Buat file apicred.json di folder yang sama, isinya:
     {"api_id": 12345678, "api_hash": "abc123..."}
  3. Jalankan skrip, masukkan nomor HP + kode login Telegram saat diminta.
  Sesi login tersimpan lokal (tonnel_session.session) — JANGAN disebar.

ISI DULU SEBELUM PAKAI (di bawah):
  REF_CODE = user id Telegram pemberi referral (boleh kosong "")

PERINGATAN: verifikasi 0,05 TON itu biaya nyata dan TIDAK bisa kembali.
Payout belum terbukti — jangan verifikasi banyak akun sekaligus sebelum
ada bukti WD pertama yang landing. Satu perangkat = satu akun.
"""
import asyncio
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar

REF_CODE = ""  # <-- isi user id Telegram pemberi referral, boleh kosong ""

BASE = "https://tonnelnetwork.online/"
BOT = "TonnelNetworkGameBot"
APP_URL = "https://t.me/TonnelNetworkGameBot/app"
UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36"}
OUT = "tonnel_daily.json"
INITDATA_FILE = "tonnel_initdata.txt"
SESSION_FILE = "tonnel_session"
MIN_WD = 10.0


def wib_now():
    return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(time.time() + 7 * 3600))


def load_apicred():
    try:
        d = json.load(open("apicred.json"))
        return int(d["api_id"]), str(d["api_hash"])
    except Exception:
        print("  [!] apicred.json tidak ada — buat dulu dari https://my.telegram.org")
        print("      Isi: {\"api_id\": 12345678, \"api_hash\": \"abc123...\"}")
        return None, None


def vis(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


class Tonnel:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.initdata = None

    def post(self, path, data):
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(BASE + path, data=body, headers={
            **UA, "Content-Type": "application/x-www-form-urlencoded",
            "Referer": BASE + "home.php", "Origin": BASE.rstrip("/")})
        try:
            with self.opener.open(req, timeout=25) as r:
                return {"http": r.status, "body": r.read().decode("utf-8", "ignore")}
        except urllib.error.HTTPError as e:
            return {"http": e.code, "body": e.read().decode("utf-8", "ignore")[:2000]}
        except Exception as e:
            return {"error": "%s: %s" % (type(e).__name__, e)}

    def get(self, path):
        req = urllib.request.Request(BASE + path, headers={**UA, "Referer": BASE + "home.php"})
        try:
            with self.opener.open(req, timeout=25) as r:
                return {"http": r.status, "body": r.read().decode("utf-8", "ignore")}
        except urllib.error.HTTPError as e:
            return {"http": e.code, "body": e.read().decode("utf-8", "ignore")[:2000]}
        except Exception as e:
            return {"error": "%s: %s" % (type(e).__name__, e)}

    def login(self):
        r = self.post("index.php", {"login": "true", "init_data": self.initdata, "ref_by": ""})
        return (r.get("body") or "").strip() == "done"

    def refresh_initdata(self):
        """Ambil initData fresh via Telethon WebView (sesi lokal sendiri)."""
        from telethon import TelegramClient
        from telethon.tl.types import InputPeerUser, InputUser
        from telethon.tl.functions.messages import StartBotRequest, RequestWebViewRequest
        from urllib.parse import urlparse, parse_qs
        api_id, api_hash = load_apicred()
        if not api_id:
            raise RuntimeError("apicred.json belum dibuat")
        client = TelegramClient(SESSION_FILE, api_id, api_hash)
        client.start()
        try:
            me = client.get_me()
            print("  Akun: %s @%s id=%s" % (me.first_name, me.username, me.id))
            ent = client.get_entity(BOT)
            peer = InputPeerUser(ent.id, ent.access_hash)
            client(StartBotRequest(bot=InputUser(ent.id, ent.access_hash), peer=peer,
                                   random_id=int(time.time() * 1000),
                                   start_param=REF_CODE or "start"))
            res = client(RequestWebViewRequest(peer=peer, bot=InputUser(ent.id, ent.access_hash),
                                              platform="android", from_bot_menu=True, url=APP_URL))
            q = parse_qs(urlparse(res.url).fragment)
            initdata = q.get("tgWebAppData", [None])[0]
            if not initdata:
                raise RuntimeError("WebView tidak mengembalikan initData")
            open(INITDATA_FILE, "w").write(initdata)
            self.initdata = initdata
            print("  [✓] initData disimpan di %s" % INITDATA_FILE)
        finally:
            client.disconnect()

    def ensure_login(self):
        try:
            self.initdata = open(INITDATA_FILE).read().strip()
        except Exception:
            self.initdata = None
        if self.initdata and self.login():
            return True
        print("  [!] login initData lama gagal — refresh via WebView...")
        try:
            self.refresh_initdata()
        except Exception as e:
            print("  [x] refresh initData gagal: %s" % e)
            return False
        return self.login()

    def balance(self):
        h = self.get("pages/home.php")
        t = vis(h.get("body") or "")
        m = re.search(r"Your TONNEL Balance\s*([\d.]+)", t)
        bal = float(m.group(1)) if m else None
        p = self.get("pages/profile.php")
        pt = vis(p.get("body") or "")
        verified = "Account Verified" in pt
        m2 = re.search(r"Available balance\s*([\d.]+)", pt)
        if m2:
            bal = float(m2.group(1))
        return {"balance": bal, "verified": verified,
                "mining": re.search(r"Mining Rate\s*([\d.]+)\s*/hr", t).group(1) if re.search(r"Mining Rate\s*([\d.]+)\s*/hr", t) else None}


def daily():
    t = Tonnel()
    out = {"started_at": wib_now()}
    if not t.ensure_login():
        out["error"] = "login gagal"
        json.dump(out, open(OUT, "w"), indent=2)
        print("  [x] LOGIN GAGAL")
        return out
    print("  [✓] Login OK")
    before = t.balance()
    out["before"] = before
    print("  Saldo awal: %s TONNEL | Verified: %s" % (before.get("balance"), before.get("verified")))
    if not before.get("verified"):
        print("  [!] Akun BELUM terverifikasi — verifikasi 0,05 TON dulu dari Mini App,")
        print("      baru mining bisa jalan. Daily run dihentikan di sini.")
        out["note"] = "belum terverifikasi — verifikasi 0,05 TON dulu dari Mini App"
        json.dump(out, open(OUT, "w"), indent=2)
        return out
    r = t.post("pages/home.php", {"action": "start_mining"})
    out["start_mining"] = r
    print("  Mining:", (r.get("body") or "")[:200])
    r = t.post("pages/tasks.php", {"action": "lucky_spin"})
    out["lucky_spin"] = r
    print("  Spin:", (r.get("body") or "")[:200])
    for tid in (2, 3):
        r = t.post("pages/tasks.php", {"action": "claim_task", "task_id": str(tid)})
        out["claim_task_%d" % tid] = r
        print("  Task %d:" % tid, (r.get("body") or "")[:200])
    after = t.balance()
    out["after"] = after
    print("  Saldo akhir: %s TONNEL | Verified: %s" % (after.get("balance"), after.get("verified")))
    bal = after.get("balance") or 0
    if bal >= MIN_WD:
        print("  [!] Saldo >= min WD 10 — coba WD 10 TONNEL ke wallet yang terhubung...")
        r = t.post("pages/profile.php", {"action": "submit_withdraw", "amount": 10})
        out["withdraw"] = r
        print("  WD:", (r.get("body") or "")[:300])
    else:
        out["withdraw"] = "belum cukup (%.2f/10 TONNEL)" % bal
        print("  WD: belum cukup (%.2f/10 TONNEL)" % bal)
    json.dump(out, open(OUT, "w"), indent=2)
    print("  [✓] SELESAI — %s" % OUT)
    return out


def status():
    t = Tonnel()
    if not t.ensure_login():
        print("  [x] LOGIN GAGAL")
        return
    b = t.balance()
    print("  Saldo TONNEL: %s" % b.get("balance"))
    print("  Verified: %s" % b.get("verified"))
    print("  Mining rate: %s /jam" % b.get("mining"))


def main():
    print("  ============================================================")
    print("  TONEL MINNING — skrip umum (tanpa kredensial)")
    print("  ============================================================")
    print("  [1] Daftar + login (ambil initData dari WebView bot)")
    print("  [2] Daily run (mining + spin + task + cek WD)")
    print("  [3] Cek status saja")
    print("  [4] Keluar")
    try:
        pil = input("  ➤ PILIH MENU » ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return
    if pil == "1":
        t = Tonnel()
        try:
            t.refresh_initdata()
        except Exception as e:
            print("  [x] Gagal: %s" % e)
            return
        print("  Login ke server:", "OK" if t.login() else "GAGAL")
        print("  Status:", t.balance())
    elif pil == "2":
        daily()
    elif pil == "3":
        status()
    else:
        print("  Keluar.")


if __name__ == "__main__":
    main()
