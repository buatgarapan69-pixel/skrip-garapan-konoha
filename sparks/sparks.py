#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIRST-DOLLAR SPARKS — Free Mint NFT (BNB Smart Chain)
Mint 1 NFT gratis (cuma gas) + langsung dapat 10.000 SPARK di tx yang sama.

Cara pakai (1 perintah saja):
    python3 sparks.py
Lalu pilih menu di dalam skrip.

Yang kamu butuhkan:
  - Wallet BSC yang pegang Binance Agent ID (SPACE ID)
  - Sedikit BNB buat gas (mint kami: ~0,0000111 BNB)
  - CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu
    (https://www.binance.com — Agentic Wallet; perintah yang dipakai di sini:
    `baw contract-call preview` lalu `baw contract-call execute`)

Fungsi yang dipakai (terverifikasi dari tx on-chain):
  - mint(uint256)  -> 0xa0712d68 + jumlah (1) | value 0 | gas ~180.000
  - Kontrak NFT    -> 0xd52FD117c4b47d03E4e16E778871F09FAA5a024B
  - Token SPARK    -> 0xA798097646601145408465a7b1aC524913A7AD23

TIDAK ADA private key / seed phrase / session di skrip ini.
Isi alamat wallet kamu sendiri saat skrip bertanya.
"""
import json
import subprocess
import sys
import urllib.request

RPC = "https://bsc-dataseed.binance.org"
CONTRACT = "0xd52FD117c4b47d03E4e16E778871F09FAA5a024B"
SPARK_TOKEN = "0xA798097646601145408465a7b1aC524913A7AD23"
CALLDATA_MINT1 = "0xa0712d68" + "00" * 31 + "01"  # mint(uint256) dengan jumlah 1
GAS_LIMIT = "250000"
SITE = "https://first-dollar-sparks.pages.dev"

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
RESET = "\033[0m"


def rpc_call(to_addr, data):
    """eth_call read-only via RPC publik (stdlib saja)."""
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


def balance_of(contract, wallet):
    data = "0x70a08231" + "00" * 12 + wallet[2:].lower()
    return rpc_call(contract, data)


def total_supply(contract):
    return rpc_call(contract, "0x18160ddd")


def baw_preview(wallet):
    cmd = ["baw", "contract-call", "preview",
           "--binanceChainId", "56", "--from", wallet,
           "--to", CONTRACT, "--value", "0",
           "--inputData", CALLDATA_MINT1, "--gasLimit", GAS_LIMIT, "--json"]
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
    print(f"\n{R}⚡ FIRST-DOLLAR SPARKS — Free Mint NFT + 10.000 SPARK{RESET}")
    print(f"{C}Kontrak: {CONTRACT}{RESET}")
    print(f"{C}Situs:   {SITE}{RESET}")
    print(f"{W}[1]{RESET} Cek status (saldo NFT + SPARK + total supply)")
    print(f"{W}[2]{RESET} Mint 1 NFT gratis (preview dulu, baru eksekusi)")
    print(f"{W}[3]{RESET} Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    print(f"{G}Mint gratis, cuma gas. Nilai NFT + SPARK BELUM TERBUKTI — belum ada pool.{RESET}")
    wallet = input("Alamat wallet BSC kamu (0x...) » ").strip()
    if not (wallet.startswith("0x") and len(wallet) == 42):
        print(f"{R}[!] Alamat wallet tidak valid.{RESET}")
        sys.exit(1)
    while True:
        pil = menu()
        if pil == "1":
            try:
                print(f"NFT kamu: {balance_of(CONTRACT, wallet)}")
                print(f"Total supply: {total_supply(CONTRACT)} / 10.000")
                print(f"SPARK kamu: {balance_of(SPARK_TOKEN, wallet) / 10**18:,.0f}")
            except Exception as e:
                print(f"{R}[!] Gagal baca on-chain: {e}{RESET}")
        elif pil == "2":
            if balance_of(CONTRACT, wallet) >= 10:
                print(f"{Y}[!] Kamu sudah pegang 10 NFT (max per wallet).{RESET}")
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
            print(f"{G}[+] Selesai. Cek tx di BscScan, lalu cek saldo NFT + SPARK (menu 1).{RESET}")
            _ = ex
        elif pil == "3":
            print("Keluar.")
            break
        else:
            print(f"{Y}[!] Pilih 1/2/3.{RESET}")


if __name__ == "__main__":
    main()
