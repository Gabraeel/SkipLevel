"""Regras do sorteio e da lista de participantes, independentes da interface."""

from __future__ import annotations

import random
from typing import Iterable, Sequence

MAX_NAME_LENGTH = 60


def normalize_name(raw: str) -> str:
    """Padroniza um nome: sem espaços sobrando e em maiúsculas."""
    return " ".join(str(raw).split()).upper()


class RaffleSession:
    """Controla os participantes, quem já foi sorteado e as rodadas."""

    def __init__(self, participants: Sequence[str], winners_per_round: int = 5,
                 drawn: Iterable[str] = (), rounds: int = 0) -> None:
        self.winners_per_round = winners_per_round
        self.exclude_drawn = True          # não repetir quem já foi sorteado
        self.rounds = max(0, int(rounds))
        self.participants: list[str] = []
        self._drawn: set[str] = set()
        # SystemRandom usa a entropia do sistema operacional (sorteio imparcial).
        self._rng = random.SystemRandom()
        self.set_participants(participants)
        self._drawn = {normalize_name(n) for n in drawn} & set(self.participants)

    # ------------------------------------------------------------- consultas
    @property
    def total(self) -> int:
        return len(self.participants)

    @property
    def drawn(self) -> list[str]:
        return sorted(self._drawn)

    def was_drawn(self, name: str) -> bool:
        return name in self._drawn

    def available(self) -> list[str]:
        """Participantes que podem sair na próxima rodada."""
        if self.exclude_drawn:
            return [p for p in self.participants if p not in self._drawn]
        return list(self.participants)

    def can_draw(self) -> bool:
        return len(self.available()) >= self.winners_per_round

    # --------------------------------------------------------------- sorteio
    def draw(self) -> list[str]:
        """Sorteia `winners_per_round` pessoas distintas e registra a rodada."""
        pool = self.available()
        if len(pool) < self.winners_per_round:
            raise ValueError("Participantes insuficientes para um novo sorteio.")
        winners = self._rng.sample(pool, self.winners_per_round)
        self._drawn.update(winners)
        self.rounds += 1
        return winners

    def filler_names(self, count: int, exclude: str) -> list[str]:
        """Nomes aleatórios usados apenas no efeito visual da rolagem."""
        pool = [p for p in self.participants if p != exclude]
        if not pool:
            return [exclude] * count
        names: list[str] = []
        while len(names) < count:
            batch = pool[:]
            self._rng.shuffle(batch)
            names.extend(batch)
        return names[:count]

    def reset(self) -> None:
        """Zera o histórico de sorteados: todos voltam a concorrer."""
        self._drawn.clear()
        self.rounds = 0

    # ---------------------------------------------------------------- edição
    def set_participants(self, names: Iterable[str]) -> None:
        """Substitui a lista (normalizando e descartando vazios e duplicados)."""
        seen: dict[str, None] = {}
        for raw in names:
            name = normalize_name(raw)
            if name and len(name) <= MAX_NAME_LENGTH:
                seen.setdefault(name)
        self.participants = list(seen)
        self._drawn &= set(self.participants)

    def add(self, raw: str) -> str:
        """Adiciona uma pessoa; devolve o nome normalizado ou lança ValueError."""
        name = normalize_name(raw)
        if not name:
            raise ValueError("Digite um nome.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(f"Nome muito longo (máximo de {MAX_NAME_LENGTH} caracteres).")
        if name in self.participants:
            raise ValueError(f"{name} já está na lista.")
        self.participants.append(name)
        return name

    def remove(self, name: str) -> bool:
        """Remove uma pessoa; devolve se ela já tinha sido sorteada."""
        self.participants.remove(name)
        was_drawn = name in self._drawn
        self._drawn.discard(name)
        return was_drawn

    def restore(self, name: str, was_drawn: bool) -> None:
        """Desfaz uma remoção."""
        if name not in self.participants:
            self.participants.append(name)
            if was_drawn:
                self._drawn.add(name)
