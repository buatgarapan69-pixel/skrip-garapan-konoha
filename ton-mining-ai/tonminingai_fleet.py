#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TON MINING AI (@TonMiningai_Bot) — Fleet multi-akun pakai ref akun utama kamu.
Mirror persis logika Mini App (tonminingai_webapp.html) + probe2 Utama:
- register baru dgn refBy Utama + referrer totalRefs+1
- link wallet TON sendiri (CAS wallets, 1 wallet = 1 akun; kalau sudah milik orang lain -> gagal, jangan overwrite)
- start mining (snapshot penuh ala probe2)
- klaim semua task gratis aktif (verifikasi member via Bot API) + komisi 10% ke referrer per klaim fresh
- checkRef: wallet + mining + taskCount>=refVerifyTasks -> refRewarded, referrer verifiedRefs+1 + refBonus
Tiap akun: fakerandom UA (seed per nama) + device ID UUID5 + sesi proxy AeonProxy #2 sendiri.
GRATIS saja: tanpa deposit, tanpa WD, tanpa kirim dana. Output: ./logs/tonminingai_fleet_20261127.json
"""
import asyncio, json, os, random, re, shutil, sys, time, urllib.parse, uuid
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputPeerUser, InputUser

BOT = "TonMiningai_Bot"
# --- ISI DENGAN DATA KAMU (jangan commit file berisi data asli) ---
API_ID = int(os.environ.get("TG_API_ID", "0") or 0)
API_HASH = os.environ.get("TG_API_HASH", "")
SESSIONS_DIR = os.environ.get("TG_SESSIONS_DIR", "./sessions")
REFERRER_UID = os.environ.get("TG_USER_ID", "")  # ID Telegram akun utama (referrer)
assert API_ID and API_HASH and REFERRER_UID, "isi TG_API_ID/TG_API_HASH/TG_USER_ID dulu"
GATE_CHANNELS = ["@tonminerainews", "@globalairdropupdet", "@REFERRALS_Buy"]
OUT = "./tonminingai_fleet.json"
HTML = "./tonminingai_webapp.html"  # simpan HTML Mini App di sini (lihat README)
ROSTER = "./roster.json"  # lihat roster.example.json
NS = "zv3"
TONRE = re.compile(r"^(UQ|EQ|kQ|0Q)[A-Za-z0-9_-]{46}$")
SEM = 6
TMPDIR = "./.tmp_sessions"

html = open(HTML, encoding="utf-8", errors="ignore").read()
UP_URL = re.search(r'UP_URL="([^"]+)"', html).group(1)
UP_TOKEN = re.search(r'UP_TOKEN="([^"]+)"', html).group(1)

# --- proxy AeonProxy akun #2 (kredensial dibaca dari file, jangan hardcode password) ---
def load_proxy_creds():
    txt = open("./proxy.txt", encoding="utf-8", errors="ignore").read()  # format: "Proxy username: ..." / "Proxy password: ..." (boleh kosong = tanpa proxy)
    mu = re.search(r"Proxy username:\s*(\S+)", txt)
    mp = re.search(r"Proxy password:\s*(\S+)", txt)
    return (mu.group(1), mp.group(1)) if (mu and mp) else (None, None)

PROXY_USER, PROXY_PASS = load_proxy_creds()

DEVICES = [
    ("SM-S918B", "13"), ("SM-A546E", "13"), ("Pixel 7", "13"), ("Pixel 8", "14"),
    ("Pixel 6a", "13"), ("SM-G998B", "12"), ("SM-S901E", "12"), ("RMX3360", "12"),
    ("M2101K6G", "12"), ("V2050", "12"), ("CPH2387", "13"), ("DN2103", "13"),
    ("SM-M336BU", "13"), ("Pixel 7a", "13"), ("SM-A135F", "12"), ("2201117TG", "12"),
    ("SM-F711B", "12"), ("ASUS_AI2202", "13"), ("moto g82 5G", "12"), ("TECNO KJ5", "13"),
    ("Infinix X6833B", "12"), ("POCO F4", "12"),
]

def ua_for(name):
    rng = random.Random("tma-ua-" + name)
    model, av = rng.choice(DEVICES)
    chrome = rng.randint(118, 131)
    return ("Mozilla/5.0 (Linux; Android %s; %s) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/%d.0.0.0 Mobile Safari/537.36" % (av, model.strip(), chrome))

def device_id_for(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "tma-device-" + name))

def proxy_sid_for(name):
    return uuid.uuid5(uuid.NAMESPACE_URL, "tma-" + name).hex[:12]

def proxy_url_for(name):
    if not PROXY_USER or not PROXY_PASS:
        return None
    return "http://%s-sid-%s-time-3600:%s@gate.aeonproxy.com:7000" % (
        PROXY_USER, proxy_sid_for(name), PROXY_PASS)

def r6(n):
    return round(float(n or 0), 6)

def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))

CAS = ("local c=redis.call('HGET',KEYS[1],ARGV[1]) if ARGV[2]=='__NIL__' then if c then return 0 end "
       "elseif c~=ARGV[2] then return 0 end if ARGV[3]=='__NIL__' then redis.call('HDEL',KEYS[1],ARGV[1]) "
       "else redis.call('HSET',KEYS[1],ARGV[1],ARGV[3]) end redis.call('INCR',KEYS[2]) redis.call('INCR',KEYS[3]) return 1")

import requests

class Up:
    """Client Upstash per akun: UA acak + device ID + proxy sendiri (requests.Session)."""
    def __init__(self, name, use_proxy=True):
        self.name = name
        self.ua = ua_for(name)
        self.device_id = device_id_for(name)
        if os.environ.get("TMA_NOPROXY"):
            use_proxy = False
        self.proxy = proxy_url_for(name) if use_proxy else None
        self.proxy_ok = None
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": self.ua, "X-Device-Id": self.device_id})
        if self.proxy:
            self.s.proxies = {"http": self.proxy, "https": self.proxy}

    def _req(self, url, body=None, headers=None, timeout=25):
        h = {}
        if headers:
            h.update(headers)
        if body is not None:
            r = self.s.post(url, json=body, headers=h, timeout=timeout)
        else:
            r = self.s.get(url, headers=h, timeout=timeout)
        r.raise_for_status()
        return r.json()

    def cmd(self, a):
        j = self._req(UP_URL, body=a, headers={"Authorization": "Bearer " + UP_TOKEN,
                                                "Content-Type": "application/json"})
        if j.get("error"):
            raise RuntimeError(str(j["error"]))
        return j["result"]

    def hgetall(self, coll):
        a = self.cmd(["HGETALL", NS + ":" + coll])
        o = {}
        for i in range(0, len(a), 2):
            try:
                o[a[i]] = json.loads(a[i + 1])
            except Exception:
                o[a[i]] = a[i + 1]
        return o

    def sNow(self):
        t = self.cmd(["TIME"])
        return int(t[0]) * 1000 + int(int(t[1]) / 1000)

    def get_user(self, uid):
        raw = self.cmd(["HGET", NS + ":users", uid])
        return json.loads(raw) if raw else None

    def txn_coll(self, coll, key, fn, tries=10):
        for _ in range(tries):
            raw = self.cmd(["HGET", NS + ":" + coll, key])
            doc = json.loads(raw) if raw else None
            out = fn(doc)
            if out is None:
                return {"committed": False}
            ok = self.cmd(["EVAL", CAS, 3, NS + ":" + coll, NS + ":v:" + coll,
                           NS + ":v:" + coll + ":" + key, key,
                           "__NIL__" if raw is None else raw, js(out)])
            if ok == 1:
                return {"committed": True}
        raise RuntimeError("transaction conflict x10")

    def txn_user(self, uid, fn, tries=10):
        return self.txn_coll("users", uid, fn, tries)

    def bot_get_chat_member(self, channel, user_id):
        url = ("https://api.telegram.org/bot%s/getChatMember?chat_id=%s&user_id=%s"
               % (BOT_TOKEN, urllib.parse.quote(channel), user_id))
        try:
            return self._req(url, timeout=45)
        except Exception:
            s2 = requests.Session()
            s2.headers.update({"User-Agent": self.ua})
            r = s2.get(url, timeout=30)
            r.raise_for_status()
            return r.json()

# --- live config dari server (baca langsung, tanpa proxy) ---
_up0 = Up("utama", use_proxy=False)
SETTINGS = _up0.hgetall("settings")
TASKS_LIVE = _up0.hgetall("tasks")
BOT_TOKEN = SETTINGS.get("botToken") or ""
_cfg = lambda k, d: SETTINGS.get(k) if SETTINGS.get(k) not in (None, "") else d
RATE = float(_cfg("rate", 1000))
MINE_RATE = float(_cfg("mineRate", 1))
MINE_PCT = float(_cfg("mineBalancePct", 0))
REF_BONUS = float(_cfg("refBonus", 5))
REF_SPD = float(_cfg("refSpeedBonus", 0.5))
COMMISSION = float(_cfg("commission", 10))
REF_VERIFY_TASKS = int(float(_cfg("refVerifyTasks", 1)))

def roster_wallets():
    r = json.load(open(ROSTER))
    return {x["name"]: x["wallet"] for x in r}

async def run_one(name, wallet, sem):
    res = {"name": name, "wallet": wallet}
    up = Up(name)
    res["ua"] = up.ua
    res["device_id"] = up.device_id
    res["proxy_sid"] = proxy_sid_for(name) if up.proxy else None
    res["proxy_used"] = bool(up.proxy)
    async with sem:
        # --- Telethon: /start ref Utama + WebView initData + join gate ---
        dst = None
        try:
            sess = os.path.join(SESSIONS_DIR, name + ".session")  # 1 file .session per akun
            if os.path.exists(sess):
                os.makedirs(TMPDIR, exist_ok=True)
                dst = os.path.join(TMPDIR, name + ".session")
                shutil.copyfile(sess, dst)
                sess = dst
            client = TelegramClient(sess, API_ID, API_HASH)
            await client.connect()
            try:
                me = await client.get_me()
                res["tg_id"] = me.id
                res["username"] = me.username
                bot = await client.get_entity(BOT)
                await client.send_message(bot, "/start ref_" + REFERRER_UID)
                await asyncio.sleep(3)
                try:
                    r = await client(RequestAppWebViewRequest(
                        peer=InputPeerUser(bot.id, bot.access_hash),
                        app=InputBotAppShortName(bot_id=InputUser(bot.id, bot.access_hash), short_name="app"),
                        platform="android"))
                    frag = urllib.parse.urlparse(r.url).fragment
                    initdata = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
                    res["webview_initdata"] = bool(initdata)
                    if initdata:
                        q = urllib.parse.parse_qs(initdata)
                        res["initdata_start_param"] = q.get("start_param", [None])[0]
                        try:
                            res["initdata_user_id"] = json.loads(q.get("user", ["{}"])[0]).get("id")
                        except Exception:
                            pass
                except Exception as e:
                    res["webview_error"] = str(e)[:200]
                joins = {}
                for ch in GATE_CHANNELS:
                    try:
                        await client(JoinChannelRequest(ch))
                        joins[ch] = "joined-ok"
                    except Exception as e:
                        joins[ch] = "ERR: " + str(e)[:120]
                    await asyncio.sleep(1)
                res["joins"] = joins
            finally:
                await client.disconnect()
        except Exception as e:
            res["telethon_error"] = str(e)[:300]
            return res
        finally:
            if dst:
                for f in (dst, dst + "-journal"):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
        uid = str(res["tg_id"])
        # --- Upstash (via proxy+UA akun ini), di thread agar paralel ---
        loop = asyncio.get_running_loop()
        def _upstash():
            o = {}
            try:
                if up.proxy:
                    try:
                        o["proxy_exit_ip"] = up.s.get("http://httpbin.org/ip", timeout=15).json().get("origin")
                        up.proxy_ok = True
                    except Exception as e:
                        up.proxy_ok = False
                        o["proxy_error"] = str(e)[:150]
                        up.s.proxies = {}
                        res["proxy_used"] = False
                        res["proxy_fallback_direct"] = True
                before = up.get_user(uid)
                o["registered_before"] = before is not None
                if before is None:
                    ts = up.sNow()
                    me_name = (res.get("username") or res["name"])[:40]
                    new_user = {"uid": uid, "name": me_name, "username": res.get("username") or "",
                                "dep": 0, "locked": 0, "tvr": 0, "usdt": 0, "refEarn": 0,
                                "totalRefs": 0, "verifiedRefs": 0, "refBy": REFERRER_UID, "refRewarded": False,
                                "taskCount": 0, "done": {}, "promos": {}, "banned": False, "createdAt": ts}
                    r = up.txn_user(uid, lambda x: new_user if x is None else None)
                    o["register"] = r["committed"]
                    rr = up.txn_user(REFERRER_UID, lambda x: {**x, "totalRefs": (x.get("totalRefs") or 0) + 1} if x else None)
                    o["referrer_totalRefs_inc"] = rr["committed"]
                else:
                    o["refBy_existing"] = before.get("refBy")
                # --- link wallet (CAS, mirror probe2): 1 wallet = 1 akun ---
                assert TONRE.match(wallet), "format wallet TON tidak valid"
                u_now = up.get_user(uid)
                old_wallet = (u_now or {}).get("wallet")
                st = {"ok": False}
                def _wlink(x):
                    if x and x != uid:
                        return x
                    st["ok"] = True
                    return uid
                r = up.txn_coll("wallets", wallet, _wlink)
                o["wallet_link"] = {"committed": r["committed"], "ok": st["ok"], "old_wallet": old_wallet}
                if not st["ok"]:
                    o["wallet_conflict"] = True
                    o["final"] = up.get_user(uid)
                    return o
                ts = up.sNow()
                def _setwal(x):
                    if x:
                        x["wallet"] = wallet
                        x["walletAt"] = ts
                    return x
                r2 = up.txn_user(uid, _setwal)
                o["wallet_set"] = r2["committed"]
                if old_wallet and old_wallet != wallet:
                    up.txn_coll("wallets", old_wallet, lambda x: None if x == uid else x)
                    o["wallet_old_released"] = old_wallet
                # --- start mining (mirror probe2 snapshot penuh) ---
                ts = up.sNow()
                spd_state = {"started": False}
                def _start(x):
                    if x and x.get("wallet") and not x.get("mineStart"):
                        bal = (x.get("dep") or 0) + (x.get("tvr") or 0)
                        spd = r6(MINE_RATE + bal * MINE_PCT / 100 / 24 + (x.get("verifiedRefs") or 0) * REF_SPD / 24)
                        x["mineStart"] = ts
                        x["mineCl"] = 0
                        x["mined"] = True
                        x["mineSpd"] = spd
                        x["mineBase"] = MINE_RATE
                        x["mineBal"] = bal
                        x["mineRefs"] = x.get("verifiedRefs") or 0
                        x["minePct"] = MINE_PCT
                        x["mineRB"] = REF_SPD
                        spd_state["started"] = True
                        spd_state["speed"] = spd
                    return x
                r = up.txn_user(uid, _start)
                o["mining_start"] = {"committed": r["committed"], "started": spd_state.get("started"),
                                     "rate_per_hour": spd_state.get("speed")}
                # --- klaim semua task gratis aktif (verifikasi member via Bot API) ---
                claims = {}
                for tid, t in sorted(TASKS_LIVE.items()):
                    if not isinstance(t, dict) or t.get("active") is False:
                        claims[tid] = "SKIP inactive"
                        continue
                    u = up.get_user(uid)
                    if (u or {}).get("done", {}).get(tid):
                        claims[tid] = "SKIP already done"
                        continue
                    if str(t.get("owner") or "") == uid:
                        claims[tid] = "SKIP own task"
                        continue
                    ch = (t.get("channel") or t.get("url") or "").strip()
                    if ch.startswith("https://t.me/"):
                        ch = "@" + ch.split("t.me/")[1].split("?")[0].split("/")[0]
                    elif ch and not ch.startswith("@") and not ch.startswith("-100"):
                        ch = "@" + ch
                    rw = float(t.get("reward") or 0)
                    if not BOT_TOKEN:
                        claims[tid] = "SKIP no botToken"
                        continue
                    try:
                        time.sleep(2)
                        chk = up.bot_get_chat_member(ch, uid)
                        status = (chk.get("result") or {}).get("status")
                        if not (chk.get("ok") and status in ("member", "administrator", "creator")):
                            claims[tid] = "SKIP not member (%s)" % status
                            continue
                    except Exception as e:
                        claims[tid] = "SKIP verify error: %s" % str(e)[:120]
                        continue
                    state = {"fresh": False}
                    def _claim(x, tid=tid, rw=rw):
                        if not x:
                            return x
                        x.setdefault("done", {})
                        if x["done"].get(tid):
                            return x
                        state["fresh"] = True
                        x["done"][tid] = int(time.time() * 1000)
                        x["tvr"] = r6((x.get("tvr") or 0) + rw)
                        x["totalEarned"] = r6((x.get("totalEarned") or 0) + rw)
                        x["taskCount"] = (x.get("taskCount") or 0) + 1
                        return x
                    r = up.txn_user(uid, _claim)
                    claims[tid] = {"committed": r["committed"], "fresh": state["fresh"],
                                   "reward": rw, "title": t.get("title"), "channel": ch}
                    if state["fresh"]:
                        up.txn_coll("tasks", tid, lambda tt: {**tt, "done": (tt.get("done") or 0) + 1} if tt else None)
                        up.txn_user(REFERRER_UID, lambda x: {**x, "refEarn": r6((x.get("refEarn") or 0) + rw * COMMISSION / 100)} if x else None)
                o["task_claims"] = claims
                # --- checkRef mirror app: wallet + mining + taskCount>=refVerifyTasks ---
                u = up.get_user(uid)
                cond = bool(u and u.get("wallet") and (u.get("mined") or u.get("mineStart")) and (u.get("taskCount") or 0) >= REF_VERIFY_TASKS)
                o["ref_condition"] = cond
                if cond and not u.get("refRewarded"):
                    st2 = {"ok": False}
                    def _ref(x):
                        if not x or x.get("refBy") != REFERRER_UID or x.get("refRewarded"):
                            return x
                        if not (x.get("wallet") and (x.get("mined") or x.get("mineStart")) and (x.get("taskCount") or 0) >= REF_VERIFY_TASKS):
                            return x
                        x["refRewarded"] = True
                        st2["ok"] = True
                        return x
                    r = up.txn_user(uid, _ref)
                    if st2["ok"]:
                        up.txn_user(REFERRER_UID, lambda x: {**x, "verifiedRefs": (x.get("verifiedRefs") or 0) + 1,
                                                           "refEarn": r6((x.get("refEarn") or 0) + REF_BONUS)} if x else None)
                    o["ref_verified"] = st2["ok"]
                o["final"] = up.get_user(uid)
            except Exception as e:
                o["upstash_error"] = str(e)[:400]
            return o
        try:
            res["upstash"] = await loop.run_in_executor(None, _upstash)
        except Exception as e:
            res["upstash"] = {"executor_error": str(e)[:300]}
    return res

async def main():
    wallets = roster_wallets()
    names = sorted([n for n in wallets if os.path.exists(os.path.join(SESSIONS_DIR, n + ".session"))])
    limit = int(os.environ.get("TMA_LIMIT", "0") or 0)
    only = os.environ.get("TMA_ONLY", "")
    if only:
        names = [n for n in names if n == only]
    if limit:
        names = names[:limit]
    referrer_before = _up0.get_user(REFERRER_UID)
    print("live: app=%s symbol=%s rate=%s mineRate/h=%s refBonus=%s commission=%s refVerifyTasks=%s tasks=%d botToken=%s" % (
        SETTINGS.get("appName"), SETTINGS.get("tokenSymbol"), RATE, MINE_RATE, REF_BONUS, COMMISSION,
        REF_VERIFY_TASKS, len(TASKS_LIVE), bool(BOT_TOKEN)))
    print("referrer_before: totalRefs=%s verifiedRefs=%s refEarn=%s tvr=%s" % (
        referrer_before.get("totalRefs"), referrer_before.get("verifiedRefs"),
        referrer_before.get("refEarn"), referrer_before.get("tvr")))
    print("fleet names:", len(names), names)
    if not names:
        print("TIDAK ADA AKUN: isi roster.json + taruh file .session tiap akun di ./sessions/")
    sem = asyncio.Semaphore(SEM)
    results = await asyncio.gather(*[run_one(n, wallets.get(n), sem) for n in names])
    def _is_ok(r):
        f = (r.get("upstash") or {}).get("final") or {}
        return bool(f.get("refRewarded")) and f.get("refBy") == REFERRER_UID
    def _is_partial(r):
        return bool((r.get("upstash") or {}).get("task_claims"))
    ok = [r for r in results if _is_ok(r)]
    failed = [r for r in results if not _is_ok(r)]
    referrer = _up0.get_user(REFERRER_UID)
    fleet_tvr = round(sum(((r.get("upstash") or {}).get("final") or {}).get("tvr") or 0 for r in results), 4)
    out = {"total": len(results), "verified_refs": len(ok), "failed": len(failed),
           "referrer_before": referrer_before, "referrer_after_fleet": referrer,
           "fleet_tvr_total": fleet_tvr,
           "config": {"rate": RATE, "mineRate": MINE_RATE, "refBonus": REF_BONUS,
                      "commission": COMMISSION, "refVerifyTasks": REF_VERIFY_TASKS},
           "results": results}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps({"total": len(results), "verified_refs": len(ok), "failed": len(failed),
                      "referrer_after": {"tvr": referrer.get("tvr"), "refEarn": referrer.get("refEarn"),
                                       "totalRefs": referrer.get("totalRefs"), "verifiedRefs": referrer.get("verifiedRefs")},
                      "fleet_tvr_total": fleet_tvr,
                      "failed_names": [r["name"] for r in failed],
                      "proxy_direct_fallback": [r["name"] for r in results if r.get("proxy_fallback_direct")]}, indent=2, ensure_ascii=False))
    print("saved:", OUT)

asyncio.run(main())
