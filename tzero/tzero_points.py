#!/usr/bin/env python3
"""TZERO ($T0) — cek poin Pre-flight Season 0 + cari misi hampir liftoff.

Testnet Base Sepolia. TIDAK butuh private key, TIDAK butuh login:
poin bisa dicek publik per alamat wallet.

Cara pakai:
    python3 tzero_points.py 0xALAMAT_WALLET_KAMU

Keluaran: total poin, rincian Fuel/Crew/Liftoff/Staking/Signal,
status eligible (min 500 pts), + 5 misi live yang paling dekat
liftoff (target bagus buat misi beli/hold 0,01 ETH -> Crew +150).

Sumber data: API publik testnet.tzer0.fun (sama yang dipakai
dashboard Points di web).
"""
import json
import sys
import urllib.request

BASE = "https://testnet.tzer0.fun"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) < 2:
        print("Pakai: python3 tzero_points.py 0xALAMAT_WALLET")
        return
    addr = sys.argv[1].strip()
    p = get(f"{BASE}/api/points/{addr}")
    print("Alamat      :", p.get("address"))
    print("Total poin  :", p.get("total"), "(min 500 buat eligible)")
    print("  Fuel      :", p.get("fuel"))
    print("  Crew      :", p.get("crew"))
    print("  Liftoff   :", p.get("liftoff"))
    print("  Staking   :", p.get("staking"))
    print("  Signal    :", p.get("signal"))
    print("Eligible    :", p.get("eligible"))
    print("Rank        :", p.get("rank"), "dari", p.get("rankedWallets"), "wallet")
    print()
    print("== Misi live terdekat liftoff (progress tertinggi) ==")
    data = get(f"{BASE}/api/missions?limit=100")
    missions = sorted(data.get("missions", []),
                      key=lambda m: m.get("progressBps", 0), reverse=True)[:5]
    for m in missions:
        print(f"  #{m['id']} {m['symbol']} — {m.get('progressPercent')}% "
              f"— token {m['token']}")


if __name__ == "__main__":
    main()
