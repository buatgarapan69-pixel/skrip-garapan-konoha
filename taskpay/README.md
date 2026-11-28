# TASKPAY — 0,05 USDT/Referral, Min WD 0,10 USDT

Bot: **@TaskPayWalletbot** (Mini App "TaskPay Wallet")

## Cara daftar (gratis)

1. Buka bot: https://t.me/TaskPayWalletbot
2. Join 2 channel wajib: @TaskPayWallet dan @TaskWalletPayment, lalu klik **Verify**
3. Buka Mini App, saldo langsung bisa diisi dari iklan + referral

Link referral kamu (setelah daftar, lihat menu Invite di Mini App):
`https://t.me/TaskPayWalletbot/app?startapp=ref_<ID_TELEGRAM_KAMU>`

## Cara earn

- **Referral: 0,05 USDT** per teman — dibayar kalau teman join 2 channel
  **dan selesaikan 5 tugas**. Plus 10% dari deposit teman yang terverifikasi.
- **Iklan interstitial: 0,001 USDT**, maks 10/hari (= 0,01 USDT/hari).
- **Iklan AdsGram: 0,002 USDT**, maks 5/hari — hanya bisa diklaim setelah
  nonton iklan beneran di Mini App (tidak bisa via API).
- **Tugas channel/website** (kalau ada): reward bervariasi, verifikasi otomatis.

## Min WD & syarat (jujur)

- **Min WD: 0,10 USDT** via USDT BEP-20, **maks 2 WD/hari**, tanpa fee WD.
- **Deposit TIDAK wajib** — min deposit $1 hanya kalau mau deposit (jangan).
- **Payout platform TERBUKTI on-chain** (28 Nov 2026): WD 0,10 USDT cair,
  mis. tx `0xf163ddbe…` dan `0x90c1619b…` (cek di channel @TaskWalletPayment).
  WD kamu sendiri tetap harus dibuktikan sebelum percaya penuh.
- **Jujur soal grind:** klaim iklan saja = 0,01 USDT/hari → ±10 hari ke min WD.
  Jalur cepat = referral (2 teman qualified = 0,10 USDT). Tapi kualifikasi
  butuh 5 tugas/teman, dan **daftar tugas sempat kosong** saat probe
  28 Nov 2026 — pantau terus, tugas bisa muncul sewaktu-waktu.

## Skrip otomatis (1 akun)

`taskpay_umum.py` — daftar + verifikasi + klaim interstitial harian (maks 10x),
cek saldo, tugas, dan referral. Sekali jalan.

```bash
pip install telethon requests
python3 taskpay_umum.py
```

Isi dulu di dalam skrip:
- `API_ID` & `API_HASH` dari https://my.telegram.org (akun Telegram kamu sendiri)
- `SESSION_NAME` = nama file session Telethon kamu
- `REF_CODE` = ID Telegram pengundang (opsional, kosongkan kalau tanpa referral)

**Peringatan:** server memblokir device ganda (fingerprint SHA-256). Jangan
jalankan banyak akun dari 1 IP tanpa proxy residensial beda per akun. Skrip ini
untuk 1 akun saja.

## Status (probe 28 Nov 2026)

- Naruto: terdaftar + terverifikasi, saldo 0,002 USDT (2 klaim interstitial).
- Fleet 30/30 terdaftar pakai ref Naruto, referral total 30, qualified 0,
  flagged 0 — kualifikasi menunggu tugas tersedia.
- Runner harian jalan (klaim + pantau tugas + WD otomatis saat saldo ≥ 0,10).
