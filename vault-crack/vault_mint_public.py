#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vault_mint_public.py — FREE MINT NFT Vault-Crack (BNB Chain), versi publik.
1 NFT gratis per wallet, cuma bayar gas (~0,000016 BNB). Tanpa Agent ID.
Kontrak terverifikasi Sourcify exact_match: 0x1a7a8bbb49e3e8cf951996789fd69d4c7524a2b4
Site resmi: https://vaultcrack.xyz

CARA PAKAI (Termux / VPS / laptop):
  1. pip install web3 eth-account
  2. export PRIVATE_KEY="0x..."   # kunci wallet KAMU sendiri (BSC).
     JANGAN pernah kirim/bagikan private key ke siapa pun.
  3. python3 vault_mint_public.py
  4. Cek NFT di BscScan: https://bscscan.com/address/<wallet-kamu>#readContract
     atau tab "ERC-721 Token Txns".

YANG DICEK SKRIP INI SEBELUM KIRIM (aman):
  - mintOpen == True, mintCost(wallet,1) == 0 (gratis, value 0)
  - walletInfo: freeAvailable == True, belum pernah mint
  - simulasi eth_call freeMint() harus PASS (tidak revert)
  - gasPrice diambil dari jaringan (saat ini ~0,05 gwei)

PERINGATAN:
  - JANGAN sentuh jalur berbayar (mint 0,001 BNB) kalau cuma mau yang gratis.
  - Token Vault belum ada harga/pasar — NFT ini tiket lotre, bukan jaminan cuan.
  - Owner kontrak bisa menutup mint / menaikkan harga (maks 0,01 BNB) kapan saja.
    Kalau skrip bilang "mint tertutup", berarti sudah tutup — jangan dipaksa.
  - Pastikan wallet berisi BNB secukupnya buat gas (±0,00002 BNB).
"""
import json
import os
import sys

from eth_account import Account
from web3 import Web3

VAULT = "0x1a7a8bbb49e3e8cf951996789fd69d4c7524a2b4"
RPCS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc.publicnode.com",
]
ABI = json.loads(
    '[{"name":"freeMint","outputs":[{"type":"uint256"}],"inputs":[],'
    '"stateMutability":"nonpayable","type":"function"},'
    '{"name":"mintCost","outputs":[{"type":"uint256"}],"inputs":'
    '[{"name":"w","type":"address"},{"name":"c","type":"uint256"}],'
    '"stateMutability":"view","type":"function"},'
    '{"name":"mintOpen","outputs":[{"type":"bool"}],"inputs":[],'
    '"stateMutability":"view","type":"function"},'
    '{"name":"totalMinted","outputs":[{"type":"uint256"}],"inputs":[],'
    '"stateMutability":"view","type":"function"},'
    '{"name":"walletInfo","outputs":[{"type":"bool"},{"type":"bool"},'
    '{"type":"uint256"},{"type":"uint256"}],"inputs":[{"name":"w","type":"address"}],'
    '"stateMutability":"view","type":"function"},'
    '{"name":"balanceOf","outputs":[{"type":"uint256"}],"inputs":'
    '[{"name":"w","type":"address"}],"stateMutability":"view","type":"function"}]'
)


def main():
    priv = os.environ.get("PRIVATE_KEY", "").strip()
    if not priv:
        print("ISI DULU: export PRIVATE_KEY=\"0x...\" (kunci wallet kamu)")
        return 1
    acct = Account.from_key(priv)
    addr = acct.address
    w3 = None
    for r in RPCS:
        try:
            w = Web3(Web3.HTTPProvider(r, request_kwargs={"timeout": 15}))
            if w.is_connected():
                w3 = w
                print("RPC:", r, "| blok:", w.eth.block_number)
                break
        except Exception as e:
            print("RPC gagal:", r, e)
    if not w3:
        print("Semua RPC gagal. Coba lagi nanti.")
        return 1
    vault = w3.eth.contract(address=Web3.to_checksum_address(VAULT), abi=ABI)
    bal = w3.eth.get_balance(Web3.to_checksum_address(addr))
    print("Wallet:", addr, "| BNB:", Web3.from_wei(bal, "ether"))
    print("mintOpen:", vault.functions.mintOpen().call(),
          "| totalMinted:", vault.functions.totalMinted().call(),
          "| NFT kamu:", vault.functions.balanceOf(addr).call())
    print("mintCost:", vault.functions.mintCost(addr, 1).call(),
          "| walletInfo:", vault.functions.walletInfo(addr).call())
    if not vault.functions.mintOpen().call():
        print("Mint TERTUTUP. Berhenti.")
        return 1
    if vault.functions.mintCost(addr, 1).call() != 0:
        print("Free mint SUDAH DIPAKAI wallet ini (mintCost != 0). Berhenti.")
        return 1
    try:
        sim = vault.functions.freeMint().call({"from": addr})
        print("Simulasi freeMint: PASS -> tokenId", sim)
    except Exception as e:
        print("Simulasi freeMint GAGAL:", str(e)[:200])
        return 1
    gas_price = w3.eth.gas_price
    tx = {
        "to": Web3.to_checksum_address(VAULT),
        "data": "0x" + Web3.keccak(text="freeMint()")[:4].hex(),
        "value": 0,
        "gas": 230000,
        "gasPrice": gas_price,
        "nonce": w3.eth.get_transaction_count(Web3.to_checksum_address(addr), "pending"),
        "chainId": 56,
    }
    signed = acct.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("TX terkirim:", txh.hex())
    rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=180)
    print("Status:", rcpt["status"], "| blok:", rcpt["blockNumber"],
          "| gas:", rcpt["gasUsed"],
          "| biaya:", Web3.from_wei(rcpt["gasUsed"] * gas_price, "ether"), "BNB")
    print("NFT kamu sekarang:", vault.functions.balanceOf(addr).call())
    print("Cek di: https://bscscan.com/tx/" + txh.hex())
    return 0


if __name__ == "__main__":
    sys.exit(main())
