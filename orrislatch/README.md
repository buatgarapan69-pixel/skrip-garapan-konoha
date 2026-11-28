# OrrisLatch Key — Free Mint NFT (Agent ID)

Free mint NFT Key (OSLTK, ERC-721) di BNB Chain. Key dipakai klaim isi laci
(drawer) tiap ronde. Mint GRATIS (value 0 BNB, cuma gas).

**Status 28 Nov 2026:** mint TERBUKTI on-chain — Key #191, gas 0,0000072 BNB.
Nilai Key/OSLT **BELUM TERBUKTI** (belum ada pasar/harga). Klaim laci BERBAYAR
0,00025–0,0005 BNB dan belum dicoba (butuh gas).

## Info

- Situs: https://orrislatch-cabinet.pages.dev
- Kontrak Key (OSLTK): `0x84353B021713f0AEe1819C82c2De7c5aE5170579`
- Maks supply: 3.333 Key — sudah termint 196 saat mint (28 Nov 2026)
- Bukti mint (BscScan): https://bscscan.com/tx/0xa539b071ea039c1ec097053340f0478e14db0dad5fdcd34fb05e4ab7a40f3e50
- Sumber lead: Telegram @airdrop_newgarapan, 28 Nov 2026

## Cara mint (manual)

1. Buka https://orrislatch-cabinet.pages.dev
2. Connect wallet EVM yang memegang Agent ID (mis. hatake.ai)
3. Mint Key — gratis (0 BNB, cuma gas)
4. Simpan Key di wallet yang sama untuk klaim laci tiap ronde

## Cara mint (skrip)

```bash
pip install web3
PRIVATE_KEY=0x... RPC_URL=https://bsc-dataseed.binance.org python3 mint_key.py
```

Skrip memanggil `mintFree()` di kontrak Key (value 0). Cek dulu saldo BNB
cukup buat gas (±0,00001 BNB). **JANGAN PERNAH** kirim private key / seed
phrase ke siapa pun — skrip ini hanya membacanya dari environment variable
lokal dan tidak pernah mengirimnya ke mana pun.

## Isi laci (drawer) per ronde

| Bentuk | Isi |
|---|---|
| Oak Slip | 2.500 OSLT |
| Brass Edge | 12.500 OSLT |
| Rosewood Case | 60.000 OSLT |
| Ivory Inlay | 250.000 OSLT |

- Ronde tutup tiap tengah malam UTC; klaim tutup 18:00 UTC di hari seal.
- Klaim butuh Key di wallet yang sama + fee 0,00025 BNB (standar) /
  0,0005 BNB (rare).
- Kartu drawer 2–5 (bukan Key) berbayar 0,0002 BNB, slot 6–10 0,0004 BNB.

## Aturan main

- Gratis saja. Jangan top-up / deposit buat garapan ini.
- DYOR: OSLT belum ada pasar — Key bisa saja tidak pernah bernilai uang.
- 1 orang 1 akun. Jangan multi-akun buat referral sendiri.
