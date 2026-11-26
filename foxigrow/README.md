# FOXIGROW — Task Sosmed Dibayar USDT (Gratis)

Bot Telegram penghasil USDT: kerjain tugas sosmed (follow X/TikTok, join grup
Telegram, join Subreddit, nonton YouTube) dibayar USDT.

- Bot: https://t.me/FoxiTaskbot
- Daftar gratis, tanpa deposit.
- Earn: task follow X **$0,04**, TikTok **$0,03**, Reddit **$0,05**,
  YouTube (nonton 3 menit + like + subscribe) **$0,09**,
  join grup Telegram **$0,015**, check-in harian dapat FG Coin.
- Referral: komisi **10%** dari penghasilan teman (naik sampai 20% kalau
  temanmu banyak: 12% di 50 teman, 14% di 200, 16% di 500, 18% di 1.000).
- **Min WD: $2 USDT, fee 5% kalau WD di bawah $5** (gratis kalau WD ≥ $5).
- **Payout BELUM terbukti cair.** WD pertama belum sampai min WD.

## Cara daftar

1. Buka https://t.me/FoxiTaskbot (pakai link referral temanmu kalau ada:
   `https://t.me/FoxiTaskbot?start=ref_<user-id-teman>`).
2. Pilih bahasa, buka Mini App.
3. Check-in harian, kerjain task.

## Cara pakai skrip (1 perintah)

```bash
python3 foxigrow_umum.py
```

Lalu pilih menu di dalam: `[1]` Daftar + check-in, `[2]` Cek saldo & referral,
`[3]` Lihat daftar quest, `[4]` Coba klaim quest, `[5]` WD, `[6]` Keluar.

**Butuh:** `pip install telethon`, lalu buat `apicred.json` di folder yang
sama dengan `api_id`/`api_hash` kamu dari https://my.telegram.org:

```json
{"api_id": 12345678, "api_hash": "abc123..."}
```

Saat pertama jalan, masukkan nomor HP + kode login Telegram. Sesi login
tersimpan lokal (`foxigrow_session.session`) — **JANGAN disebar ke orang lain**.

**Sebelum pakai, isi dulu di dalam skrip:** `REF_CODE` = user id Telegram
pemberi referral (boleh kosong), `WD_ADDRESS` = alamat BEP20 USDT kamu,
`PROXY_URL` = kosongkan untuk jalan langsung.

## Catatan jujur (dicek langsung 26 Nov 2026)

- Naruto (Admin Konoha) terverifikasi: daftar OK (user #829673), check-in
  hari-1 sukses (+2 FG Coin), saldo **0 USDT**, 29 teman referral.
- Fleet 30/30 akun terdaftar pakai referral Naruto (inviteCount server: 29 —
  1 akun sudah punya akun Foxigrow lama, tidak kehitung referral).
- **Klaim quest butuh captcha Turnstile** — skrip ini tidak bisa
  menyelesaikannya. Kalau klaim mengembalikan `CAPTCHA_REQUIRED`, buka Mini
  App Foxigrow di HP dan klaim dari sana. Dari VPS, host challenge Cloudflare
  bahkan gagal DNS, jadi klaim otomatis tidak mungkin.
- Sebagian besar quest butuh akun sosmed di-bind dulu (X/TikTok/IG/FB/YouTube)
  dan verifikasi aksi (mis. retweet dulu sebelum bind X) — bind dilakukan di
  dalam Mini App, manual.
- Tanpa klaim manual dari HP, saldo USDT tetap 0. Ini garapan **grind lambat**,
  bukan instan: WD $2 butuh banyak task + klaim satu-satu.
