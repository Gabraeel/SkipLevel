"""Identidade visual: paleta, tipografia e utilitários de cor/recursos."""

from __future__ import annotations

import os
import sys
import tkinter.font as tkfont

import customtkinter as ctk

# Cada cor é um par (tema claro, tema escuro), formato aceito pelo CustomTkinter.
HEADER = ("#002855", "#06182F")
BG = ("#F8FAFC", "#0A192F")
SURFACE = ("#FFFFFF", "#0F2742")
SURFACE_ALT = ("#F1F5F9", "#0B1F38")
BORDER = ("#E2E8F0", "#1E3A5F")
TEXT = ("#0F172A", "#F1F5F9")
TEXT_MUTED = ("#64748B", "#94A3B8")
TEXT_FAINT = ("#94A3B8", "#56708F")
ACCENT = ("#3B82F6", "#3B82F6")
PRIMARY = ("#002855", "#3B82F6")
PRIMARY_HOVER = ("#0A3D7A", "#2563EB")
DISABLED = ("#CBD5E1", "#1E3A5F")
DISABLED_TEXT = ("#F8FAFC", "#56708F")
GOLD = ("#D97706", "#F59E0B")
GOLD_SOFT = ("#FFFBEB", "#2A2413")
SUCCESS = ("#059669", "#10B981")
DANGER = ("#DC2626", "#F87171")
ON_HEADER = "#FFFFFF"
ON_HEADER_MUTED = "#9FB3CC"

_FONT_CANDIDATES = ("Segoe UI", "Inter", "Helvetica Neue", "Helvetica", "Noto Sans", "DejaVu Sans", "Arial")
_family = "Segoe UI"


def init_fonts(root) -> None:
    """Escolhe a primeira família disponível no sistema (chamar após criar a janela)."""
    global _family
    installed = set(tkfont.families(root))
    _family = next((f for f in _FONT_CANDIDATES if f in installed), "TkDefaultFont")


def family() -> str:
    return _family


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=_family, size=size, weight=weight)


def is_dark() -> bool:
    return ctk.get_appearance_mode() == "Dark"


def pick(color) -> str:
    """Resolve um par (claro, escuro) para a cor do tema ativo."""
    if isinstance(color, (tuple, list)):
        return color[1] if is_dark() else color[0]
    return color


def blend(c1: str, c2: str, t: float) -> str:
    """Interpola entre duas cores hex (t=0 -> c1, t=1 -> c2)."""
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def ease_out_cubic(t: float) -> float:
    """Desaceleração gradual: rápido no início, suave no fim."""
    return 1 - (1 - t) ** 3


def resource_path(relative: str) -> str:
    """Caminho de um recurso, tanto em desenvolvimento quanto no .exe do PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)
