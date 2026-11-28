# SKYWARDEN — Mining App TON (1 akun)

Bot: [@SkywardenxBot](https://t.me/SkywardenxBot) · Mini App: skywarden-game.icu
Panduan resmi: https://info.skywarden-game.icu/

## Cara main (gratis)

1. Buka bot, kerjakan tugas: join channel + chat → dapat **300 SKYW**.
2. Undang teman lewat link referral kamu → klaim bonus referral
   (1 teman +100, 2 teman +200, 3 teman +300, 5 teman +100,
   10 teman +150, 25 teman +200 = total **1.050 SKYW**).
3. Beli kapal pertama (**1.000 SKYW**) → mining jalan otomatis
   **40 SKYW/hari**.
4. Klaim hasil mining tiap hari (menu Collect).
5. Kapal bisa di-upgrade 3× (maks 160 SKYW/hari untuk kapal 1);
   ada 10 jenis kapal, makin mahal makin besar hasil.

## Angka penting (terverifikasi dari API live, 28 Nov 2026)

- Kurs: **1.000 SKYW = 1 GRAM** (GRAM di sini = koin native TON).
- Min WD: **500 SKYW = 0,5 GRAM**.
- Syarat WD: hubungkan wallet TON + **aktivasi wallet 0,062 GRAM
  sekali per akun**, WD dikonfirmasi admin baru masuk antrean.
- Bonus tugas HANYA bisa dipakai beli/upgrade kapal (tidak bisa di-WD).
  Yang bisa di-WD: hasil mining + komisi referral (7%/3%/1% dari
  top-up teman, 3 level).
- Kecepatan gratisan: kapal 1 mining 40 SKYW/hari → min WD tercapai
  sekitar **12,5 hari** setelah kapal dibeli.
- **Payout BELUM TERBUKTI** oleh kami — channel proyek klaim 12 payout
  pada 27–28 Nov 2026. Jangan deposit/top-up kalau belum yakin.

## Cara pakai skrip

```bash
pip install telethon
python3 skywarden.py
```

- Ambil `API_ID` + `API_HASH` di https://my.telegram.org, isi di
  skrip atau via env `SKY_API_ID` / `SKY_API_HASH`.
- Login pertama kali pakai nomor HP + kode OTP Telegram.
- Kalau daftar lewat link teman, isi `SKY_REF_CODE` dengan kode
  `ref_...` dari linknya.
- Sesi tersimpan sebagai `skywarden_akun.session` — **jangan dibagikan**.

Skrip ini 1 perintah + menu di dalam skrip. Tidak ada deposit, top-up,
atau kirim dana dari wallet mana pun.
