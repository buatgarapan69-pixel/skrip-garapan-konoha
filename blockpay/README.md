# Blockpay Genesis (BPAYG)

Free mint NFT di BNB Smart Chain — 3.333 Digital Guardian NFT, **1.111 jatah gratis** (1 per wallet, cuma gas).

## Cara pakai (Termux / Linux)

```bash
python3 blockpay.py
```

Pilih menu di dalam skrip (1 perintah saja):

- `[1]` Cek status (saldo NFT + free terpakai + total supply)
- `[2]` Free mint 1 NFT (preview dulu, baru eksekusi)
- `[3]` Keluar

Tidak perlu install apa-apa (hanya Python stdlib). Tanpa proxy, tanpa API key.

## Syarat

- Wallet BSC apa saja (tanpa syarat Agent ID)
- Sedikit BNB buat gas (mint kami: ~0,0000088 BNB)
- CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu — skrip memanggil `baw contract-call preview` lalu `execute`, jadi **tidak ada private key di skrip ini**

## Yang didapat

- 1 Guardian NFT gratis per wallet (max 20 total free+paid)
- Free mint s.d. **30 Nov 2026**, listing Element mulai **2 Des 2026**

## Peringatan jujur

- **Nilai NFT BELUM TERBUKTI** — belum ada pasar. Bukan janji cuan.
- Bukti mint kami (28 Nov 2026): token **#298**, tx `0x276be3c1…13486`, gas 0,0000087698 BNB, freeMinted 298/1.111 saat itu.

## Sumber

- Mint: https://blockpay.world
- Kontrak: `0x0BF3Cf8eEeC4fE71305738c75aA9574A24DDf57b`
- Event: https://nftcalendar.io/event/blockpay-genesis/
