# BRAMBLEKIN — Mining BRAM di Telegram (Gratis)

Game mining BRAM di Telegram. Token BRAM sudah trade di STON.fi.

- Bot: https://t.me/bramblekinbot
- Earn: **Daily Coin 10 BRAM/hari** + storage pasif ~10 BRAM/hari.
  Referral 5%/3%/1% (3 level).
- **Min WD live: 3000 BRAM** — dicek langsung dari API (`/api/state`,
  klaim channel 3000 BENAR).
- **Payout BELUM terbukti cair.** Token sudah trade di STON.fi,
  kontrak: `EQDwlhwuzUncNTLRxUtVUWsU1wQky43sbt72hn7m8LS_k-Nh`.
- **Grind lambat:** ~20 BRAM/hari tanpa referral → min WD 3000 BRAM
  = ~150 hari. Jangan berharap cepat.

## Cara daftar

1. Buka https://t.me/bramblekinbot (pakai link referral temanmu kalau ada:
   `https://t.me/bramblekinbot/bram?startapp=ref_<kode-teman>`).
2. Buka WebApp "🌳 Открыть BRAMBLEKIN".
3. Klaim Daily Coin 10 BRAM + klaim storage tiap hari.

## Cara pakai skrip (1 perintah)

```bash
python3 bramblekin_umum.py
```

Lalu pilih menu di dalam: `[1]` Daftar + buka WebApp, `[2]` Cek saldo +
referral, `[3]` Klaim Daily Coin + storage, `[4]` Cek info Withdraw,
`[5]` Keluar.

**Butuh:** `pip install telethon`, lalu buat `apicred.json` di folder yang
sama dengan `api_id`/`api_hash` kamu dari https://my.telegram.org:

```json
{"api_id": 12345678, "api_hash": "abc123..."}
```

Saat pertama jalan, masukkan nomor HP + kode login Telegram. Sesi login
tersimpan lokal (`bramblekin_session.session`) — **JANGAN disebar ke orang lain**.

## Catatan jujur (dicek langsung 26 Nov 2026)

- Naruto (Admin Konoha): Daily Coin 10 BRAM klaim, storage klaim 0,04 BRAM,
  saldo **10,04 BRAM**, referral 0 → 30 referral fleet terverifikasi server
  (level 1 = 30 pemain). Fleet 30/31 (Might mati — sesi Telegram dicabut).
- **Tap / tanam / kunjungi channel TERKUNCI** — server balas 503
  ("verifikasi wallet & pembayaran belum terhubung") kalau wallet belum
  terverifikasi. Butuh **verifikasi wallet TonConnect di HP** (gratis,
  hubungkan Tonkeeper + tanda tangan proof, TIDAK perlu kirim dana).
  Daily Coin + klaim storage jalan TANPA verifikasi wallet.
- Tugas deposit ("Пополнить"/top-up 5000/10000 BRAM, reward 250/750 BRAM)
  = **MODAL — jangan dikerjakan**. Tugas channel/chat (+10 BRAM) butuh
  visit yang saat ini ikut terkunci 503.
- Jangan pernah deposit, jangan bayar verifikasi apa pun, jangan hubungkan
  wallet berisi dana besar. Satu perangkat = satu akun.
