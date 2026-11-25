#!/usr/bin/env python3
"""GOLD CLICKER / EarnGCM — skrip umum (publik, tanpa kredensial).

Game web mining: main di https://play.earngcm.fun/ (versi browser),
kumpulkan Gold Bar, convert ke SOL lewat faucet https://www.earngcm.fun/faucet.
Rate: 1 Gold Bar = 0,0001 SOL. Min klaim 25 Bar, max 100 Bar/hari/akun.
Reset harian 00:00 UTC. Faucet pool TERBATAS — klaim selagi masih ada.

Skrip ini TIDAK berisi akun/kunci siapa pun. Semua akun dibuat dari NOL
(guest) dan disimpan lokal di gcm_account.json — JANGAN disebar ke orang lain.

Cara pakai:
  python3 gcm_umum.py status            # cek faucet (buka/tutup, pool, total terbayar)
  python3 gcm_umum.py daftar            # buat akun guest baru + lihat saldo
  python3 gcm_umum.py klaim --code WEB... --wallet <alamat SOL kamu> --bars 25
      # klaim faucet. Kode WEB didapat di game: Settings -> Account ->
      # GET WEBSITE CODE (berlaku 10 menit, sekali pakai).
      # --bars 25-100, harus <= saldo Bar kamu di game.

Butuh: python3 + requests (pip install requests) atau stdlib saja (urllib).
"""
import argparse, json, os, sys, time, uuid

try:
    import requests
    HAVE_REQ = True
except ImportError:
    HAVE_REQ = False
    import urllib.request, urllib.error

BASE = "https://gcm-demo-api.onrender.com"
ACCT = "gcm_account.json"
REF_CODE = ""  # isi kode referral temanmu kalau mau (dipakai di dalam game: INVITE A FRIEND)

def call(method, path, body=None, token=None, extra_headers=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if extra_headers:
        headers.update(extra_headers)
    if HAVE_REQ:
        r = requests.request(method, url, json=body, headers=headers, timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text[:500]}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"raw": "http error"}

def faucet_status():
    s, terms = call("GET", "/v1/faucet/terms")
    s2, log = call("GET", "/v1/faucet/log")
    print("== FAUCET GOLD CLICKER ==")
    print("Buka:", terms.get("open"), "| Pause:", terms.get("paused"))
    print("Rate: 1 Bar =", terms.get("lamportsPerBar", 100000) / 1e9, "SOL")
    print("Min klaim:", terms.get("minBars"), "Bar | Max/hari:", terms.get("dailyBars"), "Bar")
    print("Reset:", terms.get("resetsAt"))
    print("Total klaim:", log.get("claims"), "| Total Bar terbayar:", log.get("bars"),
          "| Total SOL:", log.get("lamports", 0) / 1e9)
    print("Wallet faucet:", log.get("faucetWallet"))
    sent = log.get("sent") or []
    if sent:
        print("Klaim terakhir:", sent[0].get("at"), "-", sent[0].get("bars"), "Bar ->",
              str(sent[0].get("wallet"))[:12] + "...")

def load_acct():
    if not os.path.exists(ACCT):
        return None
    return json.load(open(ACCT))

def save_acct(a):
    json.dump(a, open(ACCT, "w"), indent=1)
    print("Akun tersimpan di", ACCT, "- JANGAN disebar (ini kuncimu).")

def refresh(acct):
    s, b = call("POST", "/v1/auth/refresh", {"refreshToken": acct["refreshToken"]})
    if s != 200:
        print("Refresh gagal:", s, b)
        return None
    acct["accessToken"] = b["accessToken"]
    if b.get("refreshToken"):
        acct["refreshToken"] = b["refreshToken"]  # token BEROTASI tiap refresh
    save_acct(acct)
    return acct["accessToken"]

def cmd_daftar(_args):
    s, b = call("POST", "/v1/auth/guest", {})
    if s != 200:
        print("Gagal buat akun:", s, b)
        return
    acct = {"playerCode": None, "accessToken": b["accessToken"],
            "refreshToken": b["refreshToken"]}
    s2, me = call("GET", "/v1/players/me", token=acct["accessToken"])
    acct["playerCode"] = me.get("playerCode")
    acct["playerId"] = me.get("playerId")
    save_acct(acct)
    print("Akun guest baru dibuat!")
    print("playerCode (kode referral kamu):", acct["playerCode"])
    print("Saldo gold (coins):", (me.get("balances") or {}).get("gold"))
    print("Main dulu di https://play.earngcm.fun/ sampai dapat Gold Bar,")
    print("lalu klaim lewat faucet (lihat: python3 gcm_umum.py klaim --help).")

def cmd_status(_args):
    faucet_status()
    acct = load_acct()
    if acct:
        at = refresh(acct)
        if at:
            s, me = call("GET", "/v1/players/me", token=at)
            print("== AKUNMU ==")
            print("playerCode:", me.get("playerCode"))
            print("Saldo gold (coins):", (me.get("balances") or {}).get("gold"))

def cmd_klaim(args):
    acct = load_acct()
    if not acct:
        print("Belum ada akun lokal. Jalankan dulu: python3 gcm_umum.py daftar")
        return
    if not (25 <= args.bars <= 100):
        print("Jumlah Bar harus 25-100.")
        return
    at = refresh(acct)
    if not at:
        return
    s, me = call("GET", "/v1/players/me", token=at)
    print("Akun:", me.get("playerCode"), "| gold (coins):",
          (me.get("balances") or {}).get("gold"))
    # 1. sesi faucet dari website code (berlaku 10 menit, sekali pakai)
    s, sess = call("POST", "/v1/faucet/sessions", {"code": args.code})
    if s != 200:
        print("Sesi faucet gagal (kode salah/kedaluwarsa?):", s, sess)
        return
    val = sess.get("value") or sess
    session = val.get("session") or val.get("id")
    if not session:
        print("Sesi faucet tidak mengembalikan token:", sess)
        return
    hdr = {"X-Faucet-Session": session}
    print("Sesi faucet OK.")
    # 2. cek akun faucet (saldo Bar + wallet yang terikat)
    s, acc = call("GET", "/v1/faucet/account", extra_headers=hdr)
    aval = (acc or {}).get("value") or acc
    print("Saldo Bar (faucet):", aval.get("bars"), "| wallet terikat:",
          aval.get("wallet"))
    if isinstance(aval.get("bars"), (int, float)) and aval["bars"] < args.bars:
        print("Bar kamu belum cukup untuk klaim", args.bars,
              "- main dulu di game (dive + misi harian).")
        return
    # 3. daftarkan wallet SOL (kalau belum terikat)
    if not aval.get("wallet"):
        s, w = call("POST", "/v1/faucet/wallet", {"wallet": args.wallet},
                    extra_headers=hdr)
        print("Daftar wallet:", s, str(w)[:300])
        if s != 200:
            print("Gagal daftar wallet. Cek alamat SOL kamu.")
            return
    elif aval.get("wallet") != args.wallet:
        print("Wallet yang terikat di sesi ini:", aval.get("wallet"),
              "- klaim akan dikirim ke alamat itu.")
    # 4. klaim (idempotent: claimId yang sama tidak akan klaim 2x)
    claim_id = str(uuid.uuid4())
    s, c = call("POST", "/v1/faucet/claims",
                {"claimId": claim_id, "bars": args.bars}, extra_headers=hdr)
    print("Klaim:", s, str(c)[:400])
    if s != 200:
        return
    cval = (c or {}).get("value") or c
    cid = cval.get("id") or claim_id
    for _ in range(20):
        time.sleep(5)
        s, st = call("GET", f"/v1/faucet/claims/{cid}", extra_headers=hdr)
        sval = (st or {}).get("value") or st
        print("Status klaim:", s, str(sval)[:400])
        if isinstance(sval, dict) and sval.get("status") in ("paid", "done", "completed"):
            print("TERBAYAR! tx:", sval.get("signature") or sval.get("tx"))
            return
        if isinstance(sval, dict) and sval.get("status") in ("failed", "rejected", "expired"):
            print("Klaim gagal:", sval.get("status"))
            return
    print("Klaim masih diproses — cek lagi nanti di https://www.earngcm.fun/faucet")

def main():
    ap = argparse.ArgumentParser(description="GOLD CLICKER / EarnGCM — skrip umum")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="cek faucet + saldo akunmu")
    sub.add_parser("daftar", help="buat akun guest baru")
    k = sub.add_parser("klaim", help="klaim faucet (butuh website code dari game)")
    k.add_argument("--code", required=True, help="website code, diawali WEB (dari Settings game)")
    k.add_argument("--wallet", required=True, help="alamat SOL kamu (milikmu sendiri)")
    k.add_argument("--bars", type=int, default=25, help="jumlah Bar (25-100)")
    a = ap.parse_args()
    {"status": cmd_status, "daftar": cmd_daftar, "klaim": cmd_klaim}[a.cmd](a)

if __name__ == "__main__":
    main()
