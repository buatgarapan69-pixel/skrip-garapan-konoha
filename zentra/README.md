# ZENTRA FINANCE — Quest Gratis, XP Jadi $ZNT

Quest platform lending/borrowing di Canton Network, Season 1 Genesis.
Mode Beta simulasi — tanpa deposit, tanpa dana riil. XP dikonversi ke
$ZNT di akhir season (10 XP = 1 ZNT). Referral: 10% XP teman.

> Payout $ZNT BELUM terbukti (konversi di akhir season, belum ada info WD).
> Gratis 100%. Jangan pernah deposit, jangan hubungkan wallet berisi dana.

## Cara daftar

1. Buka https://app.zentraone.xyz/quests (pakai link referral temanmu
   kalau ada — format: `https://app.zentraone.xyz/quests?ref=ZNT-XXXXXX`)
2. Daftar pakai email + password, lalu Connect Wallet -> ZENTRA Sky Wallet
3. Kerjakan quest: Supply, Borrow, Repay, Swap, Stake

## Cara pakai skrip ini (Termux / PC)

```bash
git clone https://github.com/buatgarapan69-pixel/skrip-garapan-konoha.git
cd skrip-garapan-konoha/zentra
python3 zentra_umum.py --list     # lihat daftar quest + XP
python3 zentra_umum.py --done "Daily Swap" 10   # catat quest selesai
python3 zentra_umum.py --status   # total XP + estimasi $ZNT
python3 zentra_umum.py --reset    # hapus progres lokal
```

Progres hanya tersimpan lokal di `zentra_progress.json`. Skrip ini TIDAK
login ke akunmu dan TIDAK menyimpan email/password apa pun.

## Tips quest on-chain (sudah terbukti jalan)

- Supply/Borrow/Repay: isi amount -> klik "Review ..." -> klik
  **"Authorize in wallet"** -> tunggu "Confirmed on ledger" -> klik "Verify".
  (Tombol konfirmasi BUKAN "Supply"/"Confirm" — jangan salah klik.)
- Swap: pilih aset -> isi amount -> "Authorize & swap" -> "Verify".
- Claim harian: buka "Open link" dulu, baru "Claim XP".
- Quest sosial butuh akun Telegram/X yang dihubungkan + diverifikasi.

## Bukti eksekusi Tim Konoha (25 Nov 2026)

- Naruto: 14/20 quest, 3.190 XP (1.330 quest + 1.860 referral), rank #16
- Fleet: 31/31 akun @ 930 XP (8 quest on-chain), tanpa flag/ban
