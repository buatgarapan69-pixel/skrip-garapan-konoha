# SHIBDropperBot — Gratis 10.000 SHIB

Mini App SHIB di BNB Smart Chain (BEP20). Bonus daftar **10.000 SHIB**,
per referral **5.000 SHIB**, min WD **20.000 SHIB + 2 referral terverifikasi**.
Berakhir **26 Desember 2026**.

> ⚠️ **Payout BELUM TERBUKTI.** WD Naruto (Tim Konoha, 27 Nov 2026)
> TERKENDALA: server menolak alamat wallet yang sudah dipakai akun lain
> (1 alamat = 1 akun). Jangan submit WD sebelum ada bukti WD landing.

## Cara pakai (Termux / Linux)

```bash
pip install telethon requests
python3 shibdropper.py
```

Lalu pilih menu di dalam skrip (1 perintah, semua di dalam):

- `[1]` Probe bot (cek respons saja)
- `[2]` Daftar + klaim bonus + simpan wallet
- `[3]` Cek saldo + status WD

## Yang harus diisi dulu

Buka `shibdropper.py`, isi bagian atas:

| Isian | Cara dapat |
|---|---|
| `API_ID` + `API_HASH` | Gratis di https://my.telegram.org (login → API development) |
| `SESSION_NAME` | Nama file sesi, mis. `"akun_saya"` |
| `WALLET_ADDRESS` | Alamat BEP20 **milikmu sendiri** (0x...). Wajib alamat yang **belum pernah** dipakai di bot ini — server menolak alamat yang sudah terdaftar akun lain. Boleh kosong (`""`) kalau cuma mau daftar dulu. |
| `REF_CODE` | (Opsional) kode referral pengundang |
| `PROXY` | (Opsional) proxy HTTP kamu, kosongkan kalau tidak ada |

Saat pertama jalan, Telethon minta nomor HP + kode OTP dari Telegram.
File `.session` yang terbentuk **JANGAN dibagikan** — itu kunci akunmu.

## Alur garapan

1. `/start` bot → join 3 channel → buka Mini App
2. Captcha logo-match (skrip jeda 7–12 detik, jangan di-spam)
3. Onboard → klaim bonus daftar 10.000 SHIB
4. Simpan wallet BEP20 → sebar link referral-mu
5. Tiap teman terverifikasi = +5.000 SHIB (teman wajib simpan wallet)

## Peringatan

- **JANGAN PERNAH** memasukkan private key / seed phrase ke skrip ini.
- Skrip ini **TIDAK** deposit, **TIDAK** WD otomatis, **TIDAK** meminta uang.
- WD di bot ini menarik **seluruh saldo** (tidak ada pilihan jumlah), dan
  saldo + referral yang dipakai WD dipotong permanen saat submit meski
  request ditolak. Jangan submit WD sebelum payout terbukti.
- Kalau bot minta deposit/fee sebelum bisa earn, **BERHENTI** — itu ciri
  scam/fee-gate.

Dibuat Tim Konoha, 27 Nov 2026. Gratis, tanpa garansi cuan.
