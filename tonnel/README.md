# TONEL MINNING — Mining TONNEL ⚡

Bot Telegram mining TONNEL (@TonnelNetworkGameBot). Mining 6 jam sekali,
lucky spin harian, task, referral.

- Bot: [@TonnelNetworkGameBot](https://t.me/TonnelNetworkGameBot)
- Channel: [@TonnelNetworkminer](https://t.me/TonnelNetworkminer)
- Backend: tonnelnetwork.online

## Earn

| Cara | Hadiah |
|---|---|
| Mining gratis | 0,0042 TONNEL/jam, siklus 6 jam (0,0252/siklus) |
| Lucky spin harian | +0,1 TONNEL |
| Task react channel | +0,05 TONNEL |
| Task join channel | +0,1 TONNEL |
| Referral (teman selesai task) | +0,1 TONNEL |
| Referral (teman verifikasi) | +1 TONNEL + 1 spin |

## Verifikasi (BERBAYAR)

Akun harus **verifikasi sekali dengan bayar 0,05 TON** dari wallet TON yang
terhubung ke bot — baru mining terbuka. Ini biaya nyata dan tidak bisa kembali.

## Withdraw

Min WD **10–20 TONNEL** (~$2,08 pada 1 TONNEL = $0,2078) ke wallet TON yang
terhubung. **Payout BELUM terbukti cair** — proyek baru, launch 26 Nov 2026.
Perkiraan grind 1 akun: ~0,2 TONNEL/hari → ~49 hari ke min WD.

## Cara pakai (Termux)

```bash
pkg install python -y
pip install telethon
git clone https://github.com/buatgarapan69-pixel/skrip-garapan-konoha
cd skrip-garapan-konoha/tonnel
python3 tonnel_umum.py
```

Lalu pilih menu di dalam skrip:

- `[1]` Daftar + login — buat dulu `apicred.json` dari
  https://my.telegram.org (isi `api_id` + `api_hash` kamu sendiri),
  isi `REF_CODE` kalau punya pemberi referral
- `[2]` Daily run (mining + spin + task + cek WD)
- `[3]` Cek status saja

Verifikasi 0,05 TON dilakukan dari dalam Mini App di Telegram (hubungkan
wallet TON → bayar invoice verifikasi), bukan dari skrip ini.

## Peringatan

Verifikasi 0,05 TON itu biaya nyata. Payout belum terbukti — jangan
verifikasi banyak akun sekaligus sebelum ada bukti WD pertama yang landing.
Satu perangkat = satu akun.

Hasil tim kami (27 Nov 2026): Naruto terverifikasi (0,05 TON), mining aktif,
saldo 0,25 TONNEL. Fleet ditahan sampai ada bukti WD Naruto.
