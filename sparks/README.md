# First-Dollar Sparks (SPARKS)

Free mint NFT di BNB Smart Chain — tiap mint langsung dapat **+10.000 SPARK** di transaksi yang sama.

## Cara pakai (Termux / Linux)

```bash
python3 sparks.py
```

Pilih menu di dalam skrip (1 perintah saja):

- `[1]` Cek status (saldo NFT + SPARK + total supply)
- `[2]` Mint 1 NFT gratis (preview dulu, baru eksekusi)
- `[3]` Keluar

Tidak perlu install apa-apa (hanya Python stdlib). Tanpa proxy, tanpa API key.

## Syarat

- Wallet BSC yang pegang **Binance Agent ID** (SPACE ID)
- Sedikit BNB buat gas (mint kami: ~0,0000111 BNB)
- CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu — skrip memanggil `baw contract-call preview` lalu `execute`, jadi **tidak ada private key di skrip ini**

## Yang didapat

- 1 NFT SPARKS per mint (max 10 per wallet, supply 10.000)
- +10.000 SPARK langsung di tx mint yang sama
- Window mint s.d. **3 Des 2026**

## Peringatan jujur

- **Nilai NFT + SPARK BELUM TERBUKTI** — belum ada pool/market. Bukan janji cuan.
- Bukti mint kami (28 Nov 2026): token **#1868**, tx `0xfc10823f…aecc9f`, gas 0,0000111316 BNB, saldo SPARK masuk 10.000 di tx yang sama.

## Sumber

- Mint: https://first-dollar-sparks.pages.dev
- Kontrak NFT: `0xd52FD117c4b47d03E4e16E778871F09FAA5a024B`
- Token SPARK: `0xA798097646601145408465a7b1aC524913A7AD23`
