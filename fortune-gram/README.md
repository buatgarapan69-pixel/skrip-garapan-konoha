# FORTUNE GRAM — Mining GRAM Gratis (Web App)

Bot Telegram penghasil GRAM: mining coin lewat web app, gratis, tanpa deposit.

- Bot: https://t.me/fortune_grambot
- Daftar gratis: dapat **100 coin + 1 gift box**.
- Earn: **100 coin = $0,02/hari** (0,0002 USD/coin/hari, jalan otomatis).
- Gift box: hadiah **1–25 coin/box** (welcome 1 box + 1 box tiap referral).
- Referral: **+10 coin + 1 gift box** tiap teman join pakai link kamu.
- Klaim profit (profit → USD) min **$0,001**, klaim tiap hari.
- **Min WD: $0,05, fee $0,025**, WD GRAM (native) / USDT (jetton) ke alamat TON.
- **Payout BELUM terbukti cair.** WD pertama belum sampai min WD.

## Cara daftar

1. Buka https://t.me/fortune_grambot (pakai link referral temanmu kalau ada:
   `https://t.me/fortune_grambot?start=<user-id-teman>`).
2. Join channel, klik **Verify**.
3. Login web pakai **kode 6 digit dari bot** (skrip baca otomatis dari DM bot).

## Cara pakai skrip (1 perintah)

```bash
python3 fortune_gram_umum.py
```

Lalu pilih menu di dalam: `[1]` Daftar + login web, `[2]` Cek saldo,
`[3]` Klaim harian (gift box + klaim + WD kalau ≥ $0,05), `[4]` Keluar.

**Butuh:** `pip install telethon`, lalu buat `apicred.json` di folder yang
sama dengan `api_id`/`api_hash` kamu dari https://my.telegram.org:

```json
{"api_id": 12345678, "api_hash": "abc123..."}
```

Saat pertama jalan, masukkan nomor HP + kode login Telegram. Sesi login
tersimpan lokal (`fortune_session.session`) — **JANGAN disebar ke orang lain**.

**Sebelum WD, isi dulu di dalam skrip:** `WD_ADDRESS` = alamat TON kamu.
`REF_CODE` = user id Telegram pemberi referral (boleh kosong).
`PROXY_URL` = kosongkan untuk jalan langsung.

## Catatan jujur (dicek langsung 25–26 Nov 2026)

- Naruto (Admin Konoha) terverifikasi: **663 coin, $0,1326/hari**,
  30 gift box dibuka (+261 coin), klaim pertama **$0,0022 BERHASIL**
  (profit → USD, dicek dari state server). Saldo USD 0,0022 — **WD belum
  bisa** (min $0,05, perkiraan tercapai 26–27 Nov).
- Fleet 30/30 akun terdaftar pakai referral Naruto (friends=30, +300 coin).
- Klaim di bawah $0,001 ditolak server (`below_min`) — normal, tunggu
  profit terkumpul. WD di bawah $0,05 ditolak (`below_min`), saldo
  kurang ditolak (`insufficient_balance`) — semua dicek langsung.
- Jangan pernah deposit (min depo $3 — abaikan), jangan bayar verifikasi
  apa pun, jangan hubungkan wallet berisi dana. Satu perangkat = satu akun.
