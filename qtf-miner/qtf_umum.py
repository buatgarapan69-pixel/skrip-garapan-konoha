#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QTF MINER — skrip umum (untuk dipakai orang lain, 1 akun).
Gratis 100%: mining QTF di Telegram, tanpa deposit, tanpa fee WD.

CARA PAKAI (Termux / VPS / PC):
  1. pip install telethon requests
  2. Ambil API_ID + API_HASH di https://my.telegram.org/apps
  3. Isi bagian KONFIG di bawah (TON_WALLET = alamat TON kamu, mis. dari
     Tonkeeper — diawali UQ/EQ; REF_CODE = kode referral pengundang, boleh kosong)
  4. Jalankan:  python3 qtf_umum.py
     - login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
     - skrip /start bot, join 2 channel, daftar, connect wallet, start mining,
       klaim bonus tugas +5 QTF, lalu tampilkan link referral kamu
  5. Klaim mining (24 jam sekali) + klaim bonus referral:
       python3 qtf_umum.py --claim

YANG DIDAPAT (sesuai setting live 25 Nov 2026):
  - Mining 0,8 QTF/jam (19,2 QTF per 24 jam), klaim tiap 24 jam
  - Tugas join channel +5 QTF (sekali)
  - +10 QTF tiap teman terverifikasi (wallet + mining + 1 tugas)
  - Komisi 10% dari earn tugas teman
  - Min WD 100 QTF (~$0,1) ke wallet TON, fee 0, diajukan manual (status pending)

CATATAN:
  - File sesi (qtf.session) JANGAN dibagikan ke siapa pun.
  - WD diproses manual oleh admin bot (status pending) — payout belum terbukti,
    pantau terus. Jangan deposit apa pun: deposit di app ini HANYA untuk
    pasang tugas iklan, BUKAN syarat mining/WD.
  - Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
"""

import argparse
import asyncio
import json
import re
import sys
import time

import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser

# ============================== KONFIG — ISI DULU ==============================
API_ID = 0          # <-- isi: angka dari https://my.telegram.org/apps
API_HASH = ""       # <-- isi: string dari https://my.telegram.org/apps
TON_WALLET = ""     # <-- isi: alamat TON kamu (UQ... / EQ...), tujuan WD
REF_CODE = ""       # <-- opsional: id Telegram pengundang (angka), boleh kosong
# ===============================================================================

BOT = "QTF_AIRDROP_bot"
APP_URL = "https://qtf-miner.pages.dev/"
TASK_ID = "0mwvimxx4m4i3"          # tugas: join @QTF_TRADING_FOREX (+5 QTF)
TASK_CHANNEL = "@QTF_TRADING_FOREX"
GATE_CHANNELS = ["@QTF_TRADING_FOREX", "@QtfTaskNotic"]
NS = "zv3"
UP_URL = "https://enjoyed-lamb-224809.upstash.io"
TONRE = re.compile(r"^(UQ|EQ|kQ|0Q)[A-Za-z0-9_-]{46}$")
DAY = 86400 * 1000

CAS = ("local c=redis.call('HGET',KEYS[1],ARGV[1]) if ARGV[2]=='__NIL__' then if c then return 0 end "
       "elseif c~=ARGV[2] then return 0 end if ARGV[3]=='__NIL__' then redis.call('HDEL',KEYS[1],ARGV[1]) "
       "else redis.call('HSET',KEYS[1],ARGV[1],ARGV[3]) end redis.call('INCR',KEYS[2]) redis.call('INCR',KEYS[3]) return 1")


def r6(n):
    return round(float(n or 0), 6)


def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))


class Up:
    """Client Upstash persis seperti yang dipakai Mini App QTF (token publik di halaman app)."""
    def __init__(self):
        html = requests.get(APP_URL, timeout=30).text
        self.token = re.search(r'UP_TOKEN="([^"]+)"', html).group(1)
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "QTF-Miner-umum/1.0"})

    def cmd(self, a):
        r = self.s.post(UP_URL, json=a,
                        headers={"Authorization": "Bearer " + self.token}, timeout=25)
        r.raise_for_status()
        j = r.json()
        if j.get("error"):
            raise RuntimeError(str(j["error"]))
        return j["result"]

    def multi(self, a):
        r = self.s.post(UP_URL + "/multi-exec", json=a,
                        headers={"Authorization": "Bearer " + self.token}, timeout=25)
        r.raise_for_status()
        j = r.json()
        if not isinstance(j, list):
            raise RuntimeError(str(j))
        return [x["result"] if not x.get("error") else (_ for _ in ()).throw(RuntimeError(str(x["error"]))) for x in j]

    def sNow(self):
        t = self.cmd(["TIME"])
        return int(t[0]) * 1000 + int(int(t[1]) / 1000)

    def get_user(self, uid):
        raw = self.cmd(["HGET", NS + ":users", uid])
        return json.loads(raw) if raw else None

    def get_settings(self):
        a = self.cmd(["HGETALL", NS + ":settings"])
        o = {}
        for i in range(0, len(a), 2):
            try:
                o[a[i]] = json.loads(a[i + 1])
            except Exception:
                o[a[i]] = a[i + 1]
        return o

    def txn_user(self, uid, fn, tries=10):
        for _ in range(tries):
            raw = self.cmd(["HGET", NS + ":users", uid])
            doc = json.loads(raw) if raw else None
            out = fn(doc)
            if out is None:
                return {"committed": False}
            ok = self.cmd(["EVAL", CAS, 3, NS + ":users", NS + ":v:users", NS + ":v:users:" + uid, uid,
                           "__NIL__" if raw is None else raw, js(out)])
            if ok == 1:
                return {"committed": True}
        raise RuntimeError("transaction conflict x10")

    def txn_key(self, coll, key, fn, tries=10):
        for _ in range(tries):
            raw = self.cmd(["HGET", NS + ":" + coll, key])
            doc = json.loads(raw) if raw else None
            out = fn(doc)
            if out is None:
                return {"committed": False}
            ok = self.cmd(["EVAL", CAS, 3, NS + ":" + coll, NS + ":v:" + coll, NS + ":v:" + coll + ":" + key, key,
                           "__NIL__" if raw is None else raw, js(out)])
            if ok == 1:
                return {"committed": True}
        raise RuntimeError("transaction conflict x10")

    def bot_get_chat_member(self, bot_token, channel, user_id):
        r = self.s.get("https://api.telegram.org/bot%s/getChatMember?chat_id=%s&user_id=%s"
                       % (bot_token, channel, user_id), timeout=30)
        r.raise_for_status()
        return r.json()


async def telegram_part():
    """Buka bot + Mini App (ambil start_param asli) + join channel gate."""
    client = TelegramClient("qtf", API_ID, API_HASH)
    await client.start()
    try:
        me = await client.get_me()
        bot = await client.get_entity(BOT)
        start = "/start" + (" ref_" + REF_CODE if REF_CODE else "")
        await client.send_message(bot, start)
        await asyncio.sleep(4)
        r = await client(RequestAppWebViewRequest(
            peer=InputPeerUser(bot.id, bot.access_hash),
            app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash), short_name="app"),
            platform="android"))
        import urllib.parse
        frag = urllib.parse.urlparse(r.url).fragment
        initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
        start_param = None
        if initdata:
            start_param = urllib.parse.parse_qs(initdata).get("start_param", [None])[0]
        for ch in GATE_CHANNELS:
            try:
                await client(JoinChannelRequest(ch))
                print("join", ch, "OK")
            except Exception as e:
                print("join", ch, "GAGAL:", str(e)[:100])
        return {"id": me.id, "username": me.username or "",
                "first_name": me.first_name or "User", "start_param": start_param}
    finally:
        await client.disconnect()


def do_register(up, me):
    uid = str(me["id"])
    ref_by = None
    sp = me.get("start_param") or (("ref_" + REF_CODE) if REF_CODE else None)
    if sp and sp.startswith("ref_"):
        ref_by = sp[4:]
    if ref_by == uid or (ref_by and not re.match(r"^\w{1,20}$", ref_by)):
        ref_by = None
    before = up.get_user(uid)
    if before is not None:
        print("akun sudah terdaftar (refBy:", before.get("refBy"), ")")
        return before
    ts = up.sNow()
    new_user = {"uid": uid, "name": str(me["first_name"])[:40], "username": me["username"],
                "dep": 0, "locked": 0, "tvr": 0, "usdt": 0, "refEarn": 0,
                "totalRefs": 0, "verifiedRefs": 0, "refBy": ref_by, "refRewarded": False,
                "taskCount": 0, "done": {}, "promos": {}, "banned": False, "createdAt": ts}
    up.txn_user(uid, lambda x: new_user if x is None else None)
    if ref_by:
        up.txn_user(ref_by, lambda x: {**x, "totalRefs": (x.get("totalRefs") or 0) + 1} if x else None)
        print("terdaftar dengan ref:", ref_by)
    else:
        print("terdaftar tanpa ref.")
    return up.get_user(uid)


def do_wallet_mining(up, uid):
    assert TONRE.match(TON_WALLET), "TON_WALLET tidak valid (harus UQ/EQ + 46 karakter)"
    u = up.get_user(uid)
    if u.get("wallet") != TON_WALLET:
        u["wallet"] = TON_WALLET
        up.multi([["HSET", NS + ":users", uid, js(u)], ["INCR", NS + ":v:users"],
                  ["INCR", NS + ":v:users:" + uid]])
        print("wallet TON disimpan:", TON_WALLET)
    ts = up.sNow()
    up.txn_user(uid, lambda x: ({**x, "mineStart": ts, "mined": True}
                                if x and x.get("wallet") and not x.get("mineStart") else x))
    print("mining jalan (0,8 QTF/jam). Klaim setelah 24 jam.")


def do_task(up, uid, settings):
    chk = up.bot_get_chat_member(settings["botToken"], TASK_CHANNEL, uid)
    status = (chk.get("result") or {}).get("status")
    print("status member", TASK_CHANNEL, ":", status)
    if status not in ("member", "administrator", "creator"):
        print("belum join channel tugas — join dulu lewat Telegram, lalu jalankan lagi.")
        return
    rw = 5
    st = {"fresh": False}
    def _claim(x):
        if not x:
            return x
        x.setdefault("done", {})
        if x["done"].get(TASK_ID):
            return x
        st["fresh"] = True
        x["done"][TASK_ID] = int(time.time() * 1000)
        x["tvr"] = r6((x.get("tvr") or 0) + rw)
        x["totalEarned"] = r6((x.get("totalEarned") or 0) + rw)
        x["taskCount"] = (x.get("taskCount") or 0) + 1
        return x
    up.txn_user(uid, _claim)
    if st["fresh"]:
        up.txn_key("tasks", TASK_ID, lambda t: {**t, "done": (t.get("done") or 0) + 1} if t else None)
        u = up.get_user(uid)
        if u.get("refBy"):
            up.txn_user(u["refBy"], lambda x: {**x, "refEarn": r6((x.get("refEarn") or 0) + rw * 0.10)} if x else None)
        print("tugas diklaim: +5 QTF")
    else:
        print("tugas sudah pernah diklaim.")


def do_refcheck(up, uid, settings):
    u = up.get_user(uid)
    need = settings.get("refVerifyTasks", 1)
    if not (u and u.get("wallet") and (u.get("mined") or u.get("mineStart")) and (u.get("taskCount") or 0) >= need):
        print("ref belum terverifikasi (butuh wallet + mining + %d tugas)." % need)
        return
    if u.get("refRewarded"):
        print("ref sudah terverifikasi sebelumnya.")
        return
    st = {"ok": False}
    def _ref(x):
        if not x or not x.get("refBy") or x.get("refRewarded"):
            return x
        x["refRewarded"] = True
        st["ok"] = True
        return x
    up.txn_user(uid, _ref)
    if st["ok"]:
        up.txn_user(u["refBy"], lambda x: {**x, "verifiedRefs": (x.get("verifiedRefs") or 0) + 1,
                                           "refEarn": r6((x.get("refEarn") or 0) + settings.get("refBonus", 0))} if x else None)
        print("ref terverifikasi! Pengundang +%s QTF." % settings.get("refBonus", 0))


def do_claim(up, uid, settings):
    """Klaim mining (kalau 24 jam lewat) + klaim bonus referral ke saldo."""
    u = up.get_user(uid)
    ts = up.sNow()
    rate = settings.get("mineRate", 5.4)
    g = {"amount": 0}
    def _c(x):
        if not x or not x.get("mineStart") or ts - x["mineStart"] < DAY:
            return x
        g["amount"] = r6(rate * 24)
        x["tvr"] = r6((x.get("tvr") or 0) + g["amount"])
        x["totalEarned"] = r6((x.get("totalEarned") or 0) + g["amount"])
        x["mineStart"] = 0
        return x
    up.txn_user(uid, _c)
    if g["amount"]:
        print("mining diklaim: +%s QTF. Mulai sesi baru..." % g["amount"])
        up.txn_user(uid, lambda x: ({**x, "mineStart": ts, "mined": True} if x and x.get("wallet") else x))
    else:
        left = DAY - (ts - (u.get("mineStart") or ts))
        print("mining belum siap klaim (sisa ~%.1f jam)." % (left / 3600000))
    u = up.get_user(uid)
    if (u.get("refEarn") or 0) > 0:
        amt = u["refEarn"]
        up.txn_user(uid, lambda x: {**x, "tvr": r6((x.get("tvr") or 0) + amt), "refEarn": 0} if x else None)
        print("bonus referral diklaim: +%s QTF ke saldo." % amt)
    u = up.get_user(uid)
    print("saldo withdrawable: %s QTF | min WD: %s QTF" % (u.get("tvr"), settings.get("minWithdrawTokens", 100)))


def show_status(up, uid):
    u = up.get_user(uid)
    print("---- STATUS ----")
    print("saldo (tvr):", u.get("tvr"), "QTF")
    print("bonus referral (refEarn):", u.get("refEarn"), "QTF")
    print("total referral:", u.get("totalRefs"), "| terverifikasi:", u.get("verifiedRefs"))
    print("mining:", "jalan" if u.get("mineStart") else "belum mulai")
    print("link referral kamu: https://t.me/QTF_AIRDROP_bot/app?startapp=ref_" + uid)
    print("wallet:", u.get("wallet"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", action="store_true", help="klaim mining + bonus referral saja")
    args = ap.parse_args()
    if not API_ID or not API_HASH:
        sys.exit("ISI DULU API_ID + API_HASH di bagian KONFIG (https://my.telegram.org/apps).")
    if not TON_WALLET:
        sys.exit("ISI DULU TON_WALLET di bagian KONFIG (alamat TON kamu).")
    up = Up()
    settings = up.get_settings()
    if args.claim:
        me = asyncio.run(telegram_part())
        do_claim(up, str(me["id"]), settings)
        show_status(up, str(me["id"]))
        return
    me = asyncio.run(telegram_part())
    uid = str(me["id"])
    do_register(up, me)
    do_wallet_mining(up, uid)
    do_task(up, uid, settings)
    do_refcheck(up, uid, settings)
    show_status(up, uid)
    print("\nSELESAI. Jalankan lagi besok dengan --claim untuk klaim mining harian.")


if __name__ == "__main__":
    main()
