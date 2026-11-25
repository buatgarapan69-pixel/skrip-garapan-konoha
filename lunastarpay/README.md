# LUNA STAR PAY BOT — Earn Telegram Stars (Gratis)

Bot Telegram penghasil Stars: referral + daily bonus. Gratis, tanpa deposit.

- Bot: https://t.me/LUNASTARPAYBOT
- Earn: **+4 Stars tiap teman** join pakai link referral kamu.
- Daily Bonus tiap 24 jam (klaim di menu bot).
- **Min WD live: 25 Stars** (max 1000). Klaim channel (20 Stars) SALAH —
  angka 25 ini dicek langsung dari menu Withdraw bot.
- **Payout BELUM terbukti cair.** Server klaim 162 user, 75 Stars payout,
  tanpa bukti on-chain. WD butuh 7 referral (7 × 4 = 28 Stars).

## Cara daftar

1. Buka https://t.me/LUNASTARPAYBOT (pakai link referral temanmu kalau ada:
   `https://t.me/LUNASTARPAYBOT?start=<user-id-teman>`).
2. Join 12 channel, klik **Complete**.
3. **Verifikasi di HP (Turnstile)** — buka bot di HP, ketuk
   **Start Verification**, selesaikan Turnstile di webview Telegram.
   Verifikasi TIDAK bisa lewat skrip/VPS.
4. Menu kebuka: Profile, Withdraw, Referral, Daily Bonus, Support,
   Statistics, Leaderboard.

## Cara pakai skrip (1 perintah)

```bash
python3 lunastarpay_umum.py
```

Lalu pilih menu di dalam: `[1]` Daftar + join channel, `[2]` Cek saldo +
referral, `[3]` Klaim Daily Bonus, `[4]` Cek info Withdraw, `[5]` Keluar.

**Butuh:** `pip install telethon`, lalu buat `apicred.json` di folder yang
sama dengan `api_id`/`api_hash` kamu dari https://my.telegram.org:

```json
{"api_id": 12345678, "api_hash": "abc123..."}
```

Saat pertama jalan, masukkan nomor HP + kode login Telegram. Sesi login
tersimpan lokal (`luna_session.session`) — **JANGAN disebar ke orang lain**.

## Catatan jujur (dicek langsung 25 Nov 2026)

- Naruto (Admin Konoha) terverifikasi via HP, saldo **0,10 Stars**,
  referral 0. Daily Bonus sudah diklaim (cooldown 24 jam).
- **Fleet TIDAK bisa verifikasi dari VPS**: Turnstile macet di headless
  browser (150 detik, tanpa verdict) dan proxy terlalu lambat
  (page load timeout 180 detik). Referral dari akun yang belum verifikasi
  TIDAK terhitung (Total Refer tetap 0).
- Jadi garapan ini paling cocok untuk user HP asli (satu perangkat =
  satu akun — bot memakai fingerprint perangkat, multi-akun dari
  1 perangkat berisiko di-flag).
- Jangan pernah deposit, jangan bayar verifikasi apa pun, jangan hubungkan
  wallet berisi dana. Jangan pakai VPN/proxy saat verifikasi.
