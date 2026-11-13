"""Regras do sorteio, independentes da interface."""

from __future__ import annotations

import random
from typing import Sequence


class RaffleSession:
    """Controla o conjunto de participantes e o histórico das rodadas."""

    def __init__(self, participants: Sequence[str], winners_per_round: int = 5) -> None:
        self.participants: tuple[str, ...] = tuple(participants)
        self.winners_per_round = winners_per_round
        self.exclude_drawn = True          # não repetir quem já foi sorteado
        self.rounds = 0
        self._drawn: set[str] = set()
        # SystemRandom usa a entropia do sistema operacional (sorteio imparcial).
        self._rng = random.SystemRandom()

    # ------------------------------------------------------------- consultas
    @property
    def total(self) -> int:
        return len(self.participants)

    def available(self) -> list[str]:
        """Participantes que podem sair na próxima rodada."""
        if self.exclude_drawn:
            return [p for p in self.participants if p not in self._drawn]
        return list(self.participants)

    def can_draw(self) -> bool:
        return len(self.available()) >= self.winners_per_round

    # ---------------------------------------------------------------- ações
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
        names: list[str] = []
        while len(names) < count:
            batch = pool[:]
            self._rng.shuffle(batch)
            names.extend(batch)
        return names[:count]

    def reset(self) -> None:
        """Zera o histórico: todos voltam a concorrer."""
        self._drawn.clear()
        self.rounds = 0
