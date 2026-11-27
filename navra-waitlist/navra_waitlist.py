#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAVRA WAITLIST — join waitlist navra.com pakai email sendiri.
GRATIS 100%: cuma isi email, tanpa wallet / KYC / bayar.
Fakta (probe 27 Nov 2026): funding $19M Series A dipimpin Ribbit Capital
(BusinessWire 6 Okt 2026), founder Mike Cagney (ex-SoFi & Figure).
TIDAK ADA program referral, poin, token, atau tanggal buka — ini murni
waitlist early-access, BUKAN garapan instan. Jangan harap WD.

Cara pakai (Termux / Linux):
  1. python3 navra_waitlist.py            # nanti diminta isi email
  2. atau: NAVRA_EMAIL=email@kamu.com python3 navra_waitlist.py
  3. atau: python3 navra_waitlist.py email@kamu.com

Skrip ini memanggil endpoint yang sama dengan form di situs
(POST https://www.navra.com/_serverFn/<id>, body format Seroval).
Tidak ada captcha di form ini (per 27 Nov 2026). Kalau situs berubah
(id server fn ganti / muncul captcha), skrip perlu diperbaiki —
cek bundle JS situs untuk id terbaru.

Butuh: Python 3.8+ saja (stdlib, tanpa pip install).
"""
import json
import os
import sys
import urllib.error
import urllib.request

SERVER_FN_ID = "6b8ef6f8dc021cf75910b0b30a0e2e205a4f30bf124163c13adb4ccb9c08e3f0"
URL = "https://www.navra.com/_serverFn/" + SERVER_FN_ID

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, application/x-ndjson, application/json",
    "x-tsr-serverFn": "true",
    "User-Agent": UA,
    "Origin": "https://www.navra.com",
    "Referer": "https://www.navra.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not-A.Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Linux"',
}


class _Seroval:
    """Encoder Seroval minimal untuk nilai JSON polos (dict/str/bool/None).

    Hasilnya sama dengan seroval.toJSON() untuk payload seperti ini
    (diverifikasi 27 Nov 2026 lawan library seroval asli di Node).
    Hanya untuk dict/str/bool/None — JANGAN pakai untuk angka/list/
    tanggal, karena kodenya belum diimplementasikan.
    """

    def __init__(self):
        self._next_id = 0

    def encode(self, value):
        if isinstance(value, dict):
            idx = self._next_id
            self._next_id += 1
            keys = list(value.keys())
            vals = [self.encode(value[k]) for k in keys]
            return {"t": 10, "i": idx,
                    "p": {"k": keys, "v": vals}, "o": 0}
        if isinstance(value, str):
            return {"t": 1, "s": value}
        if value is True:
            return {"t": 2, "s": 2}
        if value is False:
            return {"t": 2, "s": 3}
        if value is None:
            return {"t": 2, "s": 0}
        raise TypeError(f"tipe tidak didukung Seroval mini: {type(value)}")

    def dumps(self, value):
        return json.dumps({"t": self.encode(value), "f": 127, "m": []},
                          separators=(",", ":"))


def _decode_prim(node):
    """Decode satu node Seroval primitif: {t:2,s:N} -> bool/None."""
    if isinstance(node, dict) and node.get("t") == 2:
        return {0: None, 1: None, 2: True, 3: False}.get(node.get("s"))
    if isinstance(node, dict) and node.get("t") == 1:
        return node.get("s")
    return None


def decode_result(body):
    """Ambil {success, alreadyJoined, hubspotSynced} dari respons server."""
    try:
        root = json.loads(body)
    except json.JSONDecodeError:
        return {}
    try:
        result = root["p"]["v"][0]  # node result {t:10, p:{k, v}}
        keys = result["p"]["k"]
        vals = result["p"]["v"]
        return {k: _decode_prim(v) for k, v in zip(keys, vals)}
    except (KeyError, IndexError, TypeError):
        return {}


def join_waitlist(email):
    payload = {"data": {"email": email, "source": "waitlist",
                        "marketingConsent": True}}
    body = _Seroval().dumps(payload).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = r.read().decode("utf-8", "ignore")
            return r.status, decode_result(resp), resp
    except urllib.error.HTTPError as e:
        return e.code, {}, e.read().decode("utf-8", "ignore")[:500]


def main():
    email = (sys.argv[1] if len(sys.argv) > 1
             else os.environ.get("NAVRA_EMAIL", "")).strip()
    if not email:
        email = input("Email untuk waitlist NAVRA: ").strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        print("Email tidak valid.")
        return 1
    print(f"Mendaftar {email} ke waitlist NAVRA...")
    status, result, raw = join_waitlist(email)
    print(f"HTTP {status}")
    if status == 200 and result.get("success"):
        if result.get("alreadyJoined"):
            print("Email ini SUDAH terdaftar sebelumnya.")
        else:
            print("BERHASIL! Email terdaftar di waitlist NAVRA.")
        print("Cek inbox email — undangan akses dikirim saat aplikasi dibuka.")
        return 0
    print("Gagal / respons tak dikenal. Detail:", result or raw[:300])
    print("Coba daftar manual di https://www.navra.com/#waitlist")
    return 1


if __name__ == "__main__":
    sys.exit(main())
