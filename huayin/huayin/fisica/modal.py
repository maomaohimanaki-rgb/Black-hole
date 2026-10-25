"""Síntese modal para idiofones e membranofones: sinos 编钟, pedras 编磬, gongos 锣, pratos 钹,
tambores 鼓 e blocos de madeira 木鱼.

Cada modo é uma senoide amortecida. Os detalhes que fazem soar "de verdade":
  * razões inarmônicas medidas/estimadas por tipo de objeto;
  * amplitude por modo depende do PONTO de golpe (centro × borda, face × lateral do sino);
  * dureza da baqueta e força do golpe filtram os modos altos (golpe forte = mais brilho);
  * glissando não linear (gongos da ópera: o 小锣 sobe, o 大锣 desce; Jossic et al. 2018);
  * batimento: cada modo vira um par levemente desafinado (assimetria real do objeto);
  * "florescer" dos modos altos depois do golpe (cascata de energia do 抄锣/tam-tam).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..dsp import filtros as F
from ..dsp.util import ruido


@dataclass
class Modo:
    razao: float          # frequência relativa à fundamental nominal
    t60: float            # segundos
    amp: float            # amplitude relativa
    peso_borda: float = 1.0   # multiplicador quando golpeado na borda/lateral
    glide: float = 1.0        # quanto este modo participa do glissando não linear


@dataclass
class ParamsModal:
    f0: float
    modos: list
    vel: float = 0.7
    dur: float | None = None           # None = deixa soar até o fim natural
    borda: float = 0.0                 # 0 = centro/face, 1 = borda/lateral
    dureza: float = 0.6                # baqueta macia (0) × dura (1)
    glide_cents: float = 0.0           # desvio inicial (com vel=1) que se desfaz com o decaimento
    batimento_cents: float = 0.0
    florescer: float = 0.0             # 0–1: modos altos crescem depois do ataque
    t60_escala: float = 1.0
    t60_abafado: float = 0.08          # T60 depois de abafar (mão no gongo)
    ruido_ataque: float = 0.05
    cor_ruido_hz: float = 3000.0
    t60_ruido: float = 0.03
    n_aleatorio: int = 0               # modos extras aleatórios (pratos têm centenas)
    faixa_aleatoria: tuple = (2.0, 30.0)
    t60_aleatorio: float = 1.0
    cauda_max: float = 15.0


def renderizar_modal(p: ParamsModal, sr: int, rng: np.random.Generator) -> np.ndarray:
    modos = list(p.modos)
    if p.n_aleatorio:
        lo, hi = p.faixa_aleatoria
        razoes = np.exp(rng.uniform(np.log(lo), np.log(hi), p.n_aleatorio))
        for r in razoes:
            modos.append(Modo(float(r), p.t60_aleatorio * float(rng.uniform(0.4, 1.3)) / (r / lo) ** 0.35,
                              float(rng.uniform(0.2, 1.0)) / np.sqrt(r), 1.0, 1.0))
    t60_max = max(m.t60 for m in modos) * p.t60_escala
    if p.dur is None:
        n = int(min(t60_max * 1.1, p.cauda_max) * sr)
        n_abaf = n
    else:
        n_abaf = int(p.dur * sr)
        n = int(min(p.dur + p.t60_abafado * 1.2, t60_max * 1.1, p.cauda_max) * sr)
        n = max(n, min(n_abaf, int(p.cauda_max * sr)))
    n = max(n, 32)
    t = np.arange(n) / sr
    y = np.zeros(n)
    # baqueta: corte que sobe com a dureza e com a força (contato mais curto)
    fc = p.f0 * (2.0 + 20.0 * p.dureza ** 1.5) * (0.5 + p.vel)
    dt = 1.0 / sr
    for m in modos:
        f = p.f0 * m.razao
        if f >= 0.45 * sr:
            continue
        amp = m.amp * (1 - p.borda + p.borda * m.peso_borda)
        amp /= 1.0 + (f / fc) ** 2
        if amp < 1e-5:
            continue
        t60 = m.t60 * p.t60_escala
        sigma = 6.907755 / t60
        n_vivo = min(n, int((13.8 / sigma) * sr) + 1)  # até -120 dB
        tt = t[:n_vivo]
        env = np.exp(-sigma * tt)
        if n_abaf < n_vivo:
            s2 = 6.907755 / p.t60_abafado
            k = tt >= n_abaf * dt
            env[k] = env[n_abaf] * np.exp(-s2 * (tt[k] - n_abaf * dt))
        if p.florescer > 0 and m.razao > 3:
            # energia passa dos modos graves para os agudos nos primeiros ~0,5 s
            tau = 0.15 + 0.1 * np.log(m.razao)
            env *= 1 - p.florescer * np.exp(-tt / tau)
        # glissando: desvio proporcional à energia restante (Duffing: Δf ∝ amplitude²)
        if p.glide_cents and m.glide:
            desvio = p.glide_cents * m.glide * p.vel ** 2 * np.exp(-2.0 * sigma * tt)
            finst = f * 2.0 ** (desvio / 1200.0)
            fase = 2 * np.pi * np.cumsum(finst) * dt
        else:
            fase = 2 * np.pi * f * tt
        fase += rng.uniform(0, 2 * np.pi)
        if p.batimento_cents:
            d = p.batimento_cents * float(rng.uniform(0.5, 1.5))
            fase2 = fase * 2.0 ** (d / 1200.0)
            onda = 0.55 * np.sin(fase) + 0.45 * np.sin(fase2)
        else:
            onda = np.sin(fase)
        y[:n_vivo] += amp * env * onda
    if p.ruido_ataque > 0:
        nr = min(n, int(max(p.t60_ruido * 1.5, 0.005) * sr))
        r = ruido(nr, rng) * np.exp(-6.9 * np.arange(nr) / max(p.t60_ruido * sr, 1))
        r = F.passa_banda(r, p.cor_ruido_hz, sr, 0.8)
        y[:nr] += p.ruido_ataque * r * (0.4 + p.dureza)
    y *= p.vel
    k = min(n, int(0.003 * sr))
    y[n - k:] *= np.linspace(1, 0, k)
    return y


# ----------------------------------------------------------------------------- tabelas de modos

def modos_membrana(t60_base=0.6, n=12, ar=True):
    """Membrana circular presa na borda: zeros das funções de Bessel J_mn (Rayleigh).
    Com ar=True aproxima a carga de ar de um tambor de dois couros (modos mais juntos)."""
    razoes = [1.0, 1.594, 2.136, 2.296, 2.653, 2.918, 3.156, 3.501, 3.600, 3.652, 4.060, 4.154]
    borda = [0.6, 1.4, 1.8, 0.5, 2.0, 1.6, 2.2, 1.9, 0.6, 2.3, 2.4, 1.7]
    if ar:
        razoes = [1.0, 1.50, 1.98, 2.20, 2.44, 2.70, 2.95, 3.20, 3.35, 3.48, 3.80, 3.95]
    out = []
    for i in range(min(n, len(razoes))):
        out.append(Modo(razoes[i], t60_base / (1 + 0.35 * i), 1.0 / (1 + 0.25 * i), borda[i], 1.0))
    return out


def modos_barra_livre(t60_base=2.0, n=6):
    """Barra livre-livre (pedra de 编磬 aproximada): 1, 2.756, 5.404, 8.933... (Rayleigh)."""
    razoes = [1.0, 2.756, 5.404, 8.933, 13.34, 18.64]
    return [Modo(razoes[i], t60_base / (1 + 0.8 * i), 1.0 / (1 + 0.6 * i), 1.0 + 0.3 * i, 0.0)
            for i in range(min(n, len(razoes)))]
