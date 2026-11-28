# POEMIJJ — Mining USDT Gratis (Tugas Toko Harian)

Bot: **@poemijjbot** ("Breguet-Mall", Mini App di niuke6ed.com)

## Cara daftar (gratis)

1. Buka bot: https://t.me/poemijjbot
2. Tap **💰💰💰Start Now**, buka Mini App
3. Ambil tugas harian gratis, tap selesaikan

## Cara earn

- **1 tugas gratis/hari (VIP0) = $1 USDT** — ambil tugas lalu selesaikan, komisi masuk saldo.
- **Referral**: komisi **10%/3%/1% dari DEPOSIT teman** (bukan dari tugas gratis teman).
  - Link ref kamu: `https://t.me/poemijjbot?start=invite_code_<KODE_KAMU>` (kode 6 huruf, lihat menu Invite)
- **VIP berbayar (opsional, JANGAN dulu)**: VIP1 $9 = $5/hari, VIP2 $33 = $23/hari, VIP3 $99 = $75/hari, dst sampai VIP9 $18.888.

## Min WD & syarat (jujur)

- **Min WD: 5 USDT** via TRC20 / BEP20-USDT / BEP20-USDC / ETH-USDT / Polygon, **fee WD 14%** (dari $5 terima $4,30).
- **Grind gratis ±5 hari** baru sampai min WD.
- **Payout BELUM TERBUKTI** (belum ada WD yang landing saat skrip ini ditulis, 28 Nov 2026).
- **JANGAN deposit / beli VIP** sebelum ada bukti ada orang yang WD-nya landing. Ini skema VIP-deposit (Breguet-Mall clone).
- Server kadang timeout — kalau gagal, coba lagi beberapa menit kemudian.

## Skrip otomatis (1 akun)

`poemijj_umum.py` — login Mini App + ambil + selesaikan tugas harian gratis, sekali jalan.

```bash
pip install telethon requests
python3 poemijj_umum.py
```

Isi dulu di dalam skrip:
- `API_ID` & `API_HASH` dari https://my.telegram.org (akun Telegram kamu sendiri)
- `SESSION_NAME` = nama file session Telethon kamu

**Peringatan:** jangan pakai banyak akun dari 1 IP — pakai 1 akun = 1 IP, atau proxy residensial beda per akun. Skrip ini untuk 1 akun saja.

## Status

- Probe 28 Nov 2026: bot hidup, Mini App + API jalan. Naruto: tugas gratis selesai, saldo komisi $1,00.
- Fleet 29/29 daftar pakai ref Naruto, masing-masing saldo $1,00, referral Naruto 29 valid.
- Dipantau: WD pertama ±3 Des 2026 (setelah 5 hari klaim).
