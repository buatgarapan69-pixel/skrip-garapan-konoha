#!/usr/bin/env python3
"""TZERO ($T0) — beli misi di bonding curve (Base Sepolia testnet).

PAKAI WALLET BURNER (baru, tanpa dana nyata). Private key HANYA lewat
environment variable, TIDAK PERNAH ditulis di skrip ini:
    export TZERO_PRIVATE_KEY="0x..."
    pip install web3
    python3 tzero_buy.py 0xTOKEN_MISI 0.01

Artinya: beli 0,01 test ETH di misi itu. Hold minimal 60 menit:
  - Fuel: 1.000 pts per 1 ETH yang dibeli + hold 60 mnt (0,01 ETH = 10 pts)
  - Crew: +150 pts kalau misi itu LIFTOFF selagi kamu masih hold (>=0,01 ETH)

Syarat: wallet harus sudah punya test ETH Base Sepolia (faucet gratis,
lihat README.md). JANGAN pakai wallet berisi dana nyata.

Kontrak (Base Sepolia, chain 84532, terverifikasi di Basescan):
  Launchpad 0xbce48917C41BB45Ad15f859E4Bf0e4EEa74bAd5c
  buy(address token, uint256 minTokensOut) payable, fee 1%.
"""
import os
import sys

from web3 import Web3

RPC = "https://sepolia.base.org"
LAUNCHPAD = "0xbce48917C41BB45Ad15f859E4Bf0e4EEa74bAd5c"
CHAIN_ID = 84532

ABI = [
    {"inputs": [{"name": "token", "type": "address"},
                {"name": "nativeIn", "type": "uint256"}],
     "name": "quoteBuy", "outputs": [{"name": "", "type": "uint256"},
                                      {"name": "", "type": "uint256"},
                                      {"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "token", "type": "address"},
                {"name": "minTokensOut", "type": "uint256"}],
     "name": "buy", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "payable", "type": "function"},
]


def main():
    if len(sys.argv) < 3:
        print("Pakai: python3 tzero_buy.py 0xTOKEN_MISI JUMLAH_ETH")
        print("Contoh: python3 tzero_buy.py 0x9Fcc4eA9C188B15452031e8f1b44fd5E8B7049CF 0.01")
        return
    token = Web3.to_checksum_address(sys.argv[1])
    amount_eth = float(sys.argv[2])
    pk = os.environ.get("TZERO_PRIVATE_KEY", "")
    if not pk:
        print("Set dulu: export TZERO_PRIVATE_KEY=\"0x...\" (wallet burner!)")
        return
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
    assert w3.is_connected() and w3.eth.chain_id == CHAIN_ID
    acct = w3.eth.account.from_key(pk)
    print("Wallet:", acct.address)
    bal = w3.eth.get_balance(acct.address)
    print("Saldo test ETH:", Web3.from_wei(bal, "ether"))
    value = Web3.to_wei(amount_eth, "ether")
    if bal < value:
        print("Saldo kurang. Ambil test ETH dulu dari faucet (lihat README.md).")
        return
    lp = w3.eth.contract(address=Web3.to_checksum_address(LAUNCHPAD), abi=ABI)
    quoted = lp.functions.quoteBuy(token, value).call()[0]
    min_out = quoted * 99 // 100  # slippage 1%
    print(f"Quote: {amount_eth} ETH -> ~{Web3.from_wei(quoted, 'ether')} token "
          f"(min {Web3.from_wei(min_out, 'ether')} setelah slippage 1%)")
    tx = lp.functions.buy(token, min_out).build_transaction({
        "from": acct.address,
        "value": value,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 500000,
        "maxFeePerGas": w3.eth.gas_price * 2,
        "maxPriorityFeePerGas": Web3.to_wei(0.01, "gwei"),
        "chainId": CHAIN_ID,
    })
    signed = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("Tx terkirim:", tx_hash.hex())
    print("Tunggu receipt...")
    rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    print("Status:", "SUKSES" if rcpt.status == 1 else "GAGAL",
          "| block:", rcpt.blockNumber)
    print("JANGAN JUAL dulu — hold minimal 60 menit biar poin Fuel/Crew masuk.")


if __name__ == "__main__":
    main()
