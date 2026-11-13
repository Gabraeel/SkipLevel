"""Componentes visuais: roleta de nomes (slot machine) e card de sorteado."""

from __future__ import annotations

import math
import time
import tkinter as tk
import tkinter.font as tkfont
from typing import Callable, Sequence

import customtkinter as ctk

import theme

FRAME_MS = 15  # ~60 quadros por segundo


class NameReel(tk.Canvas):
    """Roleta vertical de nomes com desaceleração gradual.

    A animação é guiada pelo relógio (`perf_counter`) e por `after`, de modo
    que a janela nunca trava e a duração é a mesma em qualquer máquina.
    """

    def __init__(self, master, longest_name: str, base_height: int = 210) -> None:
        self._scale = ctk.ScalingTracker.get_widget_scaling(master)
        self._ch = int(base_height * self._scale)
        self._row_h = int(64 * self._scale)
        super().__init__(master, height=self._ch, highlightthickness=0, bd=0)

        self._longest = longest_name
        self._font = tkfont.Font(family=theme.family(), size=-int(22 * self._scale), weight="bold")
        self._cw = 600

        self._strip: list[str] = [""]
        self._pos = 0.0
        self._landed = False       # nome central destacado em dourado
        self._message = True       # exibindo mensagem (não um nome)
        self._job = None

        self._line_top = self.create_line(0, 0, 0, 0, width=max(1, int(2 * self._scale)))
        self._line_bot = self.create_line(0, 0, 0, 0, width=max(1, int(2 * self._scale)))
        self._mark_l = self.create_polygon(0, 0, 0, 0, 0, 0)
        self._mark_r = self.create_polygon(0, 0, 0, 0, 0, 0)
        self._texts = [self.create_text(0, 0, text="", font=self._font) for _ in range(5)]

        self.bind("<Configure>", self._on_resize)
        self.apply_theme()

    # -------------------------------------------------------------- pública
    @property
    def current(self) -> str | None:
        """Nome atualmente no centro (None se for uma mensagem)."""
        return None if self._message else self._strip[int(round(self._pos))]

    def show_message(self, text: str) -> None:
        self._cancel()
        self._strip, self._pos = [text], 0.0
        self._landed, self._message = False, True
        self._render()

    def spin(self, strip: Sequence[str], duration: float, on_done: Callable[[], None]) -> None:
        """Rola de strip[0] até strip[-2] em `duration` segundos.

        O último item é apenas o vizinho exibido abaixo do nome final.
        """
        self._cancel()
        self._strip, self._pos = list(strip), 0.0
        self._landed, self._message = False, False
        start = time.perf_counter()
        last = len(self._strip) - 2

        def tick() -> None:
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - start) / duration)
            self._pos = last * theme.ease_out_cubic(t)
            if t >= 1.0:
                self._job = None
                self._landed = True
                self._render()
                on_done()
                return
            self._render()
            self._job = self.after(FRAME_MS, tick)

        tick()

    def apply_theme(self) -> None:
        self._bg = theme.pick(theme.SURFACE)
        self.configure(bg=self._bg)
        accent = theme.pick(theme.ACCENT)
        for item in (self._line_top, self._line_bot, self._mark_l, self._mark_r):
            self.itemconfigure(item, fill=accent)
        self._render()

    # ------------------------------------------------------------- internas
    def _cancel(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def _on_resize(self, event) -> None:
        self._cw = event.width
        # Ajusta a fonte para que o nome mais longo sempre caiba.
        margin = int(90 * self._scale)
        for size in range(24, 11, -1):
            self._font.configure(size=-int(size * self._scale))
            if self._font.measure(self._longest) <= self._cw - margin:
                break
        cy, half, m = self._ch / 2, self._row_h / 2, int(9 * self._scale)
        pad = int(22 * self._scale)
        self.coords(self._line_top, pad, cy - half, self._cw - pad, cy - half)
        self.coords(self._line_bot, pad, cy + half, self._cw - pad, cy + half)
        self.coords(self._mark_l, pad, cy - m, pad + m, cy, pad, cy + m)
        self.coords(self._mark_r, self._cw - pad, cy - m, self._cw - pad - m, cy, self._cw - pad, cy + m)
        self._render()

    def _render(self) -> None:
        cx, cy = self._cw / 2, self._ch / 2
        if self._message:
            base = theme.pick(theme.TEXT_MUTED)
        else:
            base = theme.pick(theme.TEXT)
        gold = theme.pick(theme.GOLD)
        first = math.floor(self._pos) - 2
        for k, item in enumerate(self._texts):
            idx = first + k
            if 0 <= idx < len(self._strip):
                dist = abs(idx - self._pos)
                color = theme.blend(base, self._bg, min(1.0, dist / 1.45))
                if self._landed and dist < 0.01:
                    color = gold
                self.coords(item, cx, cy + (idx - self._pos) * self._row_h)
                self.itemconfigure(item, text=self._strip[idx], fill=color, state="normal")
            else:
                self.itemconfigure(item, state="hidden")


class WinnerCard(ctk.CTkFrame):
    """Card de um sorteado, com posição (1º a 5º) e revelação em fade-in."""

    FADE_MS = 420

    def __init__(self, master, position: int) -> None:
        super().__init__(master, corner_radius=12, border_width=1,
                         fg_color=theme.SURFACE, border_color=theme.BORDER)
        self._position = position
        self._job = None
        self.grid_columnconfigure(1, weight=1)

        self._badge = ctk.CTkLabel(self, text=f"{position}º", width=38, height=38, corner_radius=19,
                                   font=theme.font(14, "bold"),
                                   fg_color=theme.SURFACE_ALT, text_color=theme.TEXT_FAINT)
        self._badge.grid(row=0, column=0, rowspan=2, padx=(14, 12), pady=10)

        self._caption = ctk.CTkLabel(self, text=f"{position}º SORTEADO", height=14, anchor="w",
                                     font=theme.font(10, "bold"), text_color=theme.TEXT_FAINT)
        self._caption.grid(row=0, column=1, sticky="sw", pady=(10, 0))

        self._name = ctk.CTkLabel(self, text="Aguardando sorteio", anchor="w", justify="left",
                                  wraplength=290, font=theme.font(13, "bold"),
                                  text_color=theme.TEXT_FAINT)
        self._name.grid(row=1, column=1, sticky="nw", padx=(0, 12), pady=(0, 10))

    def clear(self) -> None:
        self._stop()
        self.configure(fg_color=theme.SURFACE, border_color=theme.BORDER)
        self._badge.configure(fg_color=theme.SURFACE_ALT, text_color=theme.TEXT_FAINT)
        self._caption.configure(text_color=theme.TEXT_FAINT)
        self._name.configure(text="Aguardando sorteio", text_color=theme.TEXT_FAINT)

    def reveal(self, name: str) -> None:
        """Mostra o nome com transição suave do estado neutro para o destaque."""
        self._stop()
        self._name.configure(text=name)
        p = theme.pick
        surface, soft, gold = p(theme.SURFACE), p(theme.GOLD_SOFT), p(theme.GOLD)
        border, alt, faint, text = p(theme.BORDER), p(theme.SURFACE_ALT), p(theme.TEXT_FAINT), p(theme.TEXT)
        start = time.perf_counter()

        def tick() -> None:
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - start) * 1000 / self.FADE_MS)
            e = theme.ease_out_cubic(t)
            if t >= 1.0:
                # Estado final em pares (claro, escuro): acompanha a troca de tema.
                self._job = None
                self.configure(fg_color=theme.GOLD_SOFT, border_color=theme.GOLD)
                self._badge.configure(fg_color=theme.GOLD, text_color="#FFFFFF")
                self._caption.configure(text_color=theme.GOLD)
                self._name.configure(text_color=theme.TEXT)
                return
            self.configure(fg_color=theme.blend(surface, soft, e), border_color=theme.blend(border, gold, e))
            self._badge.configure(fg_color=theme.blend(alt, gold, e), text_color=theme.blend(faint, "#FFFFFF", e))
            self._caption.configure(text_color=theme.blend(faint, gold, e))
            self._name.configure(text_color=theme.blend(surface, text, e))
            self._job = self.after(FRAME_MS * 2, tick)

        tick()

    def _stop(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
