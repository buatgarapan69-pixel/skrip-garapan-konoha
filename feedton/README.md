# FEEDTON — GRAM CITIZEN (skrip gratis, 1 akun)

Kartu citizen GRAM + poin FISH dari spin/misi. Pool $FISH ~$129rb, tutup 31 Des 2026.

## Cara pakai (Termux)

```bash
git clone https://github.com/buatgarapan69-pixel/skrip-garapan-konoha.git
cd skrip-garapan-konoha/feedton
pip install telethon requests
```

1. Isi `API_ID` + `API_HASH` di `feedton.py` (dari https://my.telegram.org/apps).
2. (Opsional) isi `REF_CODE` dengan kode invite temanmu (tanpa prefix `r_`). Kosong = daftar tanpa ref.
3. Jalankan, pilih menu `[01]`, login Telegram sekali (kode OTP).
4. Sesi tersimpan di `feedton.session` — **JANGAN dibagikan ke siapa pun**.

## Yang dilakukan skrip

- `/start` + buka Mini App, ambil initData
- Auth + terbitkan kartu citizen GRAM
- Join channel @tonfish_tg + grup @tonfish_en (buat misi)
- Klaim: check-in harian, free spin, spin piece, tugas kartu/channel/grup, misi visit, umur akun TG, mystery box, kode harian sendiri
- Spin semua sampai habis, kumpulin poin FISH

## Jujur

- **Payout BELUM TERBUKTI.** Poin FISH jadi bagian pool $FISH, baru dibagi habis pool tutup (31 Des 2026).
- Reward $FISH butuh connect wallet TON — lakukan dari HP sendiri, jangan di skrip ini.
- Tanpa deposit, tanpa top-up. Spin tidak bisa dibeli. Batas harian 50 spin, 250/minggu.
- Referral: yang daftar pakai ref harus pakai kode polos (tanpa `r_`) di `REF_CODE`, kalau tidak referral tidak kehitung.
