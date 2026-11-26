# TZERO ($T0) — Pre-flight Points Season 0 (Testnet Base Sepolia)

TZERO adalah token launchpad untuk Zero, chain Layer-1 dari LayerZero.
Season 0 jalan di testnet Base Sepolia. **11% supply $T0** dicadangkan
buat Pre-flight Points: **5% Season 0** + 6% mainnet seasons. Min **500
pts** buat eligible, cap 0,1% supply per wallet. Snapshot TBA (diumumkan
7 hari sebelumnya).

## Cara earn poin

| Cara | Poin | Syarat |
|---|---|---|
| Fuel | 1.000 / 1 ETH | Beli misi, hold 60 mnt (min beli 0,0005 ETH, maks 1 ETH/hari) |
| Crew | 150 / misi (maks 5/hari) | Back misi ≥0,01 ETH yang liftoff selagi masih hold |
| Liftoff | 500 | Misi buatanmu liftoff dengan ≥5 backer lain |
| Staking | bagi 5.000/hari | Stake test $T0 (maks 1.000/hari/wallet) |
| Signal | 200 + 100 | Reply/quote post Season 0 di X + follow @T0dotfun |

## Langkah

1. **Test ETH gratis** — tombol "Get test ETH" di
   https://testnet.tzer0.fun/ menunjuk 3 faucet: Coinbase (butuh
   sign-in Coinbase), Superchain (verifikasi GitHub / on-chain identity),
   Alchemy (butuh 0,001 ETH di Ethereum mainnet — HOLD, bukan dibayar).
   Faucet lain (Chainlink, QuickNode) butuh verifikasi captcha.
   ⚠️ Semua faucet butuh login/captcha — tidak ada yang sekali klik.
2. **Cek poin:** `python3 tzero_points.py 0xALAMAT_WALLET_KAMU`
3. **Beli misi:** `export TZERO_PRIVATE_KEY="0x..."` (wallet **burner**,
   tanpa dana nyata!) lalu `python3 tzero_buy.py 0xTOKEN_MISI 0.01`
   — hold minimal 60 menit, jangan jual dulu.
4. **Signal (manual, di HP):** reply/quote post Season 0 di X pakai kode
   wallet kamu (muncul di dashboard Points setelah connect wallet),
   lalu link X di dashboard dengan sign message (+200), follow
   @T0dotfun (+100).

## Cara pakai skrip

```bash
pip install web3   # cuma buat tzero_buy.py; tzero_points.py stdlib saja
python3 tzero_points.py 0xALAMAT_WALLET_KAMU
```

## Catatan jujur

- **Token $T0 belum ada**, tim anonim, tanpa tanggal snapshot/claim.
  Poin masih provisional sampai snapshot final.
- Anti-sybil: review publik sebelum snapshot menghapus farm cluster
  (wallet yang didanai dari sumber sama + pola scripted).
  **1 orang 1 wallet — jangan multi-akun.**
- Misi liftoff setelah ~0,28 ETH net buys. Fee beli/jual 1% (test ETH).
- Status 27 Nov 2026: 16.797 wallet sudah ranking, 14.204 misi live.
  Akun utama Tim Konoha masih 0 pts karena faucet belum dapat test ETH
  (semua faucet butuh login/captcha) — progres lanjut begitu test ETH
  didapat.
