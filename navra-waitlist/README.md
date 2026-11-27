# NAVRA WAITLIST

Daftar waitlist gratis di **https://www.navra.com/** — jembatan TradFi ke
onchain economy. Funding **$19M Series A dipimpin Ribbit Capital**
(BusinessWire, 6 Okt 2026). Founder Mike Cagney (ex-SoFi & Figure).

## Fakta jujur (probe 27 Nov 2026)

- **Gratis 100%**: cuma isi email. Tanpa wallet, tanpa KYC, tanpa bayar.
- **TIDAK ADA referral** — tidak ada link/kode invite di situs.
- **TIDAK ADA poin / token / tanggal buka** — ini murni waitlist
  early-access, **BUKAN garapan instan**. Jangan harap WD.
- Nilai = slot awal di produk berfunding besar.

## Cara pakai

```bash
python3 navra_waitlist.py
# lalu isi email saat ditanya, atau:
NAVRA_EMAIL=email@kamu.com python3 navra_waitlist.py
# atau:
python3 navra_waitlist.py email@kamu.com
```

Butuh Python 3.8+ saja (stdlib, tanpa install apa-apa).

## Cara kerja skrip

Form situs mengirim `POST https://www.navra.com/_serverFn/<id>` dengan body
format **Seroval** (`{"data":{"email","source":"waitlist",
"marketingConsent":true}}`). Skrip ini memakai encoder Seroval minimal
(untuk nilai JSON polos) — tidak ada captcha di form ini per 27 Nov 2026.
Kalau situs berubah (id server fn ganti / muncul captcha), cek bundle JS
situs untuk id terbaru.

Output sukses: `BERHASIL! Email terdaftar di waitlist NAVRA.` Kalau email
sudah pernah daftar, server menjawab `alreadyJoined: true`.

## Catatan

- 1 email = 1 slot. Jangan spam submit — server menolak duplikat.
- Cek inbox berkala; undangan akses dikirim saat aplikasi dibuka.
- Skrip ini dibuat Tim Konoha, gratis untuk umum. Bukan afiliasi Navra.
