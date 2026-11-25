#!/usr/bin/env python3
"""ZENTRA FINANCE — Quest tracker gratis (versi umum / sanitasi).
ZENTRA Finance (app.zentraone.xyz) = quest platform lending/borrowing di
Canton Network, Season 1 Genesis Phase. Mode BETA (simulasi) — tanpa deposit,
tanpa dana riil. XP dikonversi ke $ZNT di akhir season (10 XP = 1 ZNT).
Referral: 10% dari XP teman.

CARA PAKAI (manual, tanpa bot):
  1. Buka https://app.zentraone.xyz/quests
     (pakai link referral temanmu kalau ada — contoh format:
     https://app.zentraone.xyz/quests?ref=ZNT-XXXXXX)
  2. Daftar pakai email + password, lalu Connect Wallet -> ZENTRA Sky Wallet.
  3. Kerjakan quest di bawah ini, catat progresmu di sini:
       python3 zentra_umum.py --done "Supply Your First Asset" 50
       python3 zentra_umum.py --done "Daily Swap" 10
  4. Lihat total XP + estimasi $ZNT:  python3 zentra_umum.py --status
  5. Reset progres:                   python3 zentra_umum.py --reset

TIPS QUEST ON-CHAIN (yang sudah terbukti jalan):
  - Supply/Borrow/Repay: isi amount -> klik "Review ..." -> klik
    "Authorize in wallet" -> tunggu "Confirmed on ledger" -> klik "Verify".
    (Tombol konfirmasi BUKAN "Supply"/"Confirm" — jangan salah klik.)
  - Swap: pilih aset -> isi amount -> "Authorize & swap" -> "Verify".
  - Claim harian: buka "Open link" dulu, baru "Claim XP".
  - Quest sosial butuh akun Telegram/X yang dihubungkan + diverifikasi.

PERINGATAN: gratis 100%. Jangan pernah deposit, jangan hubungkan wallet
berisi dana, jangan bayar verifikasi apa pun. Payout $ZNT BELUM terbukti
(konversi di akhir season). Skrip ini TIDAK login ke akunmu dan TIDAK
menyimpan email/password apa pun — progres hanya tersimpan lokal.
"""
import argparse, json, os, sys

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "zentra_progress.json")

QUESTS = [
    # (nama, XP, jenis)
    ("Supply Your First Asset", 50, "ONCHAIN · ONE-TIME"),
    ("Open Your First Borrow Position", 75, "ONCHAIN · ONE-TIME"),
    ("Repay a Loan", 75, "ONCHAIN · ONE-TIME"),
    ("Daily Swap", 10, "ONCHAIN · DAILY"),
    ("Swap $ZNT To CC", 200, "ONCHAIN · DAILY"),
    ("Explore Market & Supply CC", 120, "ONCHAIN · DAILY"),
    ("Explore Market & Supply $ZNT", 150, "ONCHAIN · DAILY"),
    ("Stake $ZNT and Earn Daily XP", 250, "ONCHAIN · DAILY"),
    ("Join the Official ZENTRA Telegram Group", 20, "SOCIAL · ONE-TIME"),
    ("Join the ZENTRA WhatsApp Channel", 20, "SOCIAL · ONE-TIME"),
    ("Follow ZENTRA on X", 20, "SOCIAL · ONE-TIME"),
    # Sisa quest sosial (10) + kreatif (4): nilai XP masing-masing cek di
    # halaman Quests — total ada 22 quest.
]

def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            return {}
    return {}

def save(d):
    json.dump(d, open(STATE_FILE, "w"), indent=2)

def main():
    ap = argparse.ArgumentParser(description="ZENTRA quest tracker (gratis)")
    ap.add_argument("--done", nargs=2, metavar=("QUEST", "XP"),
                    help="tandai quest selesai, contoh: --done \"Daily Swap\" 10")
    ap.add_argument("--status", action="store_true", help="lihat progres + estimasi $ZNT")
    ap.add_argument("--list", action="store_true", help="daftar quest on-chain yang diketahui")
    ap.add_argument("--reset", action="store_true", help="hapus progres lokal")
    a = ap.parse_args()

    if a.list:
        print("ZENTRA — 22 quest (Onchain 8, Social 10, Creative 4)")
        print("10 XP = 1 $ZNT (konversi akhir season). Referral: 10% XP teman.")
        for name, xp, kind in QUESTS:
            print(f"  [{kind}] {name} — +{xp} XP")
        print("Sisa quest sosial/kreatif: cek langsung di halaman Quests.")
        return 0

    if a.reset:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        print("Progres lokal dihapus.")
        return 0

    if a.done:
        name, xp = a.done[0], int(a.done[1])
        d = load()
        d[name] = {"xp": xp, "done": True}
        save(d)
        print(f"OK: {name} (+{xp} XP) tercatat.")
        return 0

    # default: status
    d = load()
    total = sum(v.get("xp", 0) for v in d.values())
    print("ZENTRA FINANCE — progresmu")
    print(f"  Quest selesai: {len(d)}/22")
    print(f"  Total XP: {total}")
    print(f"  Estimasi $ZNT: {total / 10:.1f} (10 XP = 1 ZNT, akhir season)")
    if d:
        for name, v in d.items():
            print(f"    - {name}: +{v['xp']} XP")
    print("Catat quest selesai dengan: --done \"Nama Quest\" XP")
    print("Payout BELUM terbukti — jangan deposit/modal apa pun.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
