# TRADORA — Mining USDT Gratis + Spin Harian

Bot: **@TradoraTopbot** (Mini App TA Miner)

## Cara daftar (gratis)

1. Buka bot: https://t.me/TradoraTopbot
2. Tap **🚀 Launch TA Miner**
3. Dapat **100 TA gratis**, mining jalan otomatis

## Cara earn

- **Mining harian** dari saldo TA: 100 TA = $0,02/hari (makin banyak TA, makin besar)
- **Check-in harian**: hari 1 +2 TA, hari 2 +0,001 USDT, hari 3+ +1 TA
- **Spin harian 3x**: hadiah USDT/TA (spin 1: 0,01 USDT, spin 2: 10 TA)
- **Referral**: +3 TA tiap teman + 10% komisi dari pembelian tim
  - Link ref kamu: `https://t.me/TradoraTopbot?start=ref_<ID_TELEGRAM_KAMU>`

## Min WD & syarat (jujur)

- **Min WD: 0,1 USDT** via BSC (BEP20) — paling rendah. Arbitrum/Polygon 1 USDT, Base 0,5 USDT, Tron 10 USDT.
- **WD mode MANUAL** (bukan instan) — diproses admin.
- **Grind gratis ±4-5 hari** baru sampai min WD.
- **Payout BELUM TERBUKTI** (belum ada WD yang landing saat skrip ini ditulis, 28 Nov 2026).
- **Server Mini App kadang down** (error 500/502) — kalau gagal, coba lagi beberapa menit kemudian.
- **Beli TA minimal 200 TA = $2 USDT** — jangan deposit sebelum ada bukti WD landing.

## Skrip otomatis (1 akun)

`tradora_umum.py` — check-in + spin 3x + claim, sekali jalan.

```bash
pip install telethon
python3 tradora_umum.py
```

Isi dulu di dalam skrip:
- `API_ID` & `API_HASH` dari https://my.telegram.org (akun Telegram kamu sendiri)
- `SESSION_NAME` = nama file session Telethon kamu

**Peringatan:** jangan pakai banyak akun dari 1 IP — server mendeteksi multi-akun
(akun kena flag = tombol claim disembunyikan). 1 akun = 1 IP. Skrip ini untuk 1 akun saja.

## Status

- Probe 28 Nov 2026: bot hidup, API jalan. Naruto: 113 TA + 0,010256 USDT
  (check-in +2 TA, spin 0,01 USDT + 10 TA + 1 TA, claim 0,000256 USDT).
- Fleet TIDAK dijalankan (server deteksi multi-akun, proxy mati).
- Dipantau: WD ±3 Des 2026.
