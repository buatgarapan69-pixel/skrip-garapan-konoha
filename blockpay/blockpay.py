#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLOCKPAY GENESIS — Free Mint NFT (BNB Smart Chain)
3.333 Digital Guardian NFT, 1.111 jatah gratis (1 per wallet, cuma gas).

Cara pakai (1 perintah saja):
    python3 blockpay.py
Lalu pilih menu di dalam skrip.

Yang kamu butuhkan:
  - Wallet BSC (tanpa syarat Agent ID)
  - Sedikit BNB buat gas (mint kami: ~0,0000088 BNB)
  - CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu
    (perintah yang dipakai: `baw contract-call preview` + `execute`)

Fungsi yang dipakai (terverifikasi dari tx on-chain):
  - freeMint() -> 0x5b70ea9f | value 0 | gas ~137.000
  - Kontrak    -> 0x0BF3Cf8eEeC4fE71305738c75aA9574A24DDf57b
  - Free mint s.d. 30 Nov 2026, listing Element mulai 2 Des 2026

TIDAK ADA private key / seed phrase / session di skrip ini.
Isi alamat wallet kamu sendiri saat skrip bertanya.
"""
import json
import subprocess
import sys
import urllib.request

RPC = "https://bsc-dataseed.binance.org"
CONTRACT = "0x0BF3Cf8eEeC4fE71305738c75aA9574A24DDf57b"
CALLDATA_FREE_MINT = "0x5b70ea9f"  # freeMint()
GAS_LIMIT = "200000"
SITE = "https://blockpay.world"

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


def free_minted():
    return rpc_call(CONTRACT, "0xd10a1a2b")  # freeMinted()


def total_supply():
    return rpc_call(CONTRACT, "0x18160ddd")


def baw_preview(wallet):
    cmd = ["baw", "contract-call", "preview",
           "--binanceChainId", "56", "--from", wallet,
           "--to", CONTRACT, "--value", "0",
           "--inputData", CALLDATA_FREE_MINT, "--gasLimit", GAS_LIMIT, "--json"]
    print(f"{C}[*] Preview (simulasi dulu, belum ada tx)...{RESET}")
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


def menu():
    print(f"\n{R}🛡️ BLOCKPAY GENESIS — Free Mint 1.111 Guardian NFT{RESET}")
    print(f"{C}Kontrak: {CONTRACT}{RESET}")
    print(f"{C}Situs:   {SITE}{RESET}")
    print(f"{W}[1]{RESET} Cek status (saldo NFT + free terpakai + total supply)")
    print(f"{W}[2]{RESET} Free mint 1 NFT (preview dulu, baru eksekusi)")
    print(f"{W}[3]{RESET} Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    print(f"{G}Mint gratis, cuma gas. Nilai NFT BELUM TERBUKTI — belum ada pasar.{RESET}")
    wallet = input("Alamat wallet BSC kamu (0x...) » ").strip()
    if not (wallet.startswith("0x") and len(wallet) == 42):
        print(f"{R}[!] Alamat wallet tidak valid.{RESET}")
        sys.exit(1)
    while True:
        pil = menu()
        if pil == "1":
            try:
                print(f"NFT kamu: {balance_of(wallet)}")
                print(f"Free sudah terpakai: {free_minted()} / 1.111")
                print(f"Total supply: {total_supply()} / 3.333")
            except Exception as e:
                print(f"{R}[!] Gagal baca on-chain: {e}{RESET}")
        elif pil == "2":
            if balance_of(wallet) >= 1:
                print(f"{Y}[!] Kamu sudah pegang NFT ini (1 per wallet).{RESET}")
                continue
            prev = baw_preview(wallet)
            req_id = prev.get("requestId") or prev.get("request_id")
            if not req_id:
                print(f"{R}[!] Preview gagal / tidak ada requestId — cek output di atas. "
                      f"Jangan lanjut kalau simulasi revert.{RESET}")
                continue
            print(f"{G}[+] Preview OK, requestId: {req_id}{RESET}")
            ok = input("Eksekusi mint sekarang? (y/N) » ").strip().lower()
            if ok != "y":
                print("Dibatalkan, tidak ada tx terkirim.")
                continue
            ex = baw_execute(req_id)
            print(f"{G}[+] Selesai. Cek tx di BscScan, lalu cek saldo (menu 1).{RESET}")
            _ = ex
        elif pil == "3":
            print("Keluar.")
            break
        else:
            print(f"{Y}[!] Pilih 1/2/3.{RESET}")


if __name__ == "__main__":
    main()
