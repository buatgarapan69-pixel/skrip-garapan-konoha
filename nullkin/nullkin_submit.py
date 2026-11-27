#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NULLKIN whitelist — kirim aplikasi dari terminal (tanpa browser).

Memakai endpoint publik yang sama dengan situs nullkin.xyz
(Google Apps Script dari config.json situs). Stdlib saja.

ISI DULU data kamu sendiri, lalu:
  python3 nullkin_submit.py --handle usernamekamu \
    --wallet 0xALAMAT_EVM_KAMU \
    --comment https://x.com/usernamekamu/status/111... \
    --share https://x.com/usernamekamu/status/222...

Syarat sebelum jalan: 4 tugas X sudah dikerjakan BENERAN dari akun
kamu (follow @nullkin_NFT, like + repost postingan tugas, reply,
posting signal card). Jangan submit link palsu — aplikasi di-review
manual dan yang palsu tidak lolos. GRATIS, tanpa bayar apa pun.
"""
import argparse
import json
import re
import sys
import urllib.request

API = "https://script.google.com/macros/s/AKfycbxkGR4vXZmKE9hIZEb83_efeaWICKiIXVnI0GDuSazBgQECcdKyM4Iw40W1x2W4kuOC4w/exec"
TASK_POST_ID = "2126121257431076888"  # dari config.json nullkin.xyz

HANDLE = re.compile(r"^@?([A-Za-z0-9_]{1,15})$")
WALLET = re.compile(r"^0x[0-9a-fA-F]{40}$")
POST = re.compile(
    r"^https://(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})/status/([0-9]{1,25})/?$",
    re.I,
)


def post_of(value):
    m = POST.match((value or "").strip().split("?")[0].split("#")[0])
    if not m:
        return None
    return {"author": m.group(1), "id": m.group(2),
            "url": "https://x.com/%s/status/%s" % (m.group(1).lower(), m.group(2))}


def main():
    ap = argparse.ArgumentParser(description="Kirim aplikasi whitelist NULLKIN")
    ap.add_argument("--handle", required=True, help="username X kamu, tanpa @ juga boleh")
    ap.add_argument("--wallet", required=True, help="alamat EVM 0x (publik saja)")
    ap.add_argument("--comment", required=True, help="link reply kamu ke postingan tugas")
    ap.add_argument("--share", required=True, help="link postingan signal card kamu")
    ap.add_argument("--no-check", action="store_true",
                    help="lewati cek status buka (tidak disarankan)")
    a = ap.parse_args()

    hm = HANDLE.match(a.handle.strip())
    if not hm:
        sys.exit("ERROR: username X tidak valid (huruf/angka/_ saja, maks 15).")
    handle = hm.group(1)
    if not WALLET.match(a.wallet.strip()) or a.wallet.strip().lower() == "0x" + "0" * 40:
        sys.exit("ERROR: alamat wallet tidak valid (0x + 40 hex).")
    comment = post_of(a.comment)
    share = post_of(a.share)
    if not comment:
        sys.exit("ERROR: link reply tidak valid (harus x.com/<kamu>/status/<id>).")
    if comment["author"].lower() != handle.lower():
        sys.exit("ERROR: link reply itu bukan dari @%s." % handle)
    if comment["id"] == TASK_POST_ID:
        sys.exit("ERROR: itu link postingan tugasnya — pakai link REPLY kamu.")
    if not share:
        sys.exit("ERROR: link postingan card tidak valid (harus x.com/<kamu>/status/<id>).")
    if share["author"].lower() != handle.lower():
        sys.exit("ERROR: link postingan card itu bukan dari @%s." % handle)
    if share["id"] == comment["id"]:
        sys.exit("ERROR: link card sama dengan link reply — pakai postingan card.")

    if not a.no_check:
        try:
            with urllib.request.urlopen(API + "?api=config", timeout=30) as r:
                cfg = json.load(r)
            if not cfg.get("open"):
                sys.exit("WHITELIST TUTUP (live API open=false). Coba lagi nanti.")
            print("Whitelist TERBUKA (live API open=true).")
        except SystemExit:
            raise
        except Exception as e:
            print("Peringatan: cek status gagal (%s), lanjut kirim..." % e)

    data = {
        "xHandle": "@" + handle,
        "followed": True, "liked": True, "reposted": True,
        "commentUrl": comment["url"],
        "wallet": a.wallet.strip(),
        "shareUrl": share["url"],
        "consent": True,
        "website": "",
    }
    print("Mengirim aplikasi @%s ..." % handle)
    req = urllib.request.Request(API, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.load(r)
    except Exception as e:
        sys.exit("ERROR kirim: %s" % e)
    print("Respons server:", json.dumps(result, ensure_ascii=False))
    if not result.get("ok"):
        sys.exit("GAGAL: %s" % result.get("error", "tidak ada pesan error"))
    if result.get("existing"):
        print("SUDAH TERDAFTAR: aplikasi wallet/username ini sudah ada. Tidak perlu lagi.")
    else:
        print("BERHASIL: aplikasi tersimpan untuk review. Spot TIDAK dijamin — pantau X @nullkin_NFT.")


if __name__ == "__main__":
    main()
