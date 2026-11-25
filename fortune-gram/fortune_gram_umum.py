#!/usr/bin/env python3
"""FORTUNE GRAM — skrip umum (publik, tanpa kredensial).

Bot Telegram penghasil GRAM: mining coin (web app), gratis, tanpa deposit.
- Bot: @fortune_grambot — daftar gratis, dapat 100 coin + 1 gift box.
- Earn: 100 coin = $0,02/hari (0,0002 USD/coin/hari, otomatis, tanpa klik).
- Gift box: hadiah 1-25 coin/box (welcome 1 box + 1 box tiap referral).
- Referral: +10 coin + 1 gift box tiap teman join pakai link kamu.
- Klaim profit (profit -> USD) min $0,001, klaim tiap hari.
- Min WD: $0,05, fee $0,025, WD GRAM (native) / USDT (jetton) ke alamat TON.
- Payout BELUM terbukti cair (WD pertama Naruto belum sampai min WD).

CARA PAKAI — 1 PERINTAH:
  python3 fortune_gram_umum.py
Lalu pilih menu di dalam:
  [1] Daftar + login web (kode 6 digit dari bot)
  [2] Cek saldo (coin, USD, profit, gift box)
  [3] Klaim harian (buka gift box + klaim + WD kalau >= $0,05)
  [4] Keluar

CARA KERJA MENU [1]:
  1. Skrip minta link login ke server (pakai kode referral di REF_CODE
     kalau ada — isi user id Telegram temanmu, atau kosongkan).
  2. Skrip kirim /start <kode> ke bot. Kalau muncul gate, skrip join
     channel @fortunegrampay lalu klik tombol Verify.
  3. Bot kirim KODE 6 DIGIT ke DM — skrip baca otomatis dari DM bot.
  4. Skrip verifikasi kode ke server, lalu ambil initData (disimpan lokal
     di fortune_initdata.txt — JANGAN disebar ke orang lain).

KREDENSIAL (milikmu sendiri, TIDAK ada di skrip ini):
  1. Buka https://my.telegram.org -> API development tools -> buat app.
  2. Buat file apicred.json di folder yang sama, isinya:
     {"api_id": 12345678, "api_hash": "abc123..."}
  3. Jalankan skrip, masukkan nomor HP + kode login Telegram saat diminta.
  Sesi login tersimpan lokal (fortune_session.session) — JANGAN disebar.

ISI DULU SEBELUM PAKAI (di bawah):
  REF_CODE   = user id Telegram pemberi referral (boleh kosong "")
  WD_ADDRESS = alamat TON kamu untuk terima WD GRAM/USDT (wajib isi
               sebelum klaim menu [3] bisa WD — contoh alamat TON biasa,
               BUKAN alamat exchange tanpa memo).
  PROXY_URL  = kosongkan "" untuk jalan langsung; isi URL proxy HTTP
               kamu kalau mau lewat proxy (format http://user:pass@host:port).

PERINGATAN: gratis 100%. Jangan pernah deposit (min depo $3 — abaikan saja),
jangan bayar verifikasi apa pun, jangan hubungkan wallet berisi dana.
Satu perangkat = satu akun.
"""
import asyncio
import json
import os
import random
import re
import string
import time
import urllib.parse
import urllib.request
import http.cookiejar
import uuid

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import JoinChannelRequest
except ImportError:
    print("Telethon belum terpasang. Jalankan: pip install telethon")
    raise SystemExit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://fortune-grambot.ih0st.app"
BOT = "fortune_grambot"
CHANNEL = "fortunegrampay"

# ---- ISI DULU (milikmu sendiri) ----
REF_CODE = ""    # contoh: "123456789" = user id Telegram pemberi referral (boleh "")
WD_ADDRESS = ""  # contoh: "UQ..." = alamat TON kamu (wajib isi sebelum WD)
PROXY_URL = ""   # contoh: "http://user:pass@host:port" (boleh "" = langsung)

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")
MIN_CLAIM_USD = 0.001
MIN_WD_USD = 0.05


def load_creds():
    p = os.path.join(HERE, "apicred.json")
    if not os.path.exists(p):
        print("apicred.json belum ada. Buat dulu (lihat docstring di atas):")
        print('  {"api_id": 12345678, "api_hash": "abc123..."}')
        print("api_id/api_hash didapat dari https://my.telegram.org")
        return None
    d = json.load(open(p))
    return d["api_id"], d["api_hash"]


def device_id():
    p = os.path.join(HERE, "fortune_device_id.txt")
    if os.path.exists(p):
        return open(p).read().strip()
    did = str(uuid.uuid4())
    open(p, "w").write(did)
    return did


class Web:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        handlers = [urllib.request.HTTPCookieProcessor(self.cj)]
        if PROXY_URL:
            handlers.insert(0, urllib.request.ProxyHandler(
                {"http": PROXY_URL, "https": PROXY_URL}))
        self.opener = urllib.request.build_opener(*handlers)
        self.fp_sent = False

    def post_json(self, path, obj, timeout=30):
        data = json.dumps(obj).encode()
        headers = {"User-Agent": UA, "Content-Type": "application/json",
                   "Referer": BASE + "/", "Origin": BASE,
                   "X-Device-Id": device_id()}
        req = urllib.request.Request(BASE + path, data=data, headers=headers)
        try:
            with self.opener.open(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            try:
                return json.loads(e.read().decode("utf-8", "ignore"))
            except Exception:
                return {"http_error": e.code}

    def api(self, initdata, event, data=None):
        body = {"initData": initdata, "event": event, "data": data or {}}
        if not self.fp_sent:
            body["fp"] = {"uid": "d" + device_id().replace("-", "")[:20],
                          "sw": 360, "sh": 800, "dpr": 2, "cd": 24,
                          "tz": "Asia/Jakarta", "tzo": -420, "lang": "id-ID",
                          "plat": "Linux armv8l", "hc": 8, "dm": 6, "tp": 10}
            self.fp_sent = True
        return self.post_json("/api/app/call", body)


def initdata_path():
    return os.path.join(HERE, "fortune_initdata.txt")


def load_initdata():
    try:
        s = open(initdata_path()).read().strip()
        return s or None
    except Exception:
        return None


def save_initdata(s):
    open(initdata_path(), "w").write(s)


def show_state(d):
    print("  coin=%s | usd=%.6f | profit=%.6f | $/hari=%.4f | gift box=%s | "
          "teman=%s | ref coin=%s | sudah WD=%.4f" % (
              d.get("coins"), d.get("usd") or 0, d.get("profit") or 0,
              d.get("usd_day") or 0, d.get("gifts"), d.get("friends"),
              d.get("ref_coins"), d.get("withdrawn") or 0))


async def get_client():
    creds = load_creds()
    if not creds:
        return None
    api_id, api_hash = creds
    sess = os.path.join(HERE, "fortune_session")
    client = TelegramClient(sess, api_id, api_hash)
    await client.start()
    me = await client.get_me()
    print("Login sebagai: %s (@%s, id %s)" % (me.first_name, me.username, me.id))
    return client


async def tg_code(client, param):
    """Kirim /start wl_* ke bot, tunggu kode 6 digit di DM (maks 180 dtk)."""
    bot = await client.get_entity(BOT)
    baseline = 0
    async for m in client.iter_messages(bot, limit=1):
        baseline = m.id
    await client.send_message(bot, "/start " + param)
    print("  /start terkirim, menunggu kode 6 digit dari bot ...")
    t0 = time.time()
    joined = False
    while time.time() - t0 < 180:
        msgs = []
        async for m in client.iter_messages(bot, limit=8):
            msgs.append(m)
        for m in msgs:
            if m.id <= baseline:
                continue
            txt = m.message or ""
            mm = re.search(r"\b(\d{6})\b", txt)
            if mm and "code" in txt.lower():
                return mm.group(1)
        gate = None
        for m in msgs:
            if not m.reply_markup or not getattr(m.reply_markup, "rows", None):
                continue
            for row in m.reply_markup.rows:
                for b in row.buttons:
                    if "verif" in (b.text or "").lower():
                        gate = m
        if gate is not None and not joined:
            joined = True
            try:
                ch = await client.get_entity(CHANNEL)
                await client(JoinChannelRequest(ch))
                print("  join @%s OK" % CHANNEL)
            except Exception as e:
                print("  join channel gagal: %s" % type(e).__name__)
            await asyncio.sleep(8)
            try:
                await gate.click(2, 0)
                print("  klik Verify OK")
            except Exception:
                print("  klik Verify gagal — coba klik manual di HP")
            await asyncio.sleep(8)
            continue
        await asyncio.sleep(3)
    return None


async def cmd_daftar():
    web = Web()
    j = web.post_json("/__web/login/begin", {"ref": REF_CODE})
    if not j.get("ok"):
        print("login/begin gagal:", json.dumps(j)[:200])
        return
    link = j.get("link", "")
    param = urllib.parse.parse_qs(
        urllib.parse.urlparse(link).query).get("start", [None])[0]
    if not param:
        print("begin tanpa link:", json.dumps(j)[:200])
        return
    print("Link login didapat, lanjut ke Telegram ...")
    client = await get_client()
    if not client:
        return
    try:
        code = await tg_code(client, param)
        if not code:
            print("Kode 6 digit tidak datang (180 dtk). Coba lagi nanti.")
            return
        print("Kode diterima, verifikasi ke server ...")
        j2 = web.post_json("/__web/login/code", {"code": code})
        if not j2.get("ok"):
            print("verify kode gagal:", json.dumps(j2)[:200])
            return
        j3 = web.post_json("/__web/init", {})
        initdata = (j3 or {}).get("initData")
        if not initdata:
            print("init tanpa initData:", str(j3)[:200])
            return
        save_initdata(initdata)
        print("Login web BERHASIL, initData tersimpan lokal.")
        st = web.api(initdata, "state", {})
        d = (st.get("data") or {})
        if d.get("ok"):
            show_state(d)
            print("Link referral kamu:", d.get("ref_link"))
        else:
            print("state gagal:", json.dumps(st)[:200])
    finally:
        await client.disconnect()


def cmd_saldo():
    web = Web()
    initdata = load_initdata()
    if not initdata:
        print("Belum login web. Jalankan menu [1] dulu.")
        return
    st = web.api(initdata, "state", {})
    d = (st.get("data") or {})
    if not (st.get("ok") and d.get("ok")):
        print("state gagal (initData mungkin kedaluwarsa — jalankan menu [1] lagi):",
              json.dumps(st)[:200])
        return
    show_state(d)
    print("Link referral:", d.get("ref_link"))


def cmd_klaim():
    web = Web()
    initdata = load_initdata()
    if not initdata:
        print("Belum login web. Jalankan menu [1] dulu.")
        return
    st = web.api(initdata, "state", {})
    d = (st.get("data") or {})
    if not (st.get("ok") and d.get("ok")):
        print("state gagal — jalankan menu [1] lagi:", json.dumps(st)[:200])
        return
    show_state(d)
    gifts = d.get("gifts") or 0
    total = 0
    while gifts > 0:
        g = web.api(initdata, "gift", {})
        gd = (g.get("data") or {})
        if not (g.get("ok") and gd.get("ok")):
            print("buka gift box gagal:", json.dumps(g)[:200])
            break
        total += gd.get("prize") or 0
        gifts = gd.get("gifts", 0)
        d = gd
        time.sleep(0.5)
    if total:
        print("Gift box dibuka: +%s coin" % total)
    profit = d.get("profit") or 0
    if profit >= MIN_CLAIM_USD:
        c = web.api(initdata, "claim", {})
        cd = (c.get("data") or {})
        if c.get("ok") and cd.get("ok"):
            print("Klaim BERHASIL: usd=%.6f" % (cd.get("usd") or 0))
        else:
            print("Klaim gagal:", json.dumps(c)[:200])
    else:
        print("Profit %.6f < min klaim %.4f — klaim nanti." % (profit, MIN_CLAIM_USD))
    st2 = web.api(initdata, "state", {})
    d2 = (st2.get("data") or {})
    show_state(d2)
    usd = d2.get("usd") or 0
    if usd >= MIN_WD_USD:
        if not WD_ADDRESS:
            print("Saldo USD %.4f sudah >= min WD %.2f, TAPI WD_ADDRESS masih "
                  "kosong — isi dulu di skrip, lalu jalankan menu [3] lagi." % (usd, MIN_WD_USD))
            return
        req = "w" + "".join(random.choice(string.hexdigits.lower()) for _ in range(16))
        w = web.api(initdata, "withdraw", {"asset": "gram", "usd": round(float(usd), 4),
                                           "address": WD_ADDRESS, "memo": "", "req": req})
        wd = (w.get("data") or {})
        print("WD diajukan: %s" % json.dumps(w)[:400])
        if w.get("ok") and wd.get("ok"):
            print("WD BERHASIL diajukan — pantau masuk ke wallet TON kamu.")
        else:
            print("WD gagal/ditolak server (error: %s) — jangan coba bayar apa pun." % wd.get("error"))
    else:
        print("Saldo USD %.4f < min WD %.2f (fee $0,025) — kumpulkan dulu." % (usd, MIN_WD_USD))


def menu():
    print("\n===== FORTUNE GRAM =====")
    print("[1] Daftar + login web (kode 6 digit dari bot)")
    print("[2] Cek saldo (coin, USD, profit, gift box)")
    print("[3] Klaim harian (gift box + klaim + WD kalau >= $0,05)")
    print("[4] Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    while True:
        p = menu()
        if p == "1":
            asyncio.run(cmd_daftar())
        elif p == "2":
            cmd_saldo()
        elif p == "3":
            cmd_klaim()
        elif p == "4":
            print("Keluar. Sampai jumpa!")
            break
        else:
            print("Pilihan tidak ada, coba lagi.")


if __name__ == "__main__":
    main()
