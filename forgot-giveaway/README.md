# Forgot Giveaway — Skrip Umum (1 Akun)

Giveaway harian Telegram gratis: kerjakan tugas = tiket, 1 tiket = 1 undian.
Tanpa deposit, tanpa wallet berisi dana, tanpa WD otomatis.

## Yang didapat (hasil probe 27 Nov 2026)

- Daftar gratis: `/start` bot, gabung @AirdropForgot, verifikasi
- 3 tugas join channel = **7 tiket gratis**
  (@AirdropForgot +2, @ForgotDisscussion +3, @DeskaOfficial +2)
- Giveaway tiap hari, 10 pemenang, hadiah **Rp2.000–Rp15.000/pemenang**
  (dipotong fee 15% saat menang), undian transparan (seed hash)
- Undang teman = **1 tiket per referral** terdaftar
- Min WD: **Rp10.000 ke DANA/SeaBank** (fee 15%, ACC manual admin).
  Di bawah Rp10.000 (min Rp1.000) cuma bisa via DM admin @Ibehh_yaeilah.
- USDT tidak aktif (WD USDT dimatikan admin saat probe).

## Catatan jujur — baca dulu

- **PAYOUT BELUM TERBUKTI** (27 Nov 2026): belum ada yang menang + WD dari
  tim kami saat skrip ini ditulis. Menang itu undian, bukan pasti.
- Beli tiket di toko (Rp300 + fee Rp100/tiket) **TIDAK disarankan** —
  skrip ini TIDAK PERNAH beli tiket, cuma pakai tiket gratis.

## Cara pakai (Termux / VPS / PC)

```bash
pip install telethon requests
```

1. Ambil API_ID + API_HASH di https://my.telegram.org/apps
2. Isi bagian KONFIG di `fg_umum.py` (API_ID, API_HASH;
   REF_CODE = kode referral pengundang, mis. `ref_1234567890` — boleh kosong)
3. Jalankan:

```bash
python3 fg_umum.py
```

- Login pakai nomor HP Telegram kamu + kode yang dikirim Telegram
- Pilih menu di dalam skrip: daftar, kerjakan tugas, ikut giveaway, cek saldo

File sesi (`fg_umum.session`) JANGAN dibagikan ke siapa pun.
Skrip ini TIDAK memakai referral siapa pun kecuali REF_CODE yang kamu isi.
