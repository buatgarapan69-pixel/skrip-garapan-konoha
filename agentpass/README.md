# AgentPass (APASS)

Paspor aktivitas **soulbound** gratis buat pemegang Binance Agent ID di BNB Smart Chain. 1 paspor per alamat, tidak bisa dipindah. Check-in harian gratis naikkan streak + level (AgentScore 0–100).

## Cara pakai (Termux / Linux)

```bash
python3 agentpass.py
```

Pilih menu di dalam skrip (1 perintah saja):

- `[1]` Cek status (paspor + level + kuota Founder)
- `[2]` Mint 1 paspor gratis (via contract call)
- `[3]` Check-in harian gratis (naikkan streak + level)
- `[4]` Keluar

Tidak perlu install apa-apa (hanya Python stdlib). Tanpa proxy, tanpa API key.

## PENTING — situs tidak ada tombol mint

Situs resminya **tidak pernah connect wallet dan tidak ada tombol mint**. Satu-satunya cara mint adalah panggil `mint()` langsung di kontrak (value 0) — persis yang dilakukan skrip ini via `baw contract-call`.

## Syarat

- Wallet BSC yang pegang **Binance Agent ID** (SPACE ID)
- Sedikit BNB buat gas (mint kami: ~0,0000078 BNB)
- CLI `baw` (Binance Agentic Wallet) sudah login dengan wallet kamu — **tidak ada private key di skrip ini**

## Yang didapat

- 1 paspor APASS (Founder edition, cap 1.000 — sisa 534 saat kami mint)
- Check-in harian gratis (`checkIn()`, 1x per hari UTC) → streak → level 0–4
- Verifikasi publik via API + AgentScore (lihat situs)

## Peringatan jujur

- **Nilai BELUM TERBUKTI** — ini paspor aktivitas, bukan janji cuan. Proyeknya sendiri bilang tidak menjanjikan return.
- Bukti mint kami (28 Nov 2026): token **#466**, tx `0xd20a067a…ad7a`, gas 0,0000078344 BNB.

## Sumber

- Situs: https://agentpass-sigma.vercel.app
- GitHub: https://github.com/Ragilsetiyo/agentpass
- Kontrak: `0x2CaB70C426F92C0d08aEb7cFe41b27b746feEb09`
