#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIJIN — Free Mint NFT + Klaim 280 KIJIN (BNB Smart Chain)
15.000 NFT (5 tingkat), free zone 5.000 pertama (1 per pemegang Agent ID).
Tiap NFT bisa klaim 280 KIJIN (1x per NFT, deadline klaim 3 Des 2026).

Cara pakai (1 perintah saja):
    python3 kijin.py
Lalu pilih menu di dalam skrip.

Yang kamu butuhkan:
  - Wallet BSC yang pegang Binance Agent ID (SPACE ID)
  - Sedikit BNB buat gas (mint kami: ~0,0000102 BNB; klaim: ~0,0000087 BNB)
  - CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu
    (perintah yang dipakai: `baw contract-call preview` + `execute`)

Fungsi yang dipakai (terverifikasi dari tx on-chain):
  - mintFree()       -> 0x8ab53447 | value 0 | gas ~154.000
  - claim(uint256)   -> 0x379607f5 + tokenId | value 0 | gas ~128.000
  - Kontrak NFT      -> 0x625188954784d2f8c542fe8206050ff540ae3b20
  - Kontrak klaim    -> 0x94534656FC286e86C6a04a1fC19724E4da6264Ed
  - Token KIJIN      -> 0xaD758224f7674976CBcE6b9bd7BA7358503a7599

TIDAK ADA private key / seed phrase / session di skrip ini.
Isi alamat wallet kamu sendiri saat skrip bertanya.
"""
import json
import subprocess
import sys
import urllib.request

RPC = "https://bsc-dataseed.binance.org"
NFT = "0x625188954784d2f8c542fe8206050ff540ae3b20"
CLAIM_CONTRACT = "0x94534656FC286e86C6a04a1fC19724E4da6264Ed"
KIJIN_TOKEN = "0xaD758224f7674976CBcE6b9bd7BA7358503a7599"
CALLDATA_MINT_FREE = "0x8ab53447"  # mintFree()
GAS_MINT = "220000"
GAS_CLAIM = "200000"
SITE = "https://kijin.fcfs.workers.dev"

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


def balance_of(contract, wallet):
    data = "0x70a08231" + "00" * 12 + wallet[2:].lower()
    return rpc_call(contract, data)


def total_minted():
    return rpc_call(NFT, "0xa2309ff8")  # totalMinted()


def free_remaining():
    return rpc_call(NFT, "0x5a781a6b")  # freeRemaining()


def is_claimed(token_id):
    data = "0x9e34070f" + format(token_id, "064x")
    return rpc_call(CLAIM_CONTRACT, data)


def claim_calldata(token_id):
    return "0x379607f5" + format(token_id, "064x")  # claim(uint256)


def baw_flow(wallet, to_addr, calldata, gas_limit, label):
    cmd = ["baw", "contract-call", "preview",
           "--binanceChainId", "56", "--from", wallet,
           "--to", to_addr, "--value", "0",
           "--inputData", calldata, "--gasLimit", gas_limit, "--json"]
    print(f"{C}[*] Preview {label} (simulasi dulu, belum ada tx)...{RESET}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(r.stdout[:1000])
    if r.stderr:
        print(f"{Y}[!] {r.stderr[:300]}{RESET}")
    try:
        prev = json.loads(r.stdout)
    except Exception:
        print(f"{R}[!] Preview gagal diparse — jangan lanjut.{RESET}")
        return
    req_id = prev.get("requestId") or prev.get("request_id")
    if not req_id:
        print(f"{R}[!] Preview gagal / tidak ada requestId — cek output di atas.{RESET}")
        return
    print(f"{G}[+] Preview OK, requestId: {req_id}{RESET}")
    ok = input(f"Eksekusi {label} sekarang? (y/N) » ").strip().lower()
    if ok != "y":
        print("Dibatalkan, tidak ada tx terkirim.")
        return
    r2 = subprocess.run(["baw", "contract-call", "execute",
                         "--requestId", req_id, "--json"],
                        capture_output=True, text=True, timeout=180)
    print(r2.stdout[:1000])
    if r2.stderr:
        print(f"{Y}[!] {r2.stderr[:300]}{RESET}")
    print(f"{G}[+] Selesai. Cek tx di BscScan, lalu cek status (menu 1).{RESET}")


def menu():
    print(f"\n{R}👹 KIJIN — Free Mint NFT + Klaim 280 KIJIN{RESET}")
    print(f"{C}Kontrak NFT: {NFT}{RESET}")
    print(f"{C}Situs:       {SITE}{RESET}")
    print(f"{W}[1]{RESET} Cek status (NFT + KIJIN + free tersisa)")
    print(f"{W}[2]{RESET} Free mint 1 NFT (preview dulu, baru eksekusi)")
    print(f"{W}[3]{RESET} Klaim 280 KIJIN dari NFT kamu (per tokenId)")
    print(f"{W}[4]{RESET} Keluar")
    return input("➤ PILIH MENU » ").strip()


def main():
    print(f"{G}Mint + klaim gratis, cuma gas. Nilai KIJIN BELUM TERBUKTI — belum ada pool.{RESET}")
    wallet = input("Alamat wallet BSC kamu (0x...) » ").strip()
    if not (wallet.startswith("0x") and len(wallet) == 42):
        print(f"{R}[!] Alamat wallet tidak valid.{RESET}")
        sys.exit(1)
    while True:
        pil = menu()
        if pil == "1":
            try:
                print(f"NFT KIJIN kamu: {balance_of(NFT, wallet)}")
                print(f"Saldo KIJIN kamu: {balance_of(KIJIN_TOKEN, wallet) / 10**18:,.0f}")
                print(f"Total ter-mint: {total_minted()} / 15.000")
                print(f"Free tersisa: {free_remaining()} (free zone 5.000 pertama)")
            except Exception as e:
                print(f"{R}[!] Gagal baca on-chain: {e}{RESET}")
        elif pil == "2":
            if free_remaining() <= 0:
                print(f"{Y}[!] Free zone HABIS — mint berbayar 0,0003 BNB (tidak ditangani skrip ini).{RESET}")
                continue
            baw_flow(wallet, NFT, CALLDATA_MINT_FREE, GAS_MINT, "free mint")
        elif pil == "3":
            try:
                token_id = int(input("TokenId NFT KIJIN kamu » ").strip())
            except ValueError:
                print(f"{R}[!] TokenId harus angka.{RESET}")
                continue
            if is_claimed(token_id):
                print(f"{Y}[!] Token #{token_id} SUDAH diklaim (1x per NFT).{RESET}")
                continue
            baw_flow(wallet, CLAIM_CONTRACT, claim_calldata(token_id),
                     GAS_CLAIM, f"klaim 280 KIJIN (token #{token_id})")
        elif pil == "4":
            print("Keluar.")
            break
        else:
            print(f"{Y}[!] Pilih 1/2/3/4.{RESET}")


if __name__ == "__main__":
    main()
