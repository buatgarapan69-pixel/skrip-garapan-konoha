# Panduan Termux (HP Android)

Jalankan skrip repo ini dari HP pakai Termux.

## 1. Install Termux

Download dari **F-Droid** (resmi):

- https://f-droid.org/en/packages/com.termux/

Alternatif: https://github.com/termux/termux-app/releases

JANGAN dari Play Store — sudah tidak diupdate.

## 2. Install git + python

Buka Termux, jalankan:

```bash
pkg update -y
pkg install git python -y
```

## 3. Clone repo ini

```bash
git clone https://github.com/buatgarapan69-pixel/skrip-garapan-konoha.git
cd skrip-garapan-konoha
```

## 4. Jalankan skrip garapan

Masuk ke folder garapannya, baca `README.md` di dalam folder itu,
install dependensi yang tertulis, lalu jalankan:

```bash
cd qtf-miner
pip install telethon requests
python3 qtf_umum.py
```

## 5. API_ID + API_HASH (buat skrip Telethon)

Skrip berbasis Telethon butuh API_ID + API_HASH milik kamu sendiri:

1. Buka https://my.telegram.org/apps (dari browser HP)
2. Login pakai nomor Telegram kamu
3. Buat aplikasi, salin API_ID (angka) + API_HASH (kode)
4. Isi ke dalam skrip sebelum dijalankan (buka file-nya, cari baris API_ID / API_HASH)

Jangan pakai API_ID / API_HASH orang lain.

## 6. Update skrip ke versi terbaru

```bash
cd skrip-garapan-konoha
git pull
```

## Peringatan

- Jangan pernah kirim private key / seed phrase ke siapa pun.
- Jangan jalankan skrip dari sumber yang tidak kamu kenal tanpa membaca isinya dulu.
- Semua garapan di repo ini gratis — kalau ada yang minta deposit / top-up,
  berhenti dan jangan lanjut.
