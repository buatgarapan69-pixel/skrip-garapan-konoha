# NULLKIN — Whitelist NFT (Free Mint)

Whitelist NFT pixel-art untuk jaringan Zero (ekosistem LayerZero).
Proyek independen, bukan proyek resmi LayerZero. Mint-nya **free mint**
(cek raffle Tessera: Price: Free mint). Daftar **gratis** — tanpa connect
wallet, tanpa signature, tanpa bayar.

- Situs: https://nullkin.xyz
- X proyek: https://x.com/nullkin_NFT
- Postingan tugas: https://x.com/nullkin_NFT/status/2126121257431076888
- Mainnet Zero dijadwalkan 30 Nov 2026. Deadline & supply form tidak
  diumumkan di situs — daftar selagi terbuka.

## Syarat daftar (4 tugas, semua di X)

1. Follow @nullkin_NFT di X.
2. Like + repost postingan tugas di atas.
3. Reply postingan tugas itu, salin link balasan kamu.
4. Isi alamat EVM (0x, alamat publik saja — JANGAN pernah seed phrase)
   di situs, unduh/simpan signal card, posting card itu di X,
   salin link postingan card kamu.

Lalu di situs: centang persetujuan, klik **Send my signal**.
Aplikasi disimpan untuk review — **spot tidak dijamin**, diseleksi proyek.

## Cara pakai skrip

Isi dulu data kamu (jangan pakai data orang lain):

```bash
# 1. Buat signal card kamu (butuh Pillow: pip install pillow)
python3 nullkin_card.py --handle usernamekamu --wallet 0xALAMAT_EVM_KAMU
# -> nullkin-signal-XXXX.png (XXXX = nomor signal dari handle + wallet)

# 2. Kerjakan 4 tugas X di atas (manual, dari akun X kamu),
#    salin link reply dan link postingan card kamu.

# 3. Kirim aplikasi (validasi dulu seperti di situs, baru POST)
python3 nullkin_submit.py --handle usernamekamu \
  --wallet 0xALAMAT_EVM_KAMU \
  --comment https://x.com/usernamekamu/status/1111111111111111111 \
  --share https://x.com/usernamekamu/status/2222222222222222222
```

Skrip `nullkin_submit.py` memakai endpoint publik yang sama dengan
situs (Google Apps Script dari `config.json` nullkin.xyz). Jawaban
server: `ok: true` = tersimpan; `existing: true` = wallet/username
sudah terdaftar, tidak perlu daftar lagi.

## Yang TIDAK boleh dilakukan

- Jangan submit link reply/postingan palsu atau milik orang lain —
  aplikasi di-review manual, yang palsu tidak lolos.
- Jangan connect wallet berisi dana, jangan sign transaksi apa pun,
  jangan kirim seed phrase ke siapa pun.
- Satu username X = satu aplikasi. Jangan farming banyak akun.

## Catatan jujur

- Ini whitelist, bukan WD: belum ada mint, belum ada harga, payout
  belum terbukti. Nilai NFT-nya belum tahu.
- Postingan tugas di situs kadang berbeda dengan yang diumumkan
  (live API pernah menampilkan postingan lain) — ikuti postingan
  yang tampil di situs saat kamu buka.
