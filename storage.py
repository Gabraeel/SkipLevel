"""Persistência: guarda lista, sorteados, histórico e preferências entre execuções.

O arquivo fica na pasta de dados do usuário (no Windows, %APPDATA%\\SkipLevel),
pois o .exe de arquivo único roda a partir de uma pasta temporária.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Any

FILE_NAME = "skiplevel.json"


def data_dir() -> str:
    override = os.environ.get("SKIPLEVEL_DATA_DIR")
    if override:
        return override
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "SkipLevel")


def data_file() -> str:
    return os.path.join(data_dir(), FILE_NAME)


def load() -> dict[str, Any]:
    """Lê o estado salvo; devolve {} se não existir ou estiver corrompido."""
    try:
        with open(data_file(), encoding="utf-8") as fh:
            state = json.load(fh)
        return state if isinstance(state, dict) else {}
    except (OSError, ValueError):
        return {}


def save(state: dict[str, Any]) -> bool:
    """Grava de forma atômica (arquivo temporário + troca). Devolve se deu certo."""
    try:
        os.makedirs(data_dir(), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=data_dir(), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, data_file())
        return True
    except OSError:
        return False
