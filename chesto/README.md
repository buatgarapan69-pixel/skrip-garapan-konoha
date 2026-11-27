# Chesto AI — Daftar + Check-in Harian

Chesto (chesto.ai) adalah Human Action API: kerjakan tugas follow + komen di X,
dibayar USDC di jaringan Base. **Gratis, tanpa deposit, tanpa modal.**

## Cara pakai

```bash
python3 chesto.py
```

Pilih menu di dalam skrip (1 perintah saja, tidak ada subcommand):

1. **Daftar akun baru** — email temp dibuat otomatis (mail.tm), verifikasi
   email otomatis, langsung dapat kode referral kamu.
2. **Check-in harian + klaim welcome bonus** — login pakai email + password
   akunmu, klaim bonus daftar (+20 Karma) dan check-in harian (+3 Karma).
3. **Cek saldo / Karma / link referral** — lihat saldo USDC, Karma, jumlah
   referral, dan preview WD.
4. **Lihat tugas USDC aktif** — tanpa login, lihat semua tugas + syaratnya.
5. **Keluar**

Butuh: Python 3 + `pip install requests`.

## Isi referral kamu sendiri

Buka `chesto.py`, isi `REF_CODE = "u_xxxxxxxxxx"` dengan kode referral kamu
(kode itu muncul di menu [3] setelah daftar). Kalau kosong, pendaftaran
jalan tanpa referral. **Jangan isi kode referral orang lain** kalau kamu mau
dapat komisinya sendiri.

## Syarat jujur (hasil probe 27 Nov 2026)

- **Tugas USDC (0,1 USDC/tugas) HANYA bisa dikerjakan kalau akun X kamu
  umur 100+ hari, 40+ followers, 20+ tweet, 30+ following.** Akun X baru
  TIDAK bisa mengerjakan tugas USDC — tugasnya terkunci.
- **Min WD 0,01 USDC, fee 0**, dibayar USDC di jaringan Base (FluxaPay).
  Sekali tugas 0,1 USDC selesai, saldo sudah di atas min WD.
- **Karma BUKAN USDC dan TIDAK bisa ditukar jadi USDC.** Karma (bonus
  daftar +20, check-in +3/hari, tugas verifikasi +30) dipakai buat fee
  submit tugas (5 Karma per submit).
- **Komisi referral 33% dari fee platform** — hanya jalan kalau referralmu
  menyelesaikan tugas USDC yang didanai customer.
- **Chesto membatasi 2 akun baru per jaringan/hari.** Jangan daftar banyak
  akun dari 1 IP yang sama dalam sehari, nanti ditolak (429).
- **Payout BELUM terbukti** (saldo probe masih 0 USDC) — platformnya nyata
  (704 tugas 0,1 USDC sudah selesai per 27 Nov 2026), tapi WD pertama
  belum pernah dites sampai landing.

## Akun utama vs akun percobaan

Skrip ini daftar pakai **email temp (mail.tm)** — cocok buat percobaan.
Untuk akun utama yang mau dipakai lama, daftar manual di
https://chesto.ai/register pakai **email asli kamu** supaya bisa reset
password kalau lupa. Password akun temp **wajib disimpan sendiri** —
skrip mencetaknya sekali saat daftar.

## Catatan

- Bukan skrip resmi Chesto. Pakai dengan risiko sendiri.
- Jangan pernah memasukkan private key / seed phrase / dana ke situs apa pun.
- Kalau akun X kamu belum 100+ hari, daftar dulu saja — tugas USDC baru
  terbuka setelah akun X-mu cukup umur + followers.
