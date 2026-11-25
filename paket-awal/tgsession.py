#!/usr/bin/env python3
"""Loader sesi Telethon armada — `available_accounts()` + `load_session()`.

Modul ini hilang dari checkout; kontraknya diambil dari 22 skrip yang memakainya:

    from tgsession import available_accounts, load_session
    for name in sorted(available_accounts()):
        client = TelegramClient(load_session(name), *cred_resolve(name))

Aturan yang dipakai (sama seperti rutin lama):
  * Berkas sesi dicari di `session/`, `hatake_sessions/`, lalu `sessions/`
    (folder pertama yang memuat `.session` menang; `TG_SESSION_DIR` menimpanya).
  * Nama akun = nama berkas tanpa `.session` (`Sakura.session` -> `Sakura`).
    Berkas `.session-journal` (SQLite) dan berkas berawalan `.` diabaikan.
  * DUA bentuk sesi didukung, dibedakan dari isi berkasnya:
      - SQLite Telethon (`session/Sakura.session`) -> dikembalikan sebagai PATH;
      - StringSession base64 (`hatake_sessions/Sakura.session`) -> dikembalikan
        sebagai objek `StringSession`.
    Keduanya langsung bisa dipakai `TelegramClient(load_session(name), api_id, api_hash)`.
  * Berkas tidak harus ada saat modul diimpor, jadi `--list`/`status` tetap bisa
    jalan di checkout tanpa sesi.
"""

import base64
import binascii
import hashlib
import os
import re
import sqlite3
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_ENV = "TG_SESSION_DIR"
CANDIDATES = ("session", "hatake_sessions", "sessions")
SQLITE_MAGIC = b"SQLite format 3\x00"
IPV4_RE = re.compile(rb"(\d{1,3}(?:\.\d{1,3}){3})")
DEFAULT_PORT = 443


class SessionError(FileNotFoundError):
    """Sesi tidak ditemukan atau tidak bisa dipakai."""


def session_dirs():
    """-> daftar folder yang benar-benar ada (env dulu, lalu bawaan)."""
    out = []
    env = os.environ.get(DIR_ENV)
    if env:
        out.append(Path(env).expanduser())
    out.extend(ROOT / name for name in CANDIDATES)
    return [path for path in out if path.is_dir()]


def session_dir():
    """-> folder sesi utama (yang memuat `.session`); None kalau tidak ada."""
    for folder in session_dirs():
        if any(folder.glob("*.session")):
            return folder
    dirs = session_dirs()
    return dirs[0] if dirs else None


def available_accounts():
    """-> nama akun (str) yang punya berkas `.session`, urut abjad, tanpa duplikat."""
    seen = {}
    for folder in session_dirs():
        for path in sorted(folder.glob("*.session")):
            if path.name.startswith("."):
                continue
            seen.setdefault(path.stem, path)
    return sorted(seen)


def session_path(name):
    """-> Path berkas sesi akun `name` (tanpa perlu berkasnya ada)."""
    clean = name[:-8] if name.endswith(".session") else name
    if not clean or clean.startswith(".") or "/" in clean or "\\" in clean:
        raise SessionError(f"nama akun tidak valid: {name!r}")
    for folder in session_dirs():
        path = folder / f"{clean}.session"
        if path.exists():
            return path
    folder = session_dir() or (ROOT / "session")
    return folder / f"{clean}.session"


def _armada_string_session(text):
    """Urai format sesi string armada (`hatake_sessions/*.session`).

    Bentuknya: `"1" + base64(dc_id | panjang | IP ASCII | ... | auth_key)`,
    auth_key selalu 256 byte TERAKHIR (diverifikasi ke Telegram: akun asli
    terbaca). Port selalu 443. Bukan `StringSession` Telethon standar.
    """
    from telethon.crypto import AuthKey                        # noqa: PLC0415
    from telethon.sessions import StringSession                 # noqa: PLC0415

    raw = base64.urlsafe_b64decode(text[1:] + "=" * (-len(text[1:]) % 4))
    if len(raw) < 257:
        raise SessionError(f"sesi string terlalu pendek ({len(raw)} byte)")
    match = IPV4_RE.search(raw)
    if not match:
        raise SessionError("sesi string tanpa alamat IP")
    session = StringSession()
    session.set_dc(raw[0] or 2, match.group(1).decode(), DEFAULT_PORT)
    session._auth_key = AuthKey(raw[-256:])
    return session


def session_auth_key(name):
    """-> 256 byte auth key sesi (TIDAK dicetak; dipakai untuk sidik jari).

    Dua berkas bisa menunjuk kredensial yang sama (mis. `Pejurup.session` string
    = `Naruto.session` SQLite). Memakai keduanya berbarengan membuat
    Telegram mematikan salah satu klien (`401`), jadi pemanggil perlu tahu.
    """
    path = session_path(name)
    if not path.exists():
        raise SessionError(f"sesi {path.name} tidak ada")
    with open(path, "rb") as fh:
        head = fh.read(len(SQLITE_MAGIC))
    if head == SQLITE_MAGIC:
        try:
            con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            try:
                row = con.execute("select auth_key from sessions").fetchone()
            finally:
                con.close()
        except sqlite3.Error as e:
            raise SessionError(f"sesi {path.name} tidak terbaca: {e}")
        key = (row[0] if row else b"") or b""
    else:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        try:
            raw = base64.urlsafe_b64decode(text[1:] + "=" * (-len(text[1:]) % 4))
        except (binascii.Error, ValueError) as e:
            raise SessionError(f"sesi {path.name} tidak terbaca: {e}")
        key = raw[-256:]
    if len(key) != 256:
        raise SessionError(f"sesi {path.name}: auth key {len(key)} byte (harus 256)")
    return key


def auth_fingerprint(name):
    """-> sidik jari 16 hex dari auth key (aman dilog, tanpa membocorkan kunci)."""
    return hashlib.sha256(session_auth_key(name)).hexdigest()[:16]


def load_session(name):
    """-> sesi siap pakai untuk `TelegramClient` (path SQLite atau sesi string)."""
    path = session_path(name)
    if not path.exists():
        dirs = ", ".join(str(d) for d in session_dirs()) or "(tidak ada folder sesi)"
        raise SessionError(f"sesi {path.name} tidak ada di {dirs}")
    if path.stat().st_size == 0:
        raise SessionError(f"sesi {path.name} kosong (0 byte)")
    with open(path, "rb") as fh:
        head = fh.read(len(SQLITE_MAGIC))
    if head == SQLITE_MAGIC:
        return str(path)

    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text or "\n" in text or " " in text or len(text) < 80:
        raise SessionError(f"sesi {path.name} bukan SQLite Telethon maupun sesi string")
    from telethon.sessions import StringSession              # noqa: PLC0415
    try:                                                       # format Telethon resmi
        return StringSession(text)
    except (ValueError, TypeError, struct.error, binascii.Error):
        return _armada_string_session(text)


if __name__ == "__main__":
    names = available_accounts()
    print(f"folder sesi: {session_dir() or '-'}")
    print(f"{len(names)} akun: {', '.join(names) if names else '(kosong)'}")
