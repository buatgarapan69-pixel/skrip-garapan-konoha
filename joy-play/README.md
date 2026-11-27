# JOY PLAY — Skrip Umum

Bot Telegram **@joyplayappbot** (Mini App panel IDR, bukan kripto).

## Cara earn

- Undang teman terverifikasi: **Rp500/orang**
- Mystery Box gratis tiap hari: **Rp100–Rp600**
- Min WD: **Rp10.000** ke DANA / OVO / GoPay / ShopeePay / Bank / Pulsa
- WD manual admin, maks 1×24 jam

## Jujur soal payout

**BELUM TERBUKTI.** Saldo referral + box sudah masuk (terverifikasi di API),
tapi penarikan butuh nomor e-wallet dan ditransfer manual oleh admin —
belum ada bukti transfer yang landing. Garap **gratis saja**, jangan deposit,
jangan hubungkan wallet berisi dana.

## Cara pakai (Termux / VPS / PC)

```bash
pip install telethon requests
export TG_API_ID=123456 TG_API_HASH=isi_dari_my_telegram_org
# opsional, kode referral temanmu:
export JOYPLAY_REF=ref_1234567890
python3 joyplay_umum.py
```

Pilih menu di dalam skrip:

- `[1]` Daftar + verifikasi + buka Mystery Box
- `[2]` Cek saldo / status akun
- `[3]` Keluar

Skrip ini tidak berisi session, token, password, atau referral siapa pun.
Semua data akun dibaca dari session Telethon milikmu sendiri.
API key Telegram ambil sendiri di https://my.telegram.org
