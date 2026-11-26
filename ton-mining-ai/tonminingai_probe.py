#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TON MINING AI (@TonMiningai_Bot) — Probe akun utama, stage 2 (adapted from QTF probe2, same white-label template).
Mirror persis alur Mini App -> Upstash REST (token dibaca dari HTML Mini App, TIDAK PERNAH di-print).
GRATIS saja: tanpa deposit, tanpa WD, tanpa kirim dana. Output: ./tonminingai_probe.json

CARA ISI:
  export TG_API_ID=123456 TG_API_HASH=xxx TG_SESSION=./sessions/utama.session
  export TG_USER_ID=123456789 TG_USERNAME=username_kamu TON_WALLET=UQ...
  Simpan HTML Mini App sebagai ./tonminingai_webapp.html (buka Mini App di browser,
  simpan halaman lengkap) - UP_URL + UP_TOKEN dibaca dari file itu.
"""
import asyncio, json, os, re, shutil, sys, time, urllib.request, urllib.parse
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

BOT = "TonMiningai_Bot"
# --- ISI DENGAN DATA KAMU (jangan commit file berisi data asli) ---
API_ID = int(os.environ.get("TG_API_ID", "0") or 0)
API_HASH = os.environ.get("TG_API_HASH", "")
SESSION = os.environ.get("TG_SESSION", "./sessions/utama.session")
UID = os.environ.get("TG_USER_ID", "")  # ID Telegram akun utama kamu
USERNAME = os.environ.get("TG_USERNAME", "username_kamu")
WALLET_TON = os.environ.get("TON_WALLET", "")  # alamat wallet TON kamu (UQ.../EQ...)
assert API_ID and API_HASH and UID and WALLET_TON, "isi TG_API_ID/TG_API_HASH/TG_USER_ID/TON_WALLET dulu"
OUT = "./tonminingai_probe.json"
HTML = "./tonminingai_webapp.html"
NS = "zv3"
TONRE = re.compile(r"^(UQ|EQ|kQ|0Q)[A-Za-z0-9_-]{46}$")

html = open(HTML, encoding="utf-8", errors="ignore").read()
UP_URL = re.search(r'UP_URL="([^"]+)"', html).group(1)
UP_TOKEN = re.search(r'UP_TOKEN="([^"]+)"', html).group(1)

def r6(n):
    return round(float(n or 0), 6)

def _req(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + UP_TOKEN, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)

def cmd(a):
    j = _req(UP_URL, a)
    if j.get("error"):
        raise RuntimeError(str(j["error"]))
    return j["result"]

def multi(a):
    j = _req(UP_URL + "/multi-exec", a)
    if not isinstance(j, list):
        raise RuntimeError(str(j))
    out = []
    for x in j:
        if x.get("error"):
            raise RuntimeError(str(x["error"]))
        out.append(x["result"])
    return out

CAS = ("local c=redis.call('HGET',KEYS[1],ARGV[1]) if ARGV[2]=='__NIL__' then if c then return 0 end "
       "elseif c~=ARGV[2] then return 0 end if ARGV[3]=='__NIL__' then redis.call('HDEL',KEYS[1],ARGV[1]) "
       "else redis.call('HSET',KEYS[1],ARGV[1],ARGV[3]) end redis.call('INCR',KEYS[2]) redis.call('INCR',KEYS[3]) return 1")

def hk(c):
    return NS + ":" + c

def vk(c, d=None):
    return NS + ":v:" + c + ((":" + d) if d else "")

def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))

def hgetall(coll):
    a = cmd(["HGETALL", hk(coll)])
    o = {}
    for i in range(0, len(a), 2):
        try:
            o[a[i]] = json.loads(a[i + 1])
        except Exception:
            o[a[i]] = a[i + 1]
    return o

def get_user(uid):
    raw = cmd(["HGET", hk("users"), uid])
    return json.loads(raw) if raw else None

def txn_coll(coll, key, fn, tries=10):
    for _ in range(tries):
        raw = cmd(["HGET", hk(coll), key])
        doc = json.loads(raw) if raw else None
        out = fn(doc)
        if out is None:
            return {"committed": False}
        nr = "__NIL__" if out is None else js(out)
        ok = cmd(["EVAL", CAS, 3, hk(coll), vk(coll), vk(coll, key), key,
                  "__NIL__" if raw is None else raw, nr])
        if ok == 1:
            return {"committed": True}
    raise RuntimeError("transaction conflict x10")

def txn_user(uid, fn, tries=10):
    return txn_coll("users", uid, fn, tries)

def sNow():
    t = cmd(["TIME"])
    return int(t[0]) * 1000 + int(int(t[1]) / 1000)

def bot_get_chat_member(bot_token, channel, user_id):
    url = ("https://api.telegram.org/bot%s/getChatMember?chat_id=%s&user_id=%s"
           % (bot_token, urllib.parse.quote(channel), user_id))
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

async def telethon_join(channels):
    sess = SESSION
    res = {}
    client = None
    try:
        client = TelegramClient(sess, API_ID, API_HASH)
        await client.connect()
        me = await client.get_me()
        res["me"] = {"id": me.id, "username": me.username}
        for ch in channels:
            try:
                await client(JoinChannelRequest(ch))
                res[ch] = "joined-ok"
            except Exception as e:
                res[ch] = "ERR: %s: %s" % (type(e).__name__, str(e)[:150])
            await asyncio.sleep(1)
    finally:
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass
        for f in (dst, dst + "-journal"):
            try:
                os.remove(f)
            except Exception:
                pass
    return res

def main():
    res = {"bot": BOT, "uid": UID, "wallet_ton": WALLET_TON, "phase": "probe2-upstash"}
    # 0. Baca live: settings/tasks/packages/links/gate/promos + user + wallets + wd/dep index
    settings = hgetall("settings")
    res["settings_live"] = {k: v for k, v in settings.items() if k != "botToken"}
    res["settings_keys"] = sorted(settings.keys())
    bot_token = settings.get("botToken")
    res["has_bot_token_in_settings"] = bool(bot_token)
    res["tasks_live"] = hgetall("tasks")
    res["packages_live"] = hgetall("packages")
    res["links_live"] = hgetall("links")
    res["gate_live"] = hgetall("gate")
    res["promos_live"] = hgetall("promos")
    try:
        res["users_count"] = cmd(["HLEN", hk("users")])
    except Exception as e:
        res["users_count"] = "ERR %s" % e
    before = get_user(UID)
    res["registered_before"] = before is not None
    res["user_before"] = before
    try:
        res["wallet_owner_before"] = cmd(["HGET", hk("wallets"), WALLET_TON])
    except Exception as e:
        res["wallet_owner_before"] = "ERR %s" % e
    try:
        res["withdrawal_ids"] = cmd(["LRANGE", NS + ":i:withdrawals:" + UID, 0, -1])
        res["deposit_ids"] = cmd(["LRANGE", NS + ":i:deposits:" + UID, 0, -1])
    except Exception as e:
        res["wd_dep_index_err"] = str(e)[:200]

    cfg = lambda k, d: settings.get(k) if settings.get(k) not in (None, "") else d
    RATE = float(cfg("rate", 500))
    MINE_RATE = float(cfg("mineRate", 5.4))
    MINE_PCT = float(cfg("mineBalancePct", 5))
    REF_BONUS = float(cfg("refBonus", 0))
    REF_SPD = float(cfg("refSpeedBonus", 1))
    COMMISSION = float(cfg("commission", 10))
    REF_VERIFY_TASKS = int(float(cfg("refVerifyTasks", 1)))
    res["derived"] = {"rate_QTF_per_unit": RATE, "mineRate_QTF_h": MINE_RATE,
                      "per_24h_base_QTF": round(MINE_RATE * 24, 4),
                      "refBonus": REF_BONUS, "commission_pct": COMMISSION,
                      "refVerifyTasks": REF_VERIFY_TASKS,
                      "minWithdrawTokens": cfg("minWithdrawTokens", 500),
                      "maxWithdrawTokens": cfg("maxWithdrawTokens", 0),
                      "maxWithdrawCount": cfg("maxWithdrawCount", 0),
                      "wdPerDeposit": cfg("wdPerDeposit", 0),
                      "wdFeeTokens": cfg("wdFeeTokens", 0), "wdFeePercent": cfg("wdFeePercent", 0),
                      "tokenSymbol": settings.get("tokenSymbol") or settings.get("symbol") or "QTF",
                      "appName": settings.get("appName"),
                      "minDeposit": cfg("minDeposit", 0.01), "minGram": cfg("minGram", 0.01),
                      "gramAddress": settings.get("gramAddress"),
                      "depositAddress_BEP20": settings.get("depositAddress"),
                      "maintenance": settings.get("maintenance"),
                      "paymentChannel": settings.get("paymentChannel"),
                      "miniAppLink": settings.get("miniAppLink")}

    # 1. Telethon: join gate + task channels
    join_targets = []
    for g in res["gate_live"].values():
        ch = (g or {}).get("channel") or (g or {}).get("url")
        if ch:
            join_targets.append(ch)
    for t in res["tasks_live"].values():
        ch = (t or {}).get("channel")
        if ch:
            join_targets.append(ch)
    join_targets = sorted(set(join_targets))
    res["join_targets"] = join_targets
    res["telethon"] = asyncio.run(telethon_join(join_targets))

    # 2. Registrasi (mirror init()) — refBy None (daftar murni, tanpa ref orang lain)
    if before is None:
        ts = sNow()
        new_user = {"uid": UID, "name": "AkunUtama", "username": USERNAME,
                    "dep": 0, "locked": 0, "tvr": 0, "usdt": 0, "refEarn": 0,
                    "totalRefs": 0, "verifiedRefs": 0, "refBy": None, "refRewarded": False,
                    "taskCount": 0, "done": {}, "promos": {}, "banned": False, "createdAt": ts}
        r = txn_user(UID, lambda x: new_user if x is None else None)
        res["register"] = {"committed": r["committed"], "refBy": None, "createdAt": ts}
    else:
        res["register"] = {"skipped": "already registered", "refBy_existing": before.get("refBy")}

    # 3. Link wallet (mirror #wAdd): wallets/<addr> txn + users wallet/walletAt
    assert TONRE.match(WALLET_TON), "format wallet tidak valid"
    u_now = get_user(UID)
    old_wallet = (u_now or {}).get("wallet")
    st = {"ok": False}
    def _wlink(x):
        if x and x != UID:
            return x
        st["ok"] = True
        return UID
    r = txn_coll("wallets", WALLET_TON, _wlink)
    res["wallet_link"] = {"committed": r["committed"], "ok": st["ok"], "old_wallet": old_wallet}
    if st["ok"]:
        ts = sNow()
        def _setwal(x):
            if x:
                x["wallet"] = WALLET_TON
                x["walletAt"] = ts
            return x
        r2 = txn_user(UID, _setwal)
        res["wallet_set"] = {"committed": r2["committed"]}
        if old_wallet and old_wallet != WALLET_TON:
            txn_coll("wallets", old_wallet, lambda x: None if x == UID else x)
            res["wallet_old_released"] = old_wallet

    # 4. Start mining (mirror #start, snapshot penuh)
    ts = sNow()
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
    r = txn_user(UID, _start)
    res["mining_start"] = {"committed": r["committed"], "started": spd_state.get("started"),
                           "mineStart": ts if spd_state.get("started") else None,
                           "rate_per_hour": spd_state.get("speed"),
                           "per_24h_QTF": round(spd_state["speed"] * 24, 4) if spd_state.get("speed") else None}

    # 5. Klaim semua task gratis (join-channel): verifikasi via Bot API lalu txn klaim
    claims = {}
    if bot_token:
        for tid, t in sorted(res["tasks_live"].items()):
            if not isinstance(t, dict) or t.get("active") is False:
                claims[tid] = "SKIP inactive"
                continue
            u = get_user(UID)
            if (u or {}).get("done", {}).get(tid):
                claims[tid] = "SKIP already done"
                continue
            if str(t.get("owner") or "") == UID:
                claims[tid] = "SKIP own task"
                continue
            ch = (t.get("channel") or t.get("url") or "").strip()
            if ch.startswith("https://t.me/"):
                ch = "@" + ch.split("t.me/")[1].split("?")[0].split("/")[0]
            elif ch and not ch.startswith("@") and not ch.startswith("-100"):
                ch = "@" + ch
            rw = float(t.get("reward") or 0)
            try:
                time.sleep(4)
                chk = bot_get_chat_member(bot_token, ch, UID)
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
            r = txn_user(UID, _claim)
            claims[tid] = {"committed": r["committed"], "fresh": state["fresh"],
                           "reward": rw, "title": t.get("title"), "channel": ch}
            if state["fresh"]:
                txn_coll("tasks", tid, lambda tt: {**tt, "done": (tt.get("done") or 0) + 1} if tt else None)
    else:
        claims = {"error": "no botToken in settings — cannot verify tasks"}
    res["task_claims"] = claims

    # 6. Baca balik final
    res["user_final"] = get_user(UID)
    try:
        res["wallet_owner_final"] = cmd(["HGET", hk("wallets"), WALLET_TON])
    except Exception as e:
        res["wallet_owner_final"] = "ERR %s" % e
    res["ref_link"] = "https://t.me/TonMiningai_Bot/app?startapp=ref_" + UID
    with open(OUT, "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    # ringkasan tanpa secrets
    u = res["user_final"] or {}
    print("registered_before:", res["registered_before"])
    print("settings appName:", res["derived"]["appName"], "| symbol:", res["derived"]["tokenSymbol"],
          "| rate:", RATE, "| mineRate/h:", MINE_RATE, "| refBonus:", REF_BONUS, "| commission:", COMMISSION)
    print("minWD:", res["derived"]["minWithdrawTokens"], "| maxWD:", res["derived"]["maxWithdrawTokens"],
          "| maxWDCount:", res["derived"]["maxWithdrawCount"], "| wdPerDeposit:", res["derived"]["wdPerDeposit"],
          "| fee:", res["derived"]["wdFeeTokens"], "+", res["derived"]["wdFeePercent"], "%")
    print("minDeposit:", res["derived"]["minDeposit"], "| minGram:", res["derived"]["minGram"])
    print("tasks:", len(res["tasks_live"]), "| packages:", len(res["packages_live"]),
          "| gate:", len(res["gate_live"]), "| links:", len(res["links_live"]),
          "| promos:", len(res["promos_live"]), "| users_count:", res["users_count"])
    print("joins:", res["telethon"])
    print("wallet_link:", res["wallet_link"], "| wallet_set:", res.get("wallet_set"))
    print("mining:", res["mining_start"])
    print("claims:", json.dumps(claims, ensure_ascii=False))
    print("FINAL tvr:", u.get("tvr"), "| totalEarned:", u.get("totalEarned"),
          "| taskCount:", u.get("taskCount"), "| dep:", u.get("dep"),
          "| refBy:", u.get("refBy"), "| verifiedRefs:", u.get("verifiedRefs"),
          "| mineStart:", u.get("mineStart"), "| mineSpd:", u.get("mineSpd"))
    print("ref_link:", res["ref_link"])
    print("saved:", OUT)

main()
