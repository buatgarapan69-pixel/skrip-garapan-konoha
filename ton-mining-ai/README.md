# TON MINING AI — Skrip Garapan Gratis

Bot: [@TonMiningai_Bot](https://t.me/TonMiningai_Bot) — mining token TMA di Telegram (Mini App).
Template white-label yang sama dengan QTF Miner (Upstash).

## Fakta live (27 Nov 2026, hasil probe + fleet 30 akun)

- Mining: **1 TMA/jam**, siklus 24 jam (klaim, lalu mulai sesi baru)
- Tugas join channel: **+6 TMA** (sponsor +5, channel resmi +1)
- Referral terverifikasi: **+5 TMA** + komisi 10% dari earn tugas teman
- Min WD: **100 TMA (≈ $0,1)** — rate 1000 TMA = 1 USDT / 1 GRAM, fee WD 0
- **2 WD pertama gratis** tanpa deposit (maks 2 WD, setting server `maxWithdrawCount: 2`)
- Daftar 100% gratis, tanpa deposit

## ⚠️ Status payout — JUJUR

- WD pertama (100 TMA) **sudah diajukan 27 Nov 2026 06:32 WIB**, status server `pending`,
  **BELUM LANDING** on-chain (dicek 06:35 WIB via TonCenter — tidak ada incoming GRAM).
  **Payout BELUM TERBUKTI.**
- Peringatan: QTF Miner (template yang sama) WD #1/#2 status server `approved`
  tapi `txHash` kosong — 2 hari tidak landing. Garapan ini satu template dengan QTF,
  jadi jangan anggap pasti bayar sebelum ada bukti landing on-chain.
- DYOR. Jangan deposit untuk "mempercepat" WD.

## File

| File | Fungsi |
|---|---|
| `tonminingai_probe.py` | Probe akun utama: daftar, connect wallet TON, start mining, klaim tugas gratis |
| `tonminingai_fleet.py` | Fleet multi-akun pakai ref akun utama (daftar + wallet + mining + tugas + verifikasi ref) |
| `roster.example.json` | Contoh roster fleet (nama + wallet TON tiap akun) |

## Cara pakai

### 1. Prasyarat

- Python 3.10+, `pip install telethon requests`
- `API_ID` + `API_HASH` dari https://my.telegram.org
- Sesi Telethon tiap akun (file `.session`, dibuat sekali via Telethon — JANGAN commit file ini)
- File HTML Mini App: buka Mini App TON MINING AI di browser, simpan halamannya sebagai
  `tonminingai_webapp.html` di folder ini (UP_URL + UP_TOKEN dibaca dari file itu, tidak pernah di-hardcode)

### 2. Probe akun utama

```bash
export TG_API_ID=123456 TG_API_HASH=isi_api_hash_kamu
export TG_SESSION=./sessions/utama.session
export TG_USER_ID=123456789 TG_USERNAME=username_kamu
export TON_WALLET=UQ...alamat_ton_kamu...
python3 tonminingai_probe.py
```

### 3. Fleet (opsional, pakai ref akun utama)

```bash
cp roster.example.json roster.json   # isi nama + wallet TON tiap akun
# taruh file .session tiap akun di ./sessions/<nama>.session
# proxy (opsional): isi proxy.txt — format:
#   Proxy username: user_kamu
#   Proxy password: password_kamu
# Tanpa proxy.txt = jalan langsung (dicatat di log).
export TG_API_ID=123456 TG_API_HASH=isi_api_hash_kamu TG_USER_ID=123456789
python3 tonminingai_fleet.py
```

Tiap akun fleet: User-Agent acak (seed per nama) + device ID UUID5 + sesi proxy sendiri
(kalau `proxy.txt` diisi). 1 wallet TON = 1 akun, jangan dipakai 2 akun.

### 4. WD (manual, dari hasil probe)

1. Klaim `refEarn` jadi saldo (`tvr`) dulu — di Mini App itu tombol klaim referral.
2. WD 100 TMA ke wallet TON yang ter-link di app, **hanya kalau saldo withdrawable ≥ 100 TMA**.
3. Cek landing on-chain (TonCenter/TonAPI) — status `pending`/`approved` di server
   BUKAN bukti landing. WD > 3 hari tidak landing = anggap scam (aturan 3 hari).

## Catatan keamanan

- TIDAK ADA api_id/api_hash, token, session, private key, password, email, atau nomor HP
  di repo ini — semua dibaca dari environment/file lokal kamu.
- Jangan pernah kirim dana/deposit ke alamat proyek sebelum payout terbukti.
- Skrip ini mirror logika Mini App (baca/tulis state Upstash yang sama) — kalau Mini App
  berubah, skrip bisa berhenti jalan dan perlu disesuaikan lagi.
