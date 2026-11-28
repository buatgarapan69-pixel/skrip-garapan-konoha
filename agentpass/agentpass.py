#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENTPASS (APASS) — Paspor Soulbound Gratis (BNB Smart Chain)
Paspor aktivitas buat pemegang Binance Agent ID. 1 paspor per alamat,
soulbound (tidak bisa dipindah). Check-in harian gratis naikkan streak + level.

PENTING: situs TIDAK ADA tombol mint. Satu-satunya cara mint adalah
panggil mint() langsung di kontrak (value 0) — persis yang dilakukan skrip ini.

Cara pakai (1 perintah saja):
    python3 agentpass.py
Lalu pilih menu di dalam skrip.

Yang kamu butuhkan:
  - Wallet BSC yang pegang Binance Agent ID (SPACE ID)
  - Sedikit BNB buat gas (mint kami: ~0,0000078 BNB)
  - CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu
    (perintah yang dipakai: `baw contract-call preview` + `execute`)

Fungsi yang dipakai (terverifikasi dari tx on-chain + repo proyek):
  - mint()    -> 0x1249c58b | value 0 | gas ~103.000
  - checkIn() -> 0x183ff085 | value 0 | 1x per hari UTC
  - Kontrak   -> 0x2CaB70C426F92C0d08aEb7cFe41b27b746feEb09
  - Founder edition: 1.000 paspor (sisa 534 saat kami mint)

TIDAK ADA private key / seed phrase / session di skrip ini.
Isi alamat wallet kamu sendiri saat skrip bertanya.
"""
import json
import subprocess
import sys
import urllib.request

RPC = "https://bsc-dataseed.binance.org"
CONTRACT = "0x2CaB70C426F92C0d08aEb7cFe41b27b746feEb09"
CALLDATA_MINT = "0x1249c58b"       # mint()
CALLDATA_CHECKIN = "0x183ff085"    # checkIn()
GAS_MINT = "180000"
GAS_CHECKIN = "150000"
SITE = "https://agentpass-sigma.vercel.app"

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
RESET = "\033[0m"


def rpc_call(to_addr, data):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": to_addr, "data": data}, "latest"],
    }).encode()
    req = urllib.request.Request(
        RPC, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        out = json.load(resp)
    if "error" in out:
        raise RuntimeError(out["error"].get("message", out["error"]))
    return int(out["result"], 16)


def balance_of(wallet):
    data = "0x70a08231" + "00" * 12 + wallet[2:].lower()
    return rpc_call(CONTRACT, data)


def free_given():
    return rpc_call(CONTRACT, "0x3aedb2f1")  # freeGiven()


def free_remaining():
    return rpc_call(CONTRACT, "0x5a781a6b")  # freeRemaining()


def level_of(wallet):
    data = "0x5c138c9d" + "00" * 12 + wallet[2:].lower()
    return rpc_call(CONTRACT, data)


def baw_call(wallet, calldata, gas_limit, label):
    cmd = ["baw", "contract-call", "preview",
           "--binanceChainId", "56", "--from", wallet,
           "--to", CONTRACT, "--value", "0",
           "--inputData", calldata, "--gasLimit", gas_limit, "--json"]
    print(f"{C}[*] Preview {label} (simulasi dulu, belum ada tx)...{RESET}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(r.stdout[:1000])
    if r.stderr:
        print(f"{Y}[!] {r.stderr[:300]}{RESET}")
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout}


def baw_execute(request_id):
    cmd = ["baw", "contract-call", "execute",
           "--requestId", request_id, "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    print(r.stdout[:1000])
    if r.stderr:
        print(f"{Y}[!] {r.stderr[:300]}{RESET}")
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout}


def run_flow(wallet, calldata, gas_limit, label):
    prev = baw_call(wallet, calldata, gas_limit, label)
    req_id = prev.get("requestId") or prev.get("request_id")
    if not req_id:
        print(f"{R}[!] Preview gagal / tidak ada requestId — cek output di atas. "
              f"Jangan lanjut kalau simulasi revert.{RESET}")
        return
    print(f"{G}[+] Preview OK, requestId: {req_id}{RESET}")
    ok = input(f"Eksekusi {label} sekarang? (y/N) » ").strip().lower()
    if ok != "y":
        print("Dibatalkan, tidak ada tx terkirim.")
        return
    baw_execute(req_id)
    print(f"{G}[+] Selesai. Cek tx di BscScan, lalu cek status (menu 1).{RESET}")


def menu():
    print(f"\n{R}🎫 AGENTPASS — Paspor Soulbound Gratis Buat Agent ID{RESET}")
    print(f"{C}Kontrak: {CONTRACT}{RESET}")
    print(f"{C}Situs:   {SITE}{RESET}")
    print(f"{W}[1]{RESET} Cek status (paspor + level + kuota Founder)")
    print(f"{W}[2]{RESET} Mint 1 paspor gratis (via contract call)")
    print(f"{W}[3]{RESET} Check-in harian gratis (naikkan streak + level)")
    print(f"{W}[4]{RESET} Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    print(f"{G}Mint gratis, cuma gas. Nilai BELUM TERBUKTI — ini paspor aktivitas, bukan janji cuan.{RESET}")
    wallet = input("Alamat wallet BSC kamu (0x...) » ").strip()
    if not (wallet.startswith("0x") and len(wallet) == 42):
        print(f"{R}[!] Alamat wallet tidak valid.{RESET}")
        sys.exit(1)
    while True:
        pil = menu()
        if pil == "1":
            try:
                print(f"Paspor kamu: {balance_of(wallet)}")
                print(f"Level kamu: {level_of(wallet)} (0-4, dari streak check-in)")
                print(f"Founder sudah dibagi: {free_given()} / 1.000")
                print(f"Founder tersisa: {free_remaining()}")
            except Exception as e:
                print(f"{R}[!] Gagal baca on-chain: {e}{RESET}")
        elif pil == "2":
            if balance_of(wallet) >= 1:
                print(f"{Y}[!] Kamu sudah pegang paspor (1 per alamat, selamanya).{RESET}")
                continue
            run_flow(wallet, CALLDATA_MINT, GAS_MINT, "mint")
        elif pil == "3":
            if balance_of(wallet) < 1:
                print(f"{Y}[!] Belum punya paspor — mint dulu (menu 2).{RESET}")
                continue
            run_flow(wallet, CALLDATA_CHECKIN, GAS_CHECKIN, "check-in")
        elif pil == "4":
            print("Keluar.")
            break
        else:
            print(f"{Y}[!] Pilih 1/2/3/4.{RESET}")


if __name__ == "__main__":
    main()
