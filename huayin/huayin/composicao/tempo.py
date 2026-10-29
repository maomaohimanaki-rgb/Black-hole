"""Mapa de andamento: converte tempos (beats) em segundos com mudanças e rampas (rit./accel.).

Muita música chinesa começa em 散板 (sanban, tempo livre) e acelera até 快板. Use
musica.andamento(tempo, bpm, rampa=True) para fazer a transição suave.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class MapaTempo:
    bpm_inicial: float = 90.0
    eventos: list = field(default_factory=list)  # [(beat, bpm, rampa)] — rampa: chega nesse bpm gradualmente

    def mudar(self, beat: float, bpm: float, rampa: bool = False):
        if bpm <= 0:
            raise ValueError("bpm precisa ser positivo")
        self.eventos.append((float(beat), float(bpm), bool(rampa)))
        self.eventos.sort(key=lambda e: e[0])

    def _segmentos(self):
        """[(beat_ini, bpm_ini, beat_fim, bpm_fim)] cobrindo de 0 ao infinito."""
        segs = []
        b0, v0 = 0.0, self.bpm_inicial
        for b, v, rampa in self.eventos:
            if b <= b0:  # mudança no mesmo ponto: vale na hora
                v0 = v
                continue
            segs.append((b0, v0, b, v if rampa else v0))
            b0, v0 = b, v
        segs.append((b0, v0, math.inf, v0))
        return segs

    def segundos(self, beat: float) -> float:
        t = 0.0
        for b0, v0, b1, v1 in self._segmentos():
            if beat <= b0:
                break
            fim = min(beat, b1)
            db = fim - b0
            if b1 == math.inf or v0 == v1:
                t += 60.0 * db / v0
            else:
                k = (v1 - v0) / (b1 - b0)
                t += 60.0 / k * math.log((v0 + k * db) / v0)
            if beat <= b1:
                break
        return t

    def beats(self, segundos: float) -> float:
        """Inverso de segundos() (busca binária; usado por importação MIDI e análise)."""
        lo, hi = 0.0, max(1.0, segundos * 10)
        while self.segundos(hi) < segundos:
            hi *= 2
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if self.segundos(mid) < segundos:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def bpm_em(self, beat: float) -> float:
        for b0, v0, b1, v1 in self._segmentos():
            if b0 <= beat < b1:
                if b1 == math.inf or v0 == v1:
                    return v0
                return v0 + (v1 - v0) * (beat - b0) / (b1 - b0)
        return self.bpm_inicial
