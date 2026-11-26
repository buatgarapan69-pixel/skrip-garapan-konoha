#!/usr/bin/env python3
"""KUKDOO — skrip umum (publik, tanpa kredensial).

Bot Telegram penghasil $EGG: tap ayam, kumpulin telur, gratis, tanpa deposit.
- Bot: @kukdooobot — daftar gratis, bonus 1.000 telur.
- Earn: tap ayam (1 telur/tap, telur emas tiap ~60-119 tap), klaim harian
  (hari 1: 500, hari 7: 100.000, hari 8: 200.000 telur), misi (join channel
  +5.000, follow X +5.000, tap 1.000x +5.000), beli upgrade toko (mulai 500
  telur, +60 telur/jam), combo harian 100.000 telur, referral +5.000/teman.
- Didanai sekitar $1,25 jt (info channel). Season 1 sedang jalan.
- Min WD: BELUM DIBUKA admin (withdrawOpen=false, tunggu season 1 selesai).
  WD USDT jaringan TON (alamat UQ.../EQ...). Payout BELUM terbukti cair.

CARA PAKAI — 1 PERINTAH:
  python3 kukdoo_umum.py
Lalu pilih menu di dalam:
  [1] Daftar + login (ambil initData dari WebView bot)
  [2] Cek saldo (telur, tap, energi, teman, WD)
  [3] Klaim harian (gift + daily + 250 tap + WD kalau sudah dibuka)
  [4] Keluar

CARA KERJA MENU [1]:
  1. Skrip kirim /start <REF_CODE> ke bot (isi user id Telegram pemberi
     referral kalau ada — boleh kosong "").
  2. Skrip join channel @kukdoo_xyz (misi +5.000 telur).
  3. Skrip buka WebView bot, ambil initData (disimpan lokal di
     kukdoo_initdata.txt — JANGAN disebar ke orang lain).

KREDENSIAL (milikmu sendiri, TIDAK ada di skrip ini):
  1. Buka https://my.telegram.org -> API development tools -> buat app.
  2. Buat file apicred.json di folder yang sama, isinya:
     {"api_id": 12345678, "api_hash": "abc123..."}
  3. Jalankan skrip, masukkan nomor HP + kode login Telegram saat diminta.
  Sesi login tersimpan lokal (kukdoo_session.session) — JANGAN disebar.

ISI DULU SEBELUM PAKAI (di bawah):
  REF_CODE   = user id Telegram pemberi referral (boleh kosong "")
  WD_ADDRESS = alamat TON kamu untuk terima WD USDT (wajib isi sebelum
               klaim menu [3] bisa WD — contoh alamat TON biasa UQ.../EQ...,
               BUKAN alamat exchange tanpa memo).
  PROXY_URL  = kosongkan "" untuk jalan langsung; isi URL proxy HTTP
               kamu kalau mau lewat proxy (format http://user:pass@host:port).

PERINGATAN: gratis 100%. Jangan pernah deposit, jangan bayar apa pun,
jangan hubungkan wallet berisi dana. Satu perangkat = satu akun.
Server membatasi tap (~22 tap/detik) — skrip sudah ikut batas itu.
"""
import asyncio
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import uuid

try:
    from telethon import TelegramClient
    from telethon.tl.types import InputPeerUser, InputUser
    from telethon.tl.functions.messages import RequestWebViewRequest
    from telethon.tl.functions.channels import JoinChannelRequest
except ImportError:
    print("Telethon belum terpasang. Jalankan: pip install telethon")
    raise SystemExit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://kukdoo.alexmetav.workers.dev"
WEBAPP = "https://kukdoo.alexmetav.workers.dev/"
BOT = "kukdooobot"
CHANNEL = "kukdoo_xyz"

# ---- ISI DULU (milikmu sendiri) ----
REF_CODE = ""    # contoh: "123456789" = user id Telegram pemberi referral (boleh "")
WD_ADDRESS = ""  # contoh: "UQ..." = alamat TON kamu (wajib isi sebelum WD)
PROXY_URL = ""   # contoh: "http://user:pass@host:port" (boleh "" = langsung)

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")
TAPS_PER_DAY = 250


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
    p = os.path.join(HERE, "kukdoo_device_id.txt")
    if os.path.exists(p):
        return open(p).read().strip()
    did = "d" + uuid.uuid4().hex[:24]
    open(p, "w").write(did)
    return did


def egg_gap(uid, n):
    h = 2166136261
    for ch in uid + ":" + str(n):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return 60 + (h % 60)


class Web:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        handlers = [urllib.request.HTTPCookieProcessor(self.cj)]
        if PROXY_URL:
            handlers.insert(0, urllib.request.ProxyHandler(
                {"http": PROXY_URL, "https": PROXY_URL}))
        self.opener = urllib.request.build_opener(*handlers)

    def post_json(self, path, obj, token=None, timeout=30):
        data = json.dumps(obj).encode()
        headers = {"User-Agent": UA, "Content-Type": "application/json",
                   "Referer": BASE + "/", "Origin": BASE,
                   "X-Device-Id": device_id()}
        if token:
            headers["Authorization"] = "Bearer " + token
        for _ in range(3):
            try:
                req = urllib.request.Request(BASE + path, data=data, headers=headers)
                with self.opener.open(req, timeout=timeout) as r:
                    return r.status, json.loads(r.read().decode("utf-8", "ignore"))
            except urllib.error.HTTPError as e:
                try:
                    return e.code, json.loads(e.read().decode("utf-8", "ignore"))
                except Exception:
                    return e.code, {"http_error": e.code}
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                time.sleep(2)
        return 0, {"error": "gagal 3x (cek internet/proxy)"}

    def login(self, initdata):
        return self.post_json("/api/login",
                              {"initData": initdata, "deviceId": device_id(), "ref": REF_CODE})

    def sync(self, token, tap=None, action=None):
        body = {}
        if tap is not None:
            body["tap"] = tap
        if action is not None:
            body["action"] = action
        return self.post_json("/api/sync", body, token)


def initdata_path():
    return os.path.join(HERE, "kukdoo_initdata.txt")


def load_initdata():
    try:
        s = open(initdata_path()).read().strip()
        return s or None
    except Exception:
        return None


def save_initdata(s):
    open(initdata_path(), "w").write(s)


def show_state(st):
    rw = st.get("rewards") or {}
    print("  telur=%s | total=%s | tap=%s | energi=%s | pph=%s | telur emas=%s | "
          "teman=%s | ref telur=%s | hari=%s | klaim hari ini=%s | WD buka=%s | "
          "USDT=%.2f" % (
              st.get("balance"), st.get("total"), st.get("taps"), st.get("energy"),
              st.get("pph"), st.get("goldEggs"), st.get("refCount"), st.get("refEarned"),
              st.get("day"), st.get("claimed"), st.get("withdrawOpen"), rw.get("usdt") or 0))


async def cmd_daftar():
    creds = load_creds()
    if not creds:
        return
    api_id, api_hash = creds
    sess = os.path.join(HERE, "kukdoo_session")
    client = TelegramClient(sess, api_id, api_hash)
    await client.start()
    try:
        me = await client.get_me()
        print("Login sebagai: %s (@%s, id %s)" % (me.first_name, me.username, me.id))
        ent = await client.get_entity(BOT)
        await client.send_message(ent, "/start " + REF_CODE if REF_CODE else "/start")
        print("  /start terkirim, join channel ...")
        try:
            ch = await client.get_entity(CHANNEL)
            await client(JoinChannelRequest(ch))
            print("  join @%s OK" % CHANNEL)
        except Exception as e:
            print("  join channel gagal: %s" % type(e).__name__)
        await asyncio.sleep(3)
        res = await client(RequestWebViewRequest(
            peer=InputPeerUser(ent.id, ent.access_hash),
            bot=InputUser(ent.id, ent.access_hash),
            platform="android", from_bot_menu=True, url=WEBAPP))
        frag = urllib.parse.urlparse(res.url).fragment
        qs = urllib.parse.parse_qs(frag)
        initdata = qs.get("tgWebAppData", [None])[0]
        if not initdata:
            print("  WebView tanpa initData — coba lagi.")
            return
        save_initdata(initdata)
        print("Login web BERHASIL, initData tersimpan lokal.")
        web = Web()
        s, d = web.login(initdata)
        if s != 200:
            print("  login API gagal:", s, json.dumps(d)[:200])
            return
        st = d.get("state", {})
        print("  baru=%s | bonus sambutan=%s" % (d.get("isNew"), d.get("welcome")))
        show_state(st)
    finally:
        await client.disconnect()


def need_login():
    initdata = load_initdata()
    if not initdata:
        print("Belum login web. Jalankan menu [1] dulu.")
        return None, None, None
    web = Web()
    s, d = web.login(initdata)
    if s != 200:
        print("login API gagal (initData mungkin kedaluwarsa — jalankan menu [1] lagi):",
              s, json.dumps(d)[:200])
        return None, None, None
    return web, d["token"], d.get("state", {})


def cmd_saldo():
    web, token, st = need_login()
    if not web:
        return
    show_state(st)
    s, d = web.post_json("/api/friends", None, token)
    fr = (d or {}).get("friends") or []
    if fr:
        print("  teman (%d): %s" % (len(fr), ", ".join(f.get("name", "?") for f in fr[:10])))


def do_taps(web, token, st, count=TAPS_PER_DAY):
    uid = st.get("id", "")
    gold_n = st.get("goldEggs", 0)
    taps_since = st.get("tapsSinceEgg", 0)
    gap = egg_gap(uid, gold_n)
    taps = st.get("taps", 0)
    target = taps + count
    while taps < target:
        n = min(60, target - taps)
        gold = 0
        for _ in range(n):
            taps_since += 1
            if taps_since >= gap:
                gold += 1
                gold_n += 1
                taps_since = 0
                gap = egg_gap(uid, gold_n)
        s, d = web.sync(token, tap={"taps": n, "turboTaps": 0, "earned": n, "gold": gold})
        if s != 200:
            print("  tap gagal:", s, json.dumps(d)[:200])
            break
        taps = d.get("state", {}).get("taps", taps)
        time.sleep(3)
    return taps


def cmd_klaim():
    web, token, st = need_login()
    if not web:
        return
    show_state(st)
    s, d = web.sync(token, action={"type": "claimGifts"})
    print("  gift:", json.dumps(d.get("notes")))
    s, d = web.sync(token, action={"type": "daily"})
    print("  daily:", json.dumps(d.get("notes")))
    s, d = web.sync(token, action={"type": "taskStart", "id": "tgchannel"})
    s, d = web.sync(token, action={"type": "task", "id": "tgchannel"})
    print("  task channel:", json.dumps(d.get("notes")))
    taps = do_taps(web, token, st)
    print("  tap selesai, total tap=%s" % taps)
    s, d = web.sync(token, action={"type": "task", "id": "tap1k"})
    print("  task tap1k:", json.dumps(d.get("notes")))
    s, d = web.login(load_initdata())
    st = d.get("state", {})
    show_state(st)
    rw = st.get("rewards") or {}
    if st.get("withdrawOpen") and (rw.get("usdt") or 0) > 0:
        if not WD_ADDRESS:
            print("  WD TERBUKA dan USDT %.2f — TAPI WD_ADDRESS masih kosong, "
                  "isi dulu di skrip lalu jalankan menu [3] lagi." % rw["usdt"])
            return
        s, d = web.sync(token, action={"type": "withdraw", "address": WD_ADDRESS})
        print("  WD diajukan: %s" % json.dumps(d.get("notes")))
        print("  WD masuk antrean review tim — pantau masuk ke wallet TON kamu.")
    else:
        print("  WD masih BELUM dibuka admin (atau USDT 0) — kumpulkan dulu.")


def menu():
    print("\n===== KUKDOO =====")
    print("[1] Daftar + login (ambil initData dari WebView bot)")
    print("[2] Cek saldo (telur, tap, teman, WD)")
    print("[3] Klaim harian (gift + daily + 250 tap + WD kalau dibuka)")
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
