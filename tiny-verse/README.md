# Tiny Verse — Rawat Galaksi 3D, Panen Stardust ($TINY)

Garapan gratis dari kreator **Major** (backing $2,1M, ekosistem TON).
Rawat galaksi 3D, panen stardust tiap 4–8 jam, kejar snapshot **$TINY**.

## Yang penting (jujur)

- **BUKAN WD instan.** $TINY belum TGE. Yang dikejar adalah snapshot
  Q4 2026 – Q1 2027 (55% supply untuk stargazer aktif). Belum ada yang
  terbukti cair — jangan harap duit cepat.
- **Gratis, tanpa deposit.** Skrip ini TIDAK top-up, TIDAK hubungkan
  wallet berisi dana, TIDAK beli boost/stars.
- **Referral:** atribusi referral TinyVerse HANYA jalan kalau temanmu
  buka link referral **lewat aplikasi Telegram resmi** (tap link
  startapp di HP). Lewat skrip/Telethon, referral TIDAK kehitung
  (sudah dibuktikan: 5 metode dicoba, invites tetap 0). Sebar link
  referralmu ke orang beneran.

## Cara pakai (Termux / Linux)

```bash
pip install telethon requests
```

1. Buat file `config.txt` di folder yang sama, isinya 2 baris:
   - baris 1: API ID kamu (angka, dari https://my.telegram.org)
   - baris 2: API HASH kamu
2. Buat folder `sessions/`, taruh file `.session` kamu di dalamnya
   (1 file = 1 akun Telegram).
3. Jalankan (1 perintah, pilih menu di dalam):

```bash
python3 tinyverse.py
```

- `[1]` Daftar + buat galaksi + klaim (semua sesi) — pertama kali.
  Saat diminta, paste LINK REFERRAL kamu sendiri, contoh:
  `https://t.me/tverse?startapp=galaxy-KODEGALAXIMU`
  (ambil dari dalam Mini App @tverse: menu Invites > copy link.
  Kosongkan saja kalau tidak punya — akun tetap jalan tanpa referral.)
- `[2]` Klaim dust harian saja (semua sesi) — jalankan tiap 4–8 jam.
- `[3]` Keluar.

## Yang dilakukan skrip (per akun)

- Buka Mini App @tverse, login ke server TinyVerse
- Buat galaksi pertama (gratis, dapat 1.000 stars)
- Panen stardust yang sudah terkumpul (gratis)
- Join channel @tvappchannel + grup @tverseapp (award community)
- Tampilkan: member id, galaksi, stars, saldo stardust

## Peringatan

- 1 sesi Telethon = 1 akun, 1 IP. Jangan jalankan sesi yang sama dari
  2 tempat/IP bersamaan — sesi bisa MATI permanen.
- Jangan pernah bagikan file `.session` atau `config.txt` kamu ke
  orang lain. Siapa pun yang pegang file itu bisa masuk ke akunmu.

Dibuat oleh Tim Konoha — gratis, silakan dipakai & dibagikan.
