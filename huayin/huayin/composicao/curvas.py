"""Curvas de controle: afinação (cents) de uma nota e automação de parâmetros ao longo do tempo.

A CurvaAltura é como as técnicas da mão esquerda viram som: 推 (empurrar a corda), 吟 (vibrato
pequeno), 猱 (vibrato largo do guqin), 绰/注 (entrar na nota por baixo/por cima), 滑音 (slide do
erhu). Tudo vira pontos e vibratos somados em cents relativos à nota escrita.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np

from ..dsp.util import interp_pontos


@dataclass
class Vibrato:
    inicio: float                  # s (relativo ao início da nota)
    fim: float | None = None       # s; None = até o fim
    taxa: float = 5.5              # Hz
    profundidade: float = 20.0     # cents (pico)
    forma: str = "simetrico"       # simetrico | acima | abaixo
    ataque: float = 0.15           # s até a profundidade total
    decaimento: float = 0.0        # 1/s: >0 faz o vibrato morrer (猱 do guqin)
    aceleracao: float = 0.0        # Hz/s: muda a taxa ao longo do vibrato
    jitter: float = 0.08           # irregularidade humana da taxa (fração)


@dataclass
class CurvaAltura:
    """Pontos (t, cents, forma) + vibratos. forma do segmento que CHEGA no ponto:
    linear | suave (cosseno) | degrau | rapido (sobe rápido e assenta, como um dedo deslizando)."""
    pontos: list = field(default_factory=lambda: [(0.0, 0.0, "degrau")])
    vibratos: list = field(default_factory=list)
    deriva: float = 0.0            # cents de oscilação lenta aleatória (instabilidade humana)

    def copiar(self) -> "CurvaAltura":
        return copy.deepcopy(self)

    def para(self, t: float, cents: float, forma: str = "suave") -> "CurvaAltura":
        self.pontos.append((float(t), float(cents), forma))
        self.pontos.sort(key=lambda p: p[0])
        return self

    def inicio_em(self, cents: float) -> "CurvaAltura":
        """Troca o valor inicial (ex.: 绰 começa abaixo e sobe)."""
        t0, _, f = self.pontos[0]
        self.pontos[0] = (t0, float(cents), f)
        return self

    def vibrato(self, inicio=0.0, fim=None, taxa=5.5, profundidade=20.0, forma="simetrico",
                ataque=0.15, decaimento=0.0, aceleracao=0.0, jitter=0.08) -> "CurvaAltura":
        self.vibratos.append(Vibrato(inicio, fim, taxa, profundidade, forma, ataque, decaimento,
                                     aceleracao, jitter))
        return self

    def deslocar(self, dt: float) -> "CurvaAltura":
        """Desloca tudo no tempo (usado quando uma nota em legato é emendada na anterior)."""
        c = self.copiar()
        c.pontos = [(t + dt, v, f) for t, v, f in c.pontos]
        for v in c.vibratos:
            v.inicio += dt
            if v.fim is not None:
                v.fim += dt
        return c

    def emendar(self, outra: "CurvaAltura", a_partir: float, deslocamento: float = 0.0,
                transicao: float = 0.0, forma: str = "rapido") -> "CurvaAltura":
        """Emenda outra curva a partir de a_partir (s), somando deslocamento (cents).

        transicao > 0 faz um slide do valor atual até o novo (滑音/上/下); 0 = salto (打/hammer-on).
        Os vibratos da curva atual param em a_partir.
        """
        c = self.copiar()
        o = outra.deslocar(a_partir + transicao)
        atual = self.valor_em(a_partir)
        c.pontos = [p for p in c.pontos if p[0] < a_partir]
        c.pontos.append((a_partir, atual, "linear"))
        c.pontos += [(t, v + deslocamento, forma if i == 0 and transicao > 0 else f)
                     for i, (t, v, f) in enumerate(o.pontos)]
        c.vibratos = [v for v in c.vibratos if v.inicio < a_partir]
        for v in c.vibratos:
            v.fim = a_partir if v.fim is None else min(v.fim, a_partir)
        c.vibratos += o.vibratos
        return c

    def valor_em(self, t: float) -> float:
        return float(self._pontos(np.array([t]))[0])

    def _pontos(self, t: np.ndarray) -> np.ndarray:
        ps = sorted(self.pontos, key=lambda p: p[0])
        y = np.full(t.shape, ps[0][1], dtype=float)
        for (t0, v0, _), (t1, v1, forma) in zip(ps[:-1], ps[1:]):
            m = (t >= t0) & (t < t1) if t1 > t0 else np.zeros(t.shape, bool)
            if forma == "degrau" or t1 <= t0:
                y[m] = v0
            else:
                u = (t[m] - t0) / (t1 - t0)
                if forma == "suave":
                    u = 0.5 - 0.5 * np.cos(np.pi * u)
                elif forma == "rapido":
                    u = 1 - (1 - u) ** 3
                y[m] = v0 + (v1 - v0) * u
            y[t >= t1] = v1
        return y

    def avaliar(self, n: int, sr: int, rng: np.random.Generator | None = None) -> np.ndarray:
        t = np.arange(n) / sr
        y = self._pontos(t)
        rng = rng or np.random.default_rng(0)
        for v in self.vibratos:
            fim = t[-1] + 1 if v.fim is None else v.fim
            m = (t >= v.inicio) & (t < fim)
            if not m.any():
                continue
            tt = t[m] - v.inicio
            taxa = v.taxa + v.aceleracao * tt
            if v.jitter:
                # taxa oscila devagar de forma aleatória (dedo humano não é um LFO)
                k = max(2, int(tt[-1] * 3) + 2)
                nos = rng.normal(0, v.jitter, k)
                taxa = taxa * (1 + np.interp(tt, np.linspace(0, tt[-1] + 1e-9, k), nos))
            fase = 2 * np.pi * np.cumsum(taxa) / sr
            env = np.clip(tt / max(v.ataque, 1e-4), 0, 1)
            if v.decaimento:
                env = env * np.exp(-v.decaimento * tt)
            if v.fim is not None:
                # solta o vibrato suavemente nos últimos 60 ms
                env = env * np.clip((fim - t[m]) / 0.06, 0, 1)
            if v.forma == "acima":
                onda = 0.5 * (1 - np.cos(fase))
            elif v.forma == "abaixo":
                onda = -0.5 * (1 - np.cos(fase))
            else:
                onda = np.sin(fase)
            y[m] += v.profundidade * env * onda
        if self.deriva:
            k = max(2, int(n / sr * 2) + 2)
            y += np.interp(t, np.linspace(0, t[-1] + 1e-9, k), rng.normal(0, self.deriva, k))
        return y


@dataclass
class Automacao:
    """Automação de um parâmetro de faixa ao longo da música (em TEMPOS/beats).

    pontos: [(tempo, valor)], forma: linear | suave | degrau.
    Parâmetros de faixa: volume_db, pan, reverb (envio), largura, brilho, expressao.
    """
    parametro: str
    pontos: list
    forma: str = "linear"

    def avaliar_segundos(self, t_seg: np.ndarray, beat_para_seg) -> np.ndarray:
        ps = [(beat_para_seg(b), v) for b, v in self.pontos]
        return interp_pontos(ps, t_seg, self.forma)
