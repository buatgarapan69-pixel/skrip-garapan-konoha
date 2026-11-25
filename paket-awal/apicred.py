#!/usr/bin/env python3
"""Robust session loader + credential resolver for the armada routers.

Handles missing/corrupt session files gracefully, enumerates sessions,
and resolves per-account Telegram credentials (api_id / api_hash).

Loads, in priority order:
  1. per-account entries in session/apicred.json        {"akun": {"<nama>": {…}}}
  2. defaults in session/apicred.json                   {"default": {…}}
  3. top-level keys in session/apicred.json             {"api_id": …, "api_hash": …}
  4. environment variables TG_API_ID / TG_API_HASH (both required)
  5. session/.api_id + session/.api_hash (both required)

`api_id` adalah angka (mis. 12345678) dan `api_hash` 32 karakter hex; keduanya
divalidasi terpisah — menukar keduanya hanya membuat Telegram menolak sesi.
Any failure is reported via log() — never a traceback that kills cron.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APICRED = ROOT / "session" / "apicred.json"
API_ID_FILE = ROOT / "session" / ".api_id"
API_HASH_FILE = ROOT / "session" / ".api_hash"

HEX_DIGITS = set("0123456789abcdefABCDEF")


def log(msg: str) -> None:
    print(f"[apicred] {msg}", flush=True)


def _as_id(value) -> int:
    """-> api_id positif (int); `ValueError` kalau bukan angka."""
    text = str(value if value is not None else "").strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValueError(f"api_id harus angka positif, bukan {value!r}")
    return int(text)


def _as_hex32(value) -> str:
    """-> api_hash 32 karakter hex; `ValueError` kalau bentuknya salah."""
    text = str(value if value is not None else "").strip()
    if len(text) != 32 or any(c not in HEX_DIGITS for c in text):
        raise ValueError(f"api_hash harus 32 karakter hex, bukan {value!r}")
    return text


def _pair(entry) -> tuple[int, str]:
    """-> (api_id, api_hash) dari satu entri; `ValueError` kalau tidak lengkap."""
    if not isinstance(entry, dict):
        raise ValueError("entri kredensial bukan objek")
    return _as_id(entry.get("api_id")), _as_hex32(entry.get("api_hash"))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def load_apicred() -> dict:
    try:
        data = json.loads(APICRED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _accounts(data: dict) -> dict:
    akun = data.get("akun")
    return akun if isinstance(akun, dict) else {}


def _from_json(account: str | None, data: dict) -> tuple[int, str] | None:
    """Cari pasangan di apicred.json (akun -> default -> kunci tingkat atas)."""
    akun = _accounts(data)
    if account and account in akun:
        return _pair(akun[account])
    if isinstance(data.get("default"), dict):
        return _pair(data["default"])
    if data.get("api_id") or data.get("api_hash"):
        return _pair(data)
    return None


def resolve(account: str | None = None,
            api_id: int | None = None,
            api_hash: str | None = None) -> tuple[int, str]:
    """-> (api_id: int, api_hash: str) sesuai urutan prioritas di atas."""
    if api_id is not None or api_hash is not None:
        if api_id is None or api_hash is None:
            raise ValueError("api_id dan api_hash harus diberikan bersama")
        return _as_id(api_id), _as_hex32(api_hash)

    data = load_apicred()
    try:
        pair = _from_json(account, data)
    except ValueError as e:
        raise ValueError(f"kredensial di {APICRED.name} tidak valid: {e}") from e
    if pair:
        return pair

    env_id = os.environ.get("TG_API_ID")
    env_hash = os.environ.get("TG_API_HASH")
    if env_id and env_hash:
        return _as_id(env_id), _as_hex32(env_hash)

    id_txt = _read_text(API_ID_FILE)
    hash_txt = _read_text(API_HASH_FILE)
    if id_txt and hash_txt:
        return _as_id(id_txt), _as_hex32(hash_txt)

    akun = _accounts(data)
    log(f"akun '{account or '<default>'}' tidak ditemukan — pakai akun pertama")
    if akun:
        first = sorted(akun)[0]
        try:
            return _pair(akun[first])
        except ValueError as e:
            raise ValueError(f"kredensial akun '{first}' tidak valid: {e}") from e

    raise RuntimeError(
        "kredensial Telegram belum ada — isi session/apicred.json "
        "({\"default\": {\"api_id\": …, \"api_hash\": \"…\"}}), setel env "
        "TG_API_ID + TG_API_HASH, atau tulis session/.api_id + session/.api_hash"
    )


def get_api_id(account: str | None = None) -> int:
    """-> api_id (angka) untuk `account`, atau default yang berlaku."""
    return resolve(account)[0]


def get_api_hash(account: str | None = None) -> str:
    """-> api_hash (32 hex) untuk `account`, atau default yang berlaku."""
    return resolve(account)[1]


def list_accounts() -> list[str]:
    try:
        return sorted(_accounts(load_apicred()))
    except Exception:                       # noqa: BLE001 - daftar saja, jangan matikan pemanggil
        return []


if __name__ == "__main__":
    try:
        api_id, api_hash = resolve()
    except (ValueError, RuntimeError) as e:
        raise SystemExit(f"GAGAL: {e}")
    accounts = list_accounts()
    print(f"api_id    : {api_id}")
    print(f"api_hash  : {api_hash[:4]}…{api_hash[-4:]} (32 hex)")
    print(f"akun      : {len(accounts)}" + (f" — {', '.join(accounts)}" if accounts else ""))
