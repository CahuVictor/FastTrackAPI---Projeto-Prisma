# app/utils/git_info.py
from __future__ import annotations
import subprocess


def get_git_sha(short: bool = True) -> str:
    """
    Retorna o hash do commit atual.
    • short=True  →  7 chars  (git rev-parse --short HEAD)
    • short=False →  40 chars (git rev-parse HEAD)
    Se algo der errado (repositório sem .git, etc.) devolve 'unknown'.
    """
    try:
        cmd = ["git", "rev-parse", "--short" if short else "HEAD"]
        return (
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"
