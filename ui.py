"""Janela principal do Skip Level."""

from __future__ import annotations

import sys
from datetime import datetime

import customtkinter as ctk
from PIL import Image

import theme
from data import PARTICIPANTS, WINNERS_PER_ROUND
from raffle import RaffleSession
from widgets import NameReel, WinnerCard

# Tempos da animação (segundos). Total ≈ 4,3 s de suspense.
FIRST_SPIN = 1.2      # primeira rolagem, mais longa
NEXT_SPIN = 0.55      # rolagens seguintes
HOLD = 0.18           # pausa com o nome destacado
FIRST_STRIP = 24      # nomes que passam na primeira rolagem
NEXT_STRIP = 11


class SkipLevelApp(ctk.CTk):
    def __init__(self) -> None:
        ctk.set_appearance_mode("light")
        super().__init__()
        theme.init_fonts(self)

        self.session = RaffleSession(PARTICIPANTS, WINNERS_PER_ROUND)
        self._winners: list[str] = []
        self._drawing = False
        self._drawn_at: datetime | None = None
        self._copy_job = None

        self.title("Skip Level")
        self.geometry("1120x680")
        self.minsize(1000, 640)
        self.configure(fg_color=theme.BG)
        self._set_icon()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_header()
        self._build_stats()
        self._build_main()
        self._refresh()

    # ============================================================ construção
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.HEADER, corner_radius=0, height=84)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=28)
        ctk.CTkLabel(titles, text="Skip Level", font=theme.font(26, "bold"), height=30,
                     text_color=theme.ON_HEADER).pack(anchor="w")
        ctk.CTkLabel(titles, text="Sorteio de colaboradores para conversas com a liderança",
                     font=theme.font(12), height=18, text_color=theme.ON_HEADER_MUTED).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=28)
        logo = self._load_logo()
        if logo is not None:
            ctk.CTkLabel(right, text="", image=logo).pack(side="left", padx=(0, 22))
        self.theme_btn = ctk.CTkButton(
            right, text="Tema escuro", width=112, height=32, corner_radius=16,
            font=theme.font(12, "bold"), fg_color="transparent", border_width=1,
            border_color="#35557F", hover_color="#0F3A70", text_color=theme.ON_HEADER,
            text_color_disabled="#5F7FA6", command=self._toggle_theme)
        self.theme_btn.pack(side="left")

    def _build_stats(self) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=28, pady=(20, 0))
        self._stat_values: dict[str, ctk.CTkLabel] = {}
        for i, (key, caption) in enumerate((("total", "PARTICIPANTES"), ("available", "DISPONÍVEIS"),
                                            ("per_round", "SORTEADOS POR RODADA"), ("round", "RODADA"))):
            row.grid_columnconfigure(i, weight=1, uniform="stat")
            card = ctk.CTkFrame(row, fg_color=theme.SURFACE, corner_radius=12,
                                border_width=1, border_color=theme.BORDER)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 12, 0))
            ctk.CTkLabel(card, text=caption, font=theme.font(10, "bold"), height=14,
                         text_color=theme.TEXT_MUTED).pack(anchor="w", padx=16, pady=(11, 0))
            value = ctk.CTkLabel(card, text="–", font=theme.font(22, "bold"), height=28,
                                 text_color=theme.TEXT)
            value.pack(anchor="w", padx=16, pady=(0, 10))
            self._stat_values[key] = value

    def _build_main(self) -> None:
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=2, column=0, sticky="nsew", padx=28, pady=20)
        main.grid_columnconfigure(0, weight=3, uniform="col")
        main.grid_columnconfigure(1, weight=2, uniform="col")
        main.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------- coluna do sorteio
        left = ctk.CTkFrame(main, fg_color=theme.SURFACE, corner_radius=16,
                            border_width=1, border_color=theme.BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="SORTEIO", font=theme.font(11, "bold"), height=16,
                     text_color=theme.ACCENT).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 0))

        self.reel = NameReel(left, longest_name=max(PARTICIPANTS, key=len))
        self.reel.grid(row=1, column=0, sticky="ew", padx=6, pady=(8, 0))

        self.status = ctk.CTkLabel(left, text="", font=theme.font(13), text_color=theme.TEXT_MUTED)
        self.status.grid(row=2, column=0, sticky="n", pady=(6, 0))

        self.no_repeat = ctk.CTkSwitch(
            left, text="Não repetir quem já foi sorteado", font=theme.font(12),
            text_color=theme.TEXT_MUTED, progress_color=theme.ACCENT, command=self._on_toggle_repeat)
        self.no_repeat.select()
        self.no_repeat.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 14))

        actions = ctk.CTkFrame(left, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))
        actions.grid_columnconfigure(0, weight=1)
        self.draw_btn = ctk.CTkButton(
            actions, text="Iniciar Sorteio", height=50, corner_radius=12, font=theme.font(16, "bold"),
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER, text_color="#FFFFFF",
            text_color_disabled=theme.DISABLED_TEXT, command=self.start_draw)
        self.draw_btn.grid(row=0, column=0, sticky="ew")
        self.reset_btn = self._secondary_button(actions, "Reiniciar", self._reset, width=120, height=50)
        self.reset_btn.grid(row=0, column=1, padx=(12, 0))

        # -------------------------------------------- coluna de resultados
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(right, text="Sorteados da rodada", font=theme.font(16, "bold"), height=22,
                     text_color=theme.TEXT).grid(row=0, column=0, sticky="w", pady=(2, 10))
        self.cards = [WinnerCard(right, i + 1) for i in range(WINNERS_PER_ROUND)]
        for i, card in enumerate(self.cards):
            card.grid(row=i + 1, column=0, sticky="ew", pady=(0, 8))

        self.copy_btn = self._secondary_button(right, "Copiar Lista de Vencedores", self._copy, height=44)
        self.copy_btn.grid(row=7, column=0, sticky="ew")

    def _secondary_button(self, master, text, command, **kwargs) -> ctk.CTkButton:
        return ctk.CTkButton(
            master, text=text, corner_radius=12, font=theme.font(13, "bold"),
            fg_color="transparent", border_width=1, border_color=theme.BORDER,
            hover_color=theme.SURFACE_ALT, text_color=theme.TEXT,
            text_color_disabled=theme.TEXT_FAINT, command=command, **kwargs)

    # =============================================================== recursos
    def _load_logo(self) -> ctk.CTkImage | None:
        """Carrega o logotipo e gera uma versão branca para o cabeçalho azul."""
        try:
            src = Image.open(theme.resource_path("assets/logo.png")).convert("RGBA")
        except OSError:
            return None
        alpha = src.getchannel("A")
        if alpha.getextrema()[0] == 255:
            # Imagem sem transparência (fundo preto): o brilho vira a máscara.
            lum = Image.merge("RGB", src.split()[:3]).convert("L")
            top = max(1, lum.getextrema()[1])
            alpha = lum.point(lambda v: min(255, int(v * 255 / top)))
        white = Image.new("RGBA", src.size, (255, 255, 255, 0))
        white.putalpha(alpha)
        height = 22
        return ctk.CTkImage(light_image=white, dark_image=white,
                            size=(round(src.width * height / src.height), height))

    def _set_icon(self) -> None:
        if sys.platform.startswith("win"):
            try:
                self.iconbitmap(theme.resource_path("assets/icon.ico"))
            except Exception:
                pass  # ícone é opcional

    # ================================================================ sorteio
    def start_draw(self) -> None:
        if self._drawing or not self.session.can_draw():
            return
        self._winners = self.session.draw()   # o resultado é definido aqui; a animação só o revela
        self._drawn_at = datetime.now()
        self._drawing = True
        for card in self.cards:
            card.clear()
        self._refresh()
        self._spin_stage(0)

    def _spin_stage(self, index: int) -> None:
        if index >= len(self._winners):
            self._finish()
            return
        winner = self._winners[index]
        self.status.configure(text=f"Sorteando o {index + 1}º nome…", text_color=theme.TEXT_MUTED)
        count = FIRST_STRIP if index == 0 else NEXT_STRIP
        strip = self.session.filler_names(count, exclude=winner)
        if self.reel.current:                 # continua a partir do nome que está na tela
            strip[0] = self.reel.current
        strip.append(winner)
        strip.append(self.session.filler_names(1, exclude=winner)[0])  # vizinho abaixo do vencedor
        self.reel.spin(strip, FIRST_SPIN if index == 0 else NEXT_SPIN,
                       on_done=lambda: self._on_landed(index))

    def _on_landed(self, index: int) -> None:
        self.cards[index].reveal(self._winners[index])
        self.after(int(HOLD * 1000), lambda: self._spin_stage(index + 1))

    def _finish(self) -> None:
        self._drawing = False
        self.status.configure(
            text=f"Sorteio concluído · {self._drawn_at:%d/%m/%Y às %H:%M}", text_color=theme.SUCCESS)
        self._refresh()

    # ================================================================== ações
    def _copy(self) -> None:
        if not self._winners:
            return
        lines = [f"Skip Level – Sorteados ({self._drawn_at:%d/%m/%Y %H:%M})"]
        lines += [f"{i}º {name}" for i, name in enumerate(self._winners, start=1)]
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.update()  # garante que o conteúdo permaneça na área de transferência
        self.copy_btn.configure(text="Lista copiada ✓", text_color=theme.SUCCESS)
        if self._copy_job is not None:
            self.after_cancel(self._copy_job)
        self._copy_job = self.after(1800, self._restore_copy_label)

    def _restore_copy_label(self) -> None:
        self._copy_job = None
        self.copy_btn.configure(text="Copiar Lista de Vencedores", text_color=theme.TEXT)

    def _reset(self) -> None:
        """Volta ao estado inicial: todos concorrem novamente."""
        self.session.reset()
        self._winners = []
        for card in self.cards:
            card.clear()
        self.reel.show_message("Pronto para o sorteio")
        self._refresh()

    def _on_toggle_repeat(self) -> None:
        self.session.exclude_drawn = bool(self.no_repeat.get())
        self._refresh()

    def _toggle_theme(self) -> None:
        dark = not theme.is_dark()
        ctk.set_appearance_mode("dark" if dark else "light")
        self.theme_btn.configure(text="Tema claro" if dark else "Tema escuro")
        self.reel.apply_theme()

    # ================================================================= estado
    def _refresh(self) -> None:
        """Sincroniza indicadores, textos e estados dos botões com a sessão."""
        s = self.session
        available = len(s.available())
        self._stat_values["total"].configure(text=str(s.total))
        self._stat_values["available"].configure(text=str(available))
        self._stat_values["per_round"].configure(text=str(s.winners_per_round))
        self._stat_values["round"].configure(text=str(s.rounds) if s.rounds else "–")

        idle = not self._drawing
        can_draw = idle and s.can_draw()
        self.draw_btn.configure(
            text="Sorteando…" if self._drawing else ("Sortear Novamente" if s.rounds else "Iniciar Sorteio"),
            state="normal" if can_draw else "disabled",
            fg_color=theme.PRIMARY if can_draw else theme.DISABLED)
        self.copy_btn.configure(state="normal" if idle and self._winners else "disabled")
        self.reset_btn.configure(state="normal" if idle and s.rounds else "disabled")
        self.no_repeat.configure(state="normal" if idle else "disabled")
        self.theme_btn.configure(state="normal" if idle else "disabled")

        if idle and not s.can_draw():
            self.status.configure(
                text=f"Restam {available} participantes disponíveis. Reinicie ou permita repetições.",
                text_color=theme.GOLD)
        elif idle and not self._winners:
            self.reel.show_message("Pronto para o sorteio")
            self.status.configure(text=f"{s.total} participantes carregados", text_color=theme.TEXT_MUTED)
        elif idle and self._drawn_at:
            self.status.configure(
                text=f"Sorteio concluído · {self._drawn_at:%d/%m/%Y às %H:%M}", text_color=theme.SUCCESS)
