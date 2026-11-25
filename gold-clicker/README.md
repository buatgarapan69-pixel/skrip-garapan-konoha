# GOLD CLICKER / EarnGCM — Mining Gold Bar, Convert ke SOL

Game web mining gratis. Main dive, kumpulkan **Gold Bar**, convert ke **SOL**
lewat faucet resmi. Tidak ada deposit, tidak ada top-up wajib.

- Main: https://play.earngcm.fun/ (pilih versi browser)
- Faucet/convert: https://www.earngcm.fun/faucet
- Token: $GCM — `6E8hG4V3aHjgTXLR2qrXkQFri5KFZXfoxCrgjmx2pump`

## Cara daftar

1. Buka https://play.earngcm.fun/ di browser (HP/laptop).
2. Akun guest langsung jadi — selesaikan tutorial (tap batu, buka crate,
   hire miner, merge miner).
3. Main dive (PLAY) + misi harian + Mint (forge Bar real-time).

## Cara earn Gold Bar

- **Dive**: 1 Bar per mark kedalaman. Dive pertama tiap hari ada bonus.
- **Misi harian**: selesaikan misi mode harian, dapat 1 Bar per misi.
- **Mint**: Gold Bar forge otomatis pakai timer real-time (tidak bisa dipercepat).
- **Daily**: klaim hadiah harian di kalender game (hari ke-1 sudah bisa).

## Min WD / klaim faucet

- **Rate: 1 Gold Bar = 0,0001 SOL.**
- **Min klaim 25 Bar** (= 0,0025 SOL). **Max 100 Bar/hari/akun**, reset 00:00 UTC.
- Caranya: di game buka **Settings → Account → GET WEBSITE CODE**
  (kode diawali `WEB`, berlaku 10 menit, sekali pakai), lalu masukkan di
  https://www.earngcm.fun/faucet + alamat SOL kamu.
- **Faucet pool TERBATAS** — klaim selagi masih ada. Status faucet bisa dicek
  pakai skrip di bawah (`status`).

## Status 25 Nov 2026 (dicek langsung)

- Faucet **BUKA** (tidak pause). Rate & limit terkonfirmasi live:
  1 Bar = 0,0001 SOL, min 25 Bar, max 100 Bar/hari, reset 00:00 UTC.
- **Pool HAMPIR KERING: 0,347 SOL tersisa** (wallet faucet
  `3CnuzU...Rw3UD`, dicek on-chain). Klaim terakhir 25 Nov 13:04 UTC
  (74 Bar) — sejak itu tidak ada klaim baru. Total terbayar sejauh ini:
  206 klaim, 11.923 Bar, 1,1923 SOL.
- **Mainnya WAJIB manual di HP**: tutorial game (drag merge miner)
  butuh sentuhan jari asli — tidak bisa diotomatisasi lewat browser.
  Setelah tutorial selesai, dive + klaim faucet bisa dibantu skrip ini.
  Klaim juga butuh **First Strike** (dive pertama) + akun cukup umur
  (cek di halaman faucet).

Faucet terbukti membayar on-chain (cek sendiri di
https://www.earngcm.fun/faucet, tab log): 206 klaim, 11.923 Bar,
1,1923 SOL total per 25 Nov 2026. Contoh tx: 40 Bar → 0,004 SOL
(`61KWtkjfwxTgskU4sve8VtKPbfUHa6HudGHWcBgVfBaefRgjksJ21oS19SGDebw4HkCQoyfZvhpuv8vfHDHsmdzF`).

## Skrip `gcm_umum.py` — 1 PERINTAH

Cek status faucet, buat akun guest, dan klaim faucet dari terminal.
Tidak berisi akun/kunci siapa pun — akunmu dibuat dari nol dan disimpan
lokal di `gcm_account.json` (jangan disebar).

```bash
pip install requests   # atau pakai stdlib saja (urllib)
python3 gcm_umum.py    # 1 perintah — pilih menu di dalam:
                       # [1] Cek faucet  [2] Daftar akun  [3] Klaim  [4] Keluar
```

Menu klaim minta website code dari game (Settings → Account →
GET WEBSITE CODE, berlaku 10 menit, sekali pakai) + alamat SOL kamu.

## Catatan

- Pack SOL/gems berbayar ($0,99–$4,99) itu opsional, BUKAN syarat earn.
- Game punya anti-cheat: setiap run di-replay server. Main wajar saja,
  satu orang satu akun — jangan farm.
- Website code cuma berlaku 10 menit: ambil kodenya, langsung klaim.
