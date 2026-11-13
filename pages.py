"""Abas secundárias: edição de participantes e histórico de sorteios."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

import theme
from raffle import normalize_name


def card(master, **kwargs) -> ctk.CTkFrame:
    return ctk.CTkFrame(master, fg_color=theme.SURFACE, corner_radius=16,
                        border_width=1, border_color=theme.BORDER, **kwargs)


def primary_button(master, text, command, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=text, corner_radius=12, font=theme.font(13, "bold"),
        fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER, text_color="#FFFFFF",
        text_color_disabled=theme.DISABLED_TEXT, command=command, **kwargs)


def secondary_button(master, text, command, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=text, corner_radius=12, font=theme.font(13, "bold"),
        fg_color="transparent", border_width=1, border_color=theme.BORDER,
        hover_color=theme.SURFACE_ALT, text_color=theme.TEXT,
        text_color_disabled=theme.TEXT_FAINT, command=command, **kwargs)


def format_when(iso: str) -> str:
    try:
        return f"{datetime.fromisoformat(iso):%d/%m/%Y às %H:%M}"
    except (TypeError, ValueError):
        return "Data desconhecida"


class ParticipantsPage(ctk.CTkFrame):
    """Lista editável: adicionar, remover (com desfazer), buscar e restaurar."""

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._undo: tuple[str, bool] | None = None   # (nome, já tinha sido sorteado)
        self.grid_columnconfigure(0, weight=3, uniform="col")
        self.grid_columnconfigure(1, weight=2, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        # ------------------------------------------------------------- lista
        left = card(self)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        self.title = ctk.CTkLabel(left, text="", font=theme.font(16, "bold"), text_color=theme.TEXT)
        self.title.grid(row=0, column=0, sticky="w", padx=24, pady=(18, 8))
        self.search = ctk.CTkEntry(left, placeholder_text="Buscar nome…", width=220, height=34,
                                   corner_radius=10, border_width=1, border_color=theme.BORDER,
                                   fg_color=theme.SURFACE_ALT, text_color=theme.TEXT,
                                   font=theme.font(12))
        self.search.grid(row=0, column=1, sticky="e", padx=24, pady=(18, 8))
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        self.rows = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.rows.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 14))
        self.rows.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------------------ edição
        right = card(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(right, text="ADICIONAR PESSOA", font=theme.font(11, "bold"), height=16,
                     text_color=theme.ACCENT).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 8))
        self.entry = ctk.CTkEntry(right, placeholder_text="Nome completo", height=42,
                                  corner_radius=10, border_width=1, border_color=theme.BORDER,
                                  fg_color=theme.SURFACE_ALT, text_color=theme.TEXT,
                                  font=theme.font(13))
        self.entry.grid(row=1, column=0, sticky="ew", padx=24)
        self.entry.bind("<Return>", lambda _e: self._add())
        primary_button(right, "Adicionar", self._add, height=42).grid(
            row=2, column=0, sticky="ew", padx=24, pady=(10, 0))

        self.feedback = ctk.CTkLabel(right, text="", font=theme.font(12), wraplength=300,
                                     justify="left", anchor="w", text_color=theme.TEXT_MUTED)
        self.feedback.grid(row=3, column=0, sticky="ew", padx=24, pady=(12, 0))
        self.undo_btn = secondary_button(right, "Desfazer remoção", self._undo_remove, height=34)

        ctk.CTkLabel(right, font=theme.font(11), wraplength=300, justify="left", anchor="w",
                     text_color=theme.TEXT_FAINT,
                     text="Para vários nomes de uma vez, separe com ponto e vírgula. "
                          "As alterações são salvas automaticamente neste computador."
                     ).grid(row=6, column=0, sticky="ew", padx=24, pady=(0, 12))
        secondary_button(right, "Restaurar lista original", self._restore_defaults, height=42).grid(
            row=7, column=0, sticky="ew", padx=24, pady=(0, 24))

        self.refresh()

    # ------------------------------------------------------------------ lista
    def refresh(self) -> None:
        session = self.app.session
        query = normalize_name(self.search.get())
        names = sorted(n for n in session.participants if query in n)
        self.title.configure(text=f"Participantes · {session.total}")

        for child in self.rows.winfo_children():
            child.destroy()
        if not names:
            text = "Nenhum nome encontrado." if session.total else "A lista está vazia. Adicione pessoas ao lado."
            ctk.CTkLabel(self.rows, text=text, font=theme.font(13),
                         text_color=theme.TEXT_MUTED).grid(row=0, column=0, pady=40)
            return
        for i, name in enumerate(names):
            row = ctk.CTkFrame(self.rows, fg_color=theme.SURFACE_ALT, corner_radius=10)
            row.grid(row=i, column=0, sticky="ew", pady=(0, 6))
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=name, anchor="w", font=theme.font(12, "bold"),
                         text_color=theme.TEXT).grid(row=0, column=0, sticky="w", padx=14, pady=7)
            if session.was_drawn(name):
                ctk.CTkLabel(row, text="JÁ SORTEADO", font=theme.font(10, "bold"),
                             text_color=theme.GOLD).grid(row=0, column=1, padx=(0, 12))
            ctk.CTkButton(row, text="Remover", width=78, height=26, corner_radius=8,
                          font=theme.font(11, "bold"), fg_color="transparent", border_width=1,
                          border_color=theme.BORDER, hover_color=theme.SURFACE,
                          text_color=theme.DANGER,
                          command=lambda n=name: self._remove(n)).grid(row=0, column=2, padx=(0, 10))

    def _say(self, text: str, color=theme.TEXT_MUTED, undo: bool = False) -> None:
        self.feedback.configure(text=text, text_color=color)
        if undo:
            self.undo_btn.grid(row=4, column=0, sticky="w", padx=24, pady=(8, 0))
        else:
            self._undo = None
            self.undo_btn.grid_remove()

    # ------------------------------------------------------------------ ações
    def _add(self) -> None:
        parts = [p for p in self.entry.get().replace("\n", ";").split(";") if p.strip()]
        if not parts:
            self._say("Digite um nome.", theme.DANGER)
            return
        added, errors = [], []
        for raw in parts:
            try:
                added.append(self.app.session.add(raw))
            except ValueError as exc:
                errors.append(str(exc))
        if added:
            self.entry.delete(0, "end")
            self.app.participants_changed()
            self.refresh()
        if errors:
            prefix = f"{len(added)} adicionado(s). " if added else ""
            self._say(prefix + " ".join(errors), theme.DANGER)
        elif len(added) == 1:
            self._say(f"{added[0]} adicionado(a).", theme.SUCCESS)
        else:
            self._say(f"{len(added)} pessoas adicionadas.", theme.SUCCESS)

    def _remove(self, name: str) -> None:
        was_drawn = self.app.session.remove(name)
        self.app.participants_changed()
        self.refresh()
        self._undo = (name, was_drawn)
        self._say(f"{name} removido(a).", undo=True)
        self._undo = (name, was_drawn)

    def _undo_remove(self) -> None:
        if self._undo is None:
            return
        name, was_drawn = self._undo
        self.app.session.restore(name, was_drawn)
        self.app.participants_changed()
        self.refresh()
        self._say(f"{name} voltou para a lista.", theme.SUCCESS)

    def _restore_defaults(self) -> None:
        if messagebox.askyesno(
                "Restaurar lista original",
                "A lista volta aos participantes originais do aplicativo. "
                "As pessoas que você adicionou serão removidas.\n\nContinuar?", parent=self):
            self.app.restore_default_participants()
            self.refresh()
            self._say("Lista original restaurada.", theme.SUCCESS)


class HistoryPage(ctk.CTkFrame):
    """Sorteios anteriores, do mais recente para o mais antigo."""

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._copy_job = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkLabel(top, text="", font=theme.font(16, "bold"), text_color=theme.TEXT)
        self.title.grid(row=0, column=0, sticky="w")
        self.copy_btn = secondary_button(top, "Copiar histórico", self._copy, width=160, height=38)
        self.copy_btn.grid(row=0, column=1, padx=(0, 10))
        self.clear_btn = secondary_button(top, "Limpar histórico", self._clear, width=160, height=38)
        self.clear_btn.grid(row=0, column=2)

        self.rows = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.rows.grid(row=1, column=0, sticky="nsew")
        self.rows.grid_columnconfigure((0, 1), weight=1, uniform="h")
        self.refresh()

    def refresh(self) -> None:
        history = self.app.history
        self.title.configure(text=f"Histórico · {len(history)} sorteio(s)")
        state = "normal" if history else "disabled"
        self.copy_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        for child in self.rows.winfo_children():
            child.destroy()
        if not history:
            ctk.CTkLabel(self.rows, text="Nenhum sorteio realizado ainda.", font=theme.font(13),
                         text_color=theme.TEXT_MUTED).grid(row=0, column=0, columnspan=2, pady=60)
            return
        for i, entry in enumerate(reversed(history)):
            box = card(self.rows)
            box.grid(row=i // 2, column=i % 2, sticky="nsew", padx=(0, 12), pady=(0, 12))
            ctk.CTkLabel(box, text=f"SORTEIO {len(history) - i} · {format_when(entry.get('at'))}",
                         font=theme.font(11, "bold"), height=16,
                         text_color=theme.ACCENT).pack(anchor="w", padx=18, pady=(14, 6))
            names = "\n".join(f"{n}º  {w}" for n, w in enumerate(entry.get("winners", []), start=1))
            ctk.CTkLabel(box, text=names, justify="left", anchor="w", font=theme.font(12, "bold"),
                         text_color=theme.TEXT).pack(anchor="w", padx=18, pady=(0, 14))

    def as_text(self) -> str:
        blocks = []
        for i, entry in enumerate(self.app.history, start=1):
            lines = [f"Sorteio {i} – {format_when(entry.get('at'))}"]
            lines += [f"{n}º {w}" for n, w in enumerate(entry.get("winners", []), start=1)]
            blocks.append("\n".join(lines))
        return "Skip Level – Histórico de sorteios\n\n" + "\n\n".join(blocks)

    def _copy(self) -> None:
        self.app.copy_text(self.as_text())
        self.copy_btn.configure(text="Copiado ✓", text_color=theme.SUCCESS)
        if self._copy_job is not None:
            self.after_cancel(self._copy_job)
        self._copy_job = self.after(1800, self._restore_copy_label)

    def _restore_copy_label(self) -> None:
        self._copy_job = None
        self.copy_btn.configure(text="Copiar histórico", text_color=theme.TEXT)

    def _clear(self) -> None:
        if messagebox.askyesno(
                "Limpar histórico",
                "Todos os sorteios registrados serão apagados e todos os participantes "
                "voltam a concorrer.\n\nContinuar?", parent=self):
            self.app.clear_history()
            self.refresh()
