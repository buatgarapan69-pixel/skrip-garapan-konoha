# KIJIN (鬼神)

Free mint NFT di BNB Smart Chain — 15.000 NFT (5 tingkat), free zone 5.000 pertama (1 per pemegang Agent ID). **Tiap NFT bisa klaim 280 KIJIN** (1x per NFT, deadline klaim **3 Des 2026**).

## Cara pakai (Termux / Linux)

```bash
python3 kijin.py
```

Pilih menu di dalam skrip (1 perintah saja):

- `[1]` Cek status (NFT + saldo KIJIN + free tersisa)
- `[2]` Free mint 1 NFT (preview dulu, baru eksekusi)
- `[3]` Klaim 280 KIJIN dari NFT kamu (isi tokenId)
- `[4]` Keluar

Tidak perlu install apa-apa (hanya Python stdlib). Tanpa proxy, tanpa API key.

## Syarat

- Wallet BSC yang pegang **Binance Agent ID** (SPACE ID)
- Sedikit BNB buat gas (mint kami: ~0,0000102 BNB; klaim: ~0,0000087 BNB)
- CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu — skrip memanggil `baw contract-call preview` lalu `execute`, jadi **tidak ada private key di skrip ini**

## Yang didapat

- 1 NFT KIJIN gratis (free zone sisa 2.056 saat kami mint)
- Klaim **280 KIJIN per NFT** — kami SUDAH klaim dan terverifikasi masuk saldo (280 KIJIN)
- Market resmi di situs (mode托管/escrow, ada harga minimum per tingkat)

## Peringatan jujur

- **Nilai KIJIN BELUM TERBUKTI** — belum ada pool/market likuid. Klaim tokennya nyata, harganya belum.
- Bukti mint kami (28 Nov 2026): token **#2944**, tx `0xf9620ee5…034034`, gas 0,0000101798 BNB.
- Bukti klaim kami: tx `0x224b0121…28ce0ff`, saldo KIJIN 280.

## Sumber

- Mint + klaim + market: https://kijin.fcfs.workers.dev
- Kontrak NFT: `0x625188954784d2f8c542fe8206050ff540ae3b20`
- Kontrak klaim: `0x94534656FC286e86C6a04a1fC19724E4da6264Ed`
- Token KIJIN: `0xaD758224f7674976CBcE6b9bd7BA7358503a7599`
