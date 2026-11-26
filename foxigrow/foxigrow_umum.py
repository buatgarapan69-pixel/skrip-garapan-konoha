#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FOXIGROW — Task Sosmed Dibayar USDT (versi umum, 1 perintah).
Bot: @FoxiTaskbot — kerjain tugas sosmed (follow X/TikTok, join grup TG,
Reddit, nonton YouTube) dibayar USDT. GRATIS, tanpa deposit.

CARA PAKAI (1 perintah):
    python3 foxigrow_umum.py
Lalu pilih menu di dalam: [1] Daftar + check-in, [2] Cek saldo & referral,
[3] Lihat daftar quest, [4] Coba klaim quest, [5] WD (kalau saldo >= $2),
[6] Keluar.

BUTUH:
- pip install telethon
- File apicred.json di folder yang sama, isi api_id/api_hash kamu dari
  https://my.telegram.org :
    {"api_id": 12345678, "api_hash": "abc123..."}
  Saat pertama jalan, masukkan nomor HP + kode login Telegram. Sesi login
  tersimpan lokal (foxigrow_session.session) — JANGAN disebar ke orang lain.
- REF_CODE (di bawah): user id Telegram pemberi referral, boleh kosong "".
- WD_ADDRESS (di bawah): alamat BEP20 USDT kamu, isi sebelum WD.

CATATAN JUJUR (dicek langsung 26 Nov 2026):
- Min WD $2 USDT (fee 5% kalau WD < $5, gratis kalau >= $5).
- Klaim quest BUTUH captcha Turnstile — skrip ini TIDAK BISA menyelesaikannya;
  kalau klaim mengembalikan CAPTCHA_REQUIRED, buka Mini App Foxigrow di HP
  dan klaim dari sana.
- Sebagian besar quest butuh akun sosmed di-bind dulu (X/TikTok/IG/FB/YouTube)
  dan verifikasi (mis. retweet dulu) — bind dilakukan di dalam Mini App.
- Check-in harian BISA lewat skrip ini (dapat FG Coin tiap hari).
- Payout BELUM terbukti cair (saldo USDT 0 saat pengecekan pertama).
"""
import asyncio
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

BASE = "https://api-user.foxigrow.com/api/v1"
BOT = "FoxiTaskbot"
UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")

# ---- ISI DULU SEBELUM PAKAI ----
REF_CODE = ""        # user id Telegram pemberi referral, contoh: "123456789"
WD_ADDRESS = ""      # alamat BEP20 USDT kamu, contoh: "0x..."
PROXY_URL = ""       # kosong = jalan langsung; isi "http://user:pass@host:port" kalau mau proxy
# ---------------------------------

SESSION_FILE = "foxigrow_session.session"
INITDATA_FILE = "foxigrow_initdata.txt"


def http(method, path, token=None, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"User-Agent": UA, "Locale": "en"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    opener = urllib.request.build_opener()
    if PROXY_URL:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY_URL, "https": PROXY_URL}))
    try:
        with opener.open(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "ignore"))
        except Exception:
            return e.code, {"error": str(e)}


class Foxi:
    def __init__(self):
        self.token = None
        self.user = None

    def login(self):
        initdata = None
        if os.path.exists(INITDATA_FILE):
            initdata = open(INITDATA_FILE).read().strip()
        if not initdata:
            initdata = asyncio.run(self._webview_initdata())
            if initdata:
                open(INITDATA_FILE, "w").write(initdata)
        if not initdata:
            print("Gagal dapat initData dari WebView.")
            return False
        st, j = http("POST", "/auth/telegram", body={"initData": initdata})
        if not j.get("token"):
            print("Auth gagal (initData mungkin kedaluwarsa). Hapus %s lalu ulangi."
                  % INITDATA_FILE)
            try:
                os.remove(INITDATA_FILE)
            except OSError:
                pass
            return False
        self.token = j["token"]
        self.user = j.get("user") or {}
        print("Login OK: @%s (Foxigrow user #%s)"
              % (self.user.get("username"), self.user.get("id")))
        return True

    async def _webview_initdata(self):
        from telethon import TelegramClient
        from telethon.tl.types import InputPeerUser, InputUser
        from telethon.tl.functions.messages import RequestWebViewRequest
        if not os.path.exists("apicred.json"):
            print("Buat apicred.json dulu (lihat petunjuk di atas skrip).")
            return None
        cred = json.load(open("apicred.json"))
        client = TelegramClient(SESSION_FILE, int(cred["api_id"]), str(cred["api_hash"]))
        await client.start()
        try:
            me = await client.get_me()
            print("Telegram login: @%s (%s)" % (me.username, me.id))
            ent = await client.get_entity(BOT)
            param = ("ref_" + REF_CODE) if REF_CODE else ""
            await client.send_message(ent, "/start " + param if param else "/start")
            await asyncio.sleep(8)
            res = await client(RequestWebViewRequest(
                peer=InputPeerUser(ent.id, ent.access_hash),
                bot=InputUser(ent.id, ent.access_hash), platform="android",
                from_bot_menu=True, url="https://t.me/%s/app" % BOT))
            frag = urllib.parse.urlparse(res.url).fragment
            return urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        finally:
            await client.disconnect()

    def checkin(self):
        st, j = http("POST", "/checkin", self.token, {"timezoneOffset": -420})
        print("Check-in:", json.dumps(j, ensure_ascii=False)[:300])

    def balance(self):
        st, j = http("GET", "/payout/balance", self.token)
        b = (j.get("balances") or {})
        print("Saldo: USDT %s | FG Coin %s | TON %s | Stars %s" % (
            b.get("usdt"), b.get("points"), b.get("ton"), b.get("stars")))
        print("Min WD: $%s | fee: %s%% (gratis kalau WD >= $%s)" % (
            j.get("minWithdrawAmount"), (j.get("feeRate") or 0) * 100,
            j.get("feeFreeThreshold")))
        print("Quest selesai: %s" % j.get("totalCompletedQuests"))
        st, inv = http("GET", "/invite/status", self.token)
        print("Referral: %s teman | link: %s" % (
            inv.get("inviteCount"), inv.get("inviteLink")))
        print("Komisi referral: %s%% dari penghasilan teman" % (
            inv.get("currentCommissionRate")))
        return j

    def quests(self):
        st, j = http("GET", "/quests?lang=en&page=1&pageSize=50", self.token)
        items = j.get("items", []) if isinstance(j, dict) else []
        print("Total quest tersedia: %s" % len(items))
        for q in items[:30]:
            r = q.get("reward") or {}
            print("#%s | %s | %s | $%s + %s FG" % (
                q.get("id"), (q.get("title") or "")[:45], q.get("platform"),
                r.get("amount"), r.get("points")))
        return items

    def claim(self, qid):
        st, j = http("POST", "/quests/%s/claim" % qid, self.token,
                     {"forceReclaim": False})
        if j.get("captchaRequired"):
            print("CAPTCHA_REQUIRED: klaim quest #%s butuh captcha Turnstile." % qid)
            print("Buka Mini App Foxigrow di HP kamu dan klaim dari sana.")
        elif j.get("success"):
            print("Klaim BERHASIL: %s" % json.dumps(j, ensure_ascii=False)[:300])
        else:
            print("Klaim gagal: %s" % json.dumps(j, ensure_ascii=False)[:400])

    def withdraw(self):
        st, j = http("GET", "/payout/balance", self.token)
        usdt = ((j.get("balances") or {}).get("usdt") or 0)
        min_wd = j.get("minWithdrawAmount") or 2
        print("Saldo USDT: %s (min WD $%s)" % (usdt, min_wd))
        if usdt < min_wd:
            print("Belum cukup untuk WD.")
            return
        if not WD_ADDRESS:
            print("Isi WD_ADDRESS dulu di dalam skrip (alamat BEP20 USDT kamu).")
            return
        amount = input("Jumlah WD (USDT, min %s): " % min_wd).strip()
        ok = input("WD %s USDT ke %s ? ketik YA: " % (amount, WD_ADDRESS)).strip()
        if ok != "YA":
            print("Dibatalkan.")
            return
        st, r = http("POST", "/payout/withdraw", self.token,
                     {"asset": "USDT", "amount": float(amount), "toAddress": WD_ADDRESS})
        print("Hasil WD:", json.dumps(r, ensure_ascii=False)[:500])


def menu():
    print("=" * 40)
    print("FOXIGROW — Task Sosmed Dibayar USDT")
    print("=" * 40)
    print("[1] Daftar + check-in harian")
    print("[2] Cek saldo & referral")
    print("[3] Lihat daftar quest")
    print("[4] Coba klaim quest (butuh captcha di HP)")
    print("[5] WD USDT (kalau saldo >= $2)")
    print("[6] Keluar")


def main():
    fx = Foxi()
    if not fx.login():
        return
    while True:
        menu()
        p = input("➤ PILIH MENU » ").strip()
        if p == "1":
            fx.checkin()
        elif p == "2":
            fx.balance()
        elif p == "3":
            fx.quests()
        elif p == "4":
            qid = input("ID quest (mis. 31610): ").strip()
            if qid:
                fx.claim(qid)
        elif p == "5":
            fx.withdraw()
        elif p == "6":
            print("Selesai. Sampai jumpa!")
            break
        else:
            print("Pilihan tidak dikenal.")
        print()


if __name__ == "__main__":
    main()
