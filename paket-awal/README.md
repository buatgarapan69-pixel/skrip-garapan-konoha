# Paket Awal (24 Nov 2026)

Paket skrip pertama yang dibagikan Tim Konoha: kumpulan tools pembantu
(bukan garapan), plus tutorial Termux. Semua gratis, tanpa data pribadi.

## Isi paket

- `README_PAKET.txt` — penjelasan paket (dokumen asli)
- `TUTORIAL_TERMUX.txt` — cara setup Termux dari nol (dokumen asli)
- `apicred.py` — loader kredensial Telegram. Buat file `apicred.json` sendiri
  berisi API_ID + API_HASH kamu (dari https://my.telegram.org/apps).
- `hacker.py` — skrip info/branding (status channel/grup).
- `markas_read.py` / `markas_send.py` — baca & kirim laporan ke channel/grup
  kamu sendiri. **Sesuaikan ID channel/grup dengan punyamu** (jangan pakai
  ID yang tertulis di skrip).
- `template_markas.py` — template tampilan skrip (gaya Markas Cyber Edition).
- `tgsession.py` — pembantu sesi Telethon.

## Yang TIDAK ikut di-push (ditahan)

- `scan.py` — berisi daftar ID channel/nomor yang belum terverifikasi semuanya
  ID channel publik; ditahan sampai ada versi bersih.
- `wallet.py`, `wallet_lite.py`, `wallets.py` — tools wallet pribadi, mengandung
  pola private key / nomor HP; tidak cocok dibagikan apa adanya.
- `vmos_client.py` — client VMOS, mengandung nilai kredensial yang tampak asli.
- `topnod_email.py` (versi paket ini) — digantikan versi terbaru di folder
  `topnod/` (sudah dibersihkan dari contoh domain).

## Cara pakai

```bash
pip install telethon requests
python3 hacker.py
```

Baca `TUTORIAL_TERMUX.txt` dulu kalau baru pertama kali pakai Termux.
