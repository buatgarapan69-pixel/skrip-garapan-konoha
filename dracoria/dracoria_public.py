#!/usr/bin/env python3
"""
DRACORIA — skrip gratis untuk ORANG LAIN (bukan skrip Admin Konoha).
Hatch Dragon Egg gratis dari bonus 1 GRAM, klaim harian, tugas, jual telur.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon
  2. Isi API_ID + API_HASH di bawah (buat di https://my.telegram.org)
  3. Isi REF_CODE dengan ID Telegram KAMU (angka, contoh: 123456789)
     - kosongkan ("") kalau tidak mau pakai referral siapa pun
  4. python3 dracoria_public.py
  - Login pertama akan minta kode OTP Telegram di terminal.
  - Skrip TIDAK meminta private key / seed phrase / dana apa pun.
  - GRATIS saja: bonus 1 GRAM -> beli Dragon Egg (1 GRAM).
    JANGAN beli naga TON (2,99-19,99 TON) kalau tidak mau modal.

FAKTA (dicek 24 Nov 2026, akun Admin Konoha):
  - Bonus daftar 1 GRAM, Dragon Egg 1 GRAM, +0,1 GRAM/hari (10 hari)
  - Check-in harian 2.000-12.000 telur (100.000 telur = 1 GRAM)
  - Tugas harian: +0,05 GRAM (join @Dracoria) + 0,02 GRAM (react)
  - Daily reward +0,05 GRAM, referral +0,05 GRAM/teman
  - Min WD 2 GRAM, fee 0, 2x WD gratis. WD BELUM TERBUKTI CAIR.
"""
import asyncio, hashlib, hmac, json, re, sys, time, urllib.parse, urllib.request, urllib.error, http.cookiejar, uuid, random

# ===================== ISI BAGIAN INI =====================
API_ID = 0          # <-- isi: API ID dari my.telegram.org (angka)
API_HASH = ""       # <-- isi: API hash dari my.telegram.org
SESSION_NAME = "dracoria_saya"   # nama file sesi (dibuat otomatis)
REF_CODE = ""       # <-- isi: ID Telegram kamu (angka) atau "" kalau tanpa ref
PROXY = ""          # opsional: "http://user:pass@host:port" (proxy residensial)
# =========================================================

BOT = "DracoriaRoBot"
CHANNEL = "Dracoria"
BASE = "https://app.dracoria.online/"
DEVICES = ["Pixel 7", "Pixel 8", "Samsung Galaxy S23", "Xiaomi 13", "OnePlus 11", "Redmi Note 13"]

def fake_ua(seed):
    h = int(hashlib.sha256(str(seed).encode()).hexdigest(), 16)
    dev = DEVICES[h % len(DEVICES)]
    chrome = 118 + (h // len(DEVICES)) % 14
    return (f"Mozilla/5.0 (Linux; Android 13; {dev}) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{chrome}.0.0.0 Mobile Safari/537.36")

def gate_token(secret):
    sig = hmac.new(secret.encode(), b"app.dracoria.online", hashlib.sha256).hexdigest()
    return f"tz_ddos_token={sig}&tz_ts={int(time.time())}&tz_turnstile="

def get_gate_secret(opener, ua):
    """Ambil SHARED_SECRET dari halaman verifikasi anti-DDoS (JS publik situs)."""
    urls = [BASE,
            "https://tzddosprotectionverification.tzsmm.com/?d=app.dracoria.online&url=/"]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": ua})
            with opener.open(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            m = re.search(r'SHARED_SECRET\s*=\s*"([^"]+)"', body)
            if m:
                return m.group(1)
        except Exception:
            continue
    return None

async def main():
    if not API_ID or not API_HASH:
        print("ISI DULU API_ID + API_HASH di bagian atas skrip (my.telegram.org).")
        return
    from telethon import TelegramClient
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import RequestWebViewRequest, SendReactionRequest
    from telethon.tl.types import InputUser, InputPeerUser, ReactionEmoji

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    try:
        me = await client.get_me()
        print("Login sebagai:", me.username, me.id)
        ua = fake_ua(me.id)
        devid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "dracoria-" + str(me.id)))
        bot = await client.get_entity(BOT)
        ref = REF_CODE.strip() if REF_CODE else ""
        await client.send_message(bot, "/start " + ref if ref else "/start")
        await asyncio.sleep(2)
        try:
            ch = await client.get_entity(CHANNEL)
            await client(JoinChannelRequest(ch))
            print("Join @Dracoria: OK")
            await client(SendReactionRequest(peer=ch, msg_id=9,
                                             reaction=[ReactionEmoji(emoticon="❤️")]))
            print("React pesan 9: OK")
        except Exception as e:
            print("Join/react:", type(e).__name__, str(e)[:100])
        wv = await client(RequestWebViewRequest(
            peer=InputPeerUser(bot.id, bot.access_hash),
            bot=InputUser(bot.id, bot.access_hash),
            platform="android", url=f"https://t.me/{BOT}/farm",
            start_param=ref if ref else None))
        u = urllib.parse.urlparse(wv.url)
        params = urllib.parse.parse_qs(u.query) or urllib.parse.parse_qs(u.fragment)
        initdata = params.get("tgWebAppData", [None])[0]
        if not initdata:
            print("GAGAL: tidak dapat initData dari WebView.")
            return
    finally:
        await client.disconnect()

    handlers = []
    if PROXY:
        handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    cj = http.cookiejar.CookieJar()
    handlers.append(urllib.request.HTTPCookieProcessor(cj))
    op = urllib.request.build_opener(*handlers)

    def req(method, url, data=None):
        h = {"User-Agent": ua, "Referer": BASE, "Origin": BASE.rstrip("/"),
             "Accept": "*/*", "X-Requested-With": "XMLHttpRequest",
             "X-Device-Id": devid}
        body = urllib.parse.urlencode(data).encode() if data else None
        if body:
            h["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        r = urllib.request.Request(url, data=body, method=method, headers=h)
        try:
            with op.open(r, timeout=35) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")[:500]
        except Exception as e:
            return 0, f"{type(e).__name__}: {e}"

    def post_json(path, data):
        st, b = req("POST", BASE + path, data)
        if "Security Check" in b:
            secret = get_gate_secret(op, ua)
            if secret:
                req("GET", BASE + "?" + gate_token(secret))
                st, b = req("POST", BASE + path, data)
        try:
            return st, json.loads(b)
        except Exception:
            return st, {"raw": b[:300]}

    secret = get_gate_secret(op, ua)
    if secret:
        req("GET", BASE + "?" + gate_token(secret))
    st, body = req("POST", BASE + "index.php",
                   {"login": "true", "init_data": initdata, "ref_by": ref})
    print("Login web:", body[:60])
    if body.strip() != "done":
        print("GAGAL login web. Coba lagi (initData mungkin kedaluwarsa).")
        return
    for label, path, data in [
        ("Check-in harian (+telur)", "pages/farm.php", {"action": "claim_daily_checkin"}),
        ("Daily reward (+0,05 GRAM)", "pages/tasks.php", {"action": "claim_daily"}),
        ("Tugas join (+0,05 GRAM)", "pages/tasks.php", {"action": "claim_task", "task_id": "1"}),
        ("Tugas react (+0,02 GRAM)", "pages/tasks.php", {"action": "claim_task", "task_id": "2"}),
        ("Beli Dragon Egg (1 GRAM)", "pages/shop.php", {"action": "buy_with_balance", "package_id": "1"}),
    ]:
        st, j = post_json(path, data)
        print(f"{label}: {j}")
    print("SELESAI. Cek saldo di bot @DracoriaRoBot > Wallet. Min WD 2 GRAM.")

if __name__ == "__main__":
    asyncio.run(main())
