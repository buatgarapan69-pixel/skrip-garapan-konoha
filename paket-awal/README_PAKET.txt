============================================================
  PAKET SKRIP TIM KONOHA — buat dipakai siapa saja
  (dibagikan ke grup Markas, 24 Nov 2026)
  Semua file sudah dibersihkan dari data pribadi.
  Isi dulu placeholder dengan data MILIKMU SENDIRI.
============================================================

DAFTAR SKRIP (12 file):

1. template_markas.py
   Template tampilan CYBER EDITION (banner FIGlet, warna merah/
   kuning/hijau/biru, efek ketik, loading, menu) — patokan buat
   bikin skrip baru. Cara pakai: import fungsinya dari skripmu
   atau copy polanya.

2. wallet.py
   Cek saldo + sweep MULTI-CHAIN (EVM/BSC, SOL, TON, SUI, BTC)
   buat banyak wallet sekaligus. Baca private key dari file
   kamu sendiri (pkevm.txt, pkton.txt, pksol.txt, pksui.txt,
   pkbtc.txt). Menu di dalam skrip.
   Jalanin: python wallet.py
   WAJIB ISI DULU: alamat wallet tujuan di bagian config
   (MAIN_EVM / VPS_EVM / MAIN_TON / MAIN_SOL).

3. wallets.py
   Cek saldo SEMUA wallet EVM (BSC) + sweep USDT/BNB ke wallet
   utama. Baca key dari pkevm.txt. Menu di dalam skrip.
   Jalanin: python wallets.py
   WAJIB ISI DULU: MAIN_WALLET / VPS_WALLET di bagian config.

4. wallet_lite.py
   Versi ringan (murni stdlib, tanpa pip): bikin wallet baru
   (EVM/SOL/TON) + cek saldo.
   Jalanin: python wallet_lite.py

5. topnod_email.py
   Baca OTP dari inbox temp email (generator.email). Menu di
   dalam skrip, OTP tersimpan di file biar bisa dibaca ulang.
   Jalanin: python topnod_email.py
   WAJIB ISI DULU: daftar DOMAINS dengan domain temp email
   kamu sendiri (lihat https://generator.email).

6. markas_send.py
   Kirim laporan / keputusan / rekap ke channel Telegram
   (format monospace branded, nomor laporan otomatis).
   Jalanin: python markas_send.py --laporan --judul "NAMA" --isi "TEKS"
            python markas_send.py --keputusan --reply 123 --isi "KEPUTUSAN: ..."
            python markas_send.py --bebas --isi "teks bebas"
            Tambah --dry-run buat lihat hasil tanpa mengirim.
   Butuh: api_id/api_hash + sesi Telegram kamu (lihat apicred.py).

7. markas_read.py
   Baca N pesan terakhir channel Telegram.
   Jalanin: python markas_read.py --n 5
            python markas_read.py --n 10 --cari LAPORAN
   Butuh: api_id/api_hash + sesi Telegram kamu.

8. scan.py
   Scan channel-channel garapan buat cari garapan baru
   (15 channel inti + 134 channel tier-2). Hasil JSON ke logs/.
   Jalanin: python scan.py --tier1
            python scan.py --tier2 --limit 20
   Butuh: api_id/api_hash + sesi Telegram kamu. Edit daftar
   channel (TIER1/TIER2) sesuai kebutuhanmu.

9. hacker.py
   Skrip terminal interaktif (banner + status live channel/grup
   via Telethon).
   Jalanin: python hacker.py
   Butuh: sesi Telegram kamu (dicari otomatis di folder session/).

10. vmos_client.py
    Klien API VMOS Cloud (lihat device, jalankan perintah).
    Jalanin: python vmos_client.py padlist
             python vmos_client.py cmd "<script>"
    Butuh: file .vmos_api berisi {"access_key": "...",
    "secret_key": "..."} + isi PAD dengan padCode device
    VMOS kamu.

11. apicred.py (helper)
    Baca api_id/api_hash Telegram dari file session/apicred.json
    atau env TG_API_ID / TG_API_HASH. Dipakai markas_send,
    markas_read, scan, hacker. Daftar dulu di
    https://my.telegram.org buat dapat api_id/api_hash sendiri.

12. tgsession.py (helper)
    Cari + load file sesi Telethon (.session). Dipakai
    markas_send dan markas_read.

------------------------------------------------------------
SYARAT UMUM
------------------------------------------------------------
- Python 3.8+ (di Termux: pkg install python)
- Skrip Telegram (markas_send, markas_read, scan, hacker):
  pip install telethon
  + api_id/api_hash dari https://my.telegram.org
  + sesi Telegram kamu sendiri (file .session)
- Skrip wallet: TIDAK butuh pip (murni stdlib).
  Butuh file private key / mnemonic KAMU SENDIRI.

------------------------------------------------------------
PERINGATAN KEAMANAN — BACA DULU, PENTING!
------------------------------------------------------------
- JANGAN PERNAH kirim private key / mnemonic / seed phrase /
  password / API key ke siapa pun, termasuk ke grup ini.
  Admin TIDAK PERNAH minta private key kamu.
- Skrip wallet HANYA membaca file pk di HP/VPS kamu sendiri.
  Jangan pernah pakai file pk orang lain.
- Isi semua placeholder (ALAMAT_..._ANDA, PADCODE_VMOS_ANDA,
  DOMAINS, api_id/api_hash) dengan data MILIKMU SENDIRI
  sebelum menjalankan skrip.
- Kalau ada yang minta private key dengan alasan apa pun,
  itu PENIPU. Abaikan + lapor admin.
