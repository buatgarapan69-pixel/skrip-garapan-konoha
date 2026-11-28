#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mint OrrisLatch Key gratis (value 0, cuma gas) via contract call mintFree().

Syarat: wallet harus memegang Agent ID yang eligible (mis. hatake.ai).
Isi dulu data kamu sendiri lewat environment variable — JANGAN tulis
private key di dalam file ini.

    pip install web3
    PRIVATE_KEY=0x... RPC_URL=https://bsc-dataseed.binance.org python3 mint_key.py
"""
import os
import sys

from web3 import Web3

KEY_CONTRACT = "0x84353B021713f0AEe1819C82c2De7c5aE5170579"
ABI = [
    {"inputs": [], "name": "mintFree", "outputs": [],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "totalMinted", "outputs":
     [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
     "name": "balanceOf", "outputs":
     [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]


def main():
    pk = os.environ.get("PRIVATE_KEY", "")
    rpc = os.environ.get("RPC_URL", "https://bsc-dataseed.binance.org")
    if not pk or pk in ("0x", "0x..."):
        print("Isi PRIVATE_KEY dulu (environment variable).")
        sys.exit(1)
    w3 = Web3(Web3.HTTPProvider(rpc))
    acct = w3.eth.account.from_key(pk)
    key = w3.eth.contract(address=Web3.to_checksum_address(KEY_CONTRACT), abi=ABI)
    print("Wallet:", acct.address)
    print("Balance Key sekarang:", key.functions.balanceOf(acct.address).call())
    print("Total minted:", key.functions.totalMinted().call(), "/ 3333")
    tx = key.functions.mintFree().build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 200000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 56,
    })
    signed = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("Tx terkirim:", tx_hash.hex())
    print("BscScan: https://bscscan.com/tx/" + tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    print("Status:", receipt.status, "| Blok:", receipt.blockNumber,
          "| Gas:", receipt.gasUsed)
    print("Balance Key sesudah:", key.functions.balanceOf(acct.address).call())


if __name__ == "__main__":
    main()
