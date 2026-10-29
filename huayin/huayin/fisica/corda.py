"""Corda dedilhada/percutida por guia de onda digital.

Uma nota de corda = uma excitação (o formato do dedilhado) circulando numa malha cujo
comprimento é o período da nota. A malha tem:
  * atraso fracionário variável por amostra (bend 推拉, vibrato 吟揉, slide 绰注);
  * filtro de perda projetado a partir do T60 do material (seda, aço, náilon);
  * passa-tudos de dispersão (rigidez → parciais levemente agudas, Fletcher 1964);
  * duas polarizações (vertical decai rápido, horizontal sustenta: "dupla queda");
  * modulação de tensão: dedilhado forte começa um pouco agudo e desce (comum no guqin).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from ..dsp import filtros as F
from ..dsp.kernels import kernel_corda
from ..dsp.util import ruido


@dataclass
class Material:
    """Comportamento de amortecimento e rigidez de um tipo de corda.

    t60_baixo/f_baixo e t60_alto/f_alto: dois pontos da curva T60(f) (σ = b1 + b3 f²).
    B_ref: coeficiente de inarmonicidade típico de uma corda SOLTA desse material. Ao pressionar
    a corda, B cresce com (f/f_solta)², porque B ∝ 1/L² e f ∝ 1/L. f_B fica só como documentação
    da faixa em que o valor foi estimado.
    """
    nome: str
    t60_baixo: float
    f_baixo: float
    t60_alto: float
    f_alto: float
    B_ref: float
    f_B: float
    ruido_atrito: float = 0.0  # ruído de deslizar o dedo (cordas enroladas de seda/metal)
    enrolamentos_por_m: float = 0.0
    descricao: str = ""

    def t60(self, f):
        return F.t60_material(f, self.t60_baixo, self.f_baixo, self.t60_alto, self.f_alto)

    def B(self, f, f_solta=None):
        if f_solta is None:
            return self.B_ref
        return self.B_ref * max(float(f) / float(f_solta), 1.0) ** 2


# v1.0: números de partida guiados pela literatura (seda tem atrito interno alto → agudos morrem
# antes; aço quase não perde). Ver docs/FIDELIDADE.md para o que é medido e o que é estimado.
MATERIAIS = {
    "seda": Material("seda", 9.0, 65.0, 0.9, 2500.0, 2.0e-5, 65.0, 0.9, 1800.0,
                     "corda de seda torcida (guqin, pipa Tang, se): quente, ataque macio, agudos curtos"),
    "seda_fina": Material("seda_fina", 4.0, 150.0, 0.6, 3000.0, 3.0e-5, 150.0, 0.5, 2500.0,
                          "seda fina sob tensão alta (pipa Tang, konghou)"),
    "aco_nylon": Material("aco_nylon", 7.0, 110.0, 1.6, 3000.0, 1.2e-4, 110.0, 0.35, 3000.0,
                          "aço revestido de náilon (pipa, guzheng e ruan modernos): brilhante e longo"),
    "aco": Material("aco", 9.0, 200.0, 2.2, 4000.0, 2.5e-4, 200.0, 0.2, 0.0,
                    "aço (yangqin, liuqin): metálico, sustain muito longo"),
    "aco_erhu": Material("aco_erhu", 3.0, 290.0, 0.8, 3000.0, 1.5e-4, 290.0, 0.25, 0.0,
                         "aço fino do erhu (só usado quando a corda é pinçada, 拨弦)"),
    "tripa": Material("tripa", 3.5, 100.0, 0.5, 2000.0, 6.0e-5, 100.0, 0.4, 0.0,
                      "corda de tripa/seda grossa (sanxian antigo)"),
}


@dataclass
class ParamsCorda:
    """Tudo que define UM golpe numa corda (gerado pelas técnicas dos instrumentos)."""
    f0: float                     # frequência de referência (Hz)
    dur: float                    # segundos até abafar
    vel: float = 0.7              # 0–1
    posicao: float = 0.12         # ponto do dedilhado (fração do comprimento a partir da ponte)
    dureza: float = 0.6           # 0 = polpa do dedo, 1 = palheta/unha dura
    material: Material = field(default_factory=lambda: MATERIAIS["aco_nylon"])
    t60_escala: float = 1.0       # multiplica o T60 (abafado parcialmente, corda velha)
    t60_soltura: float = 0.12     # T60 depois de abafar
    cents: np.ndarray | None = None  # curva de afinação por amostra (bend/vibrato/slide)
    modulacao_tensao: float = 0.0    # cents de subida no ataque com vel=1
    detune_pol: float = 0.8       # cents entre as duas polarizações
    mistura_pol: float = 0.45     # peso da polarização horizontal (sustenta mais)
    ruido_ataque: float = 0.03    # ruído do contato (unha/palheta raspando)
    contato: float = 0.0          # choque não linear (0 = desligado)
    harmonico: int = 0            # 泛音: >1 toca o harmônico n (dedo encostado no nó)
    f_solta: float | None = None  # frequência da corda solta (escala a rigidez ao pressionar)
    martelo: bool = False         # True = corda percutida (yangqin): pulso de contato em vez de pinçada
    contato_ms: float = 1.2       # duração do contato do martelo (mais curto = mais brilhante)
    reexcitacoes: list = field(default_factory=list)  # [(t_rel s, vel)] novos golpes sem abafar (trêmulo
                                                      # de baqueta): a corda é linear, então somar as
                                                      # excitações num só laço é exato e bem mais barato
    cauda_max: float = 12.0       # corta a cauda depois disso (segundos)


def _excitacao_martelo(P: int, posicao: float, contato_ms: float, vel: float, ruido_ataque: float,
                       rng: np.random.Generator, sr: int) -> np.ndarray:
    """Corda percutida: força na ponte ∝ sin(nπβ)·H(f), sem o 1/n da pinçada — o espectro só cai
    pelo tempo de contato do martelo (golpe forte = contato mais curto = mais brilho; Hall 1986)."""
    P = max(P, 4)
    w = max(2, int(contato_ms * 1e-3 * sr * (1.25 - 0.5 * vel)))
    pulso = np.hanning(w + 2)[1:-1]
    e = np.zeros(P + w + 2)
    k = int(np.clip(round(posicao * P), 1, P - 1))
    e[:w] += pulso
    e[k:k + w] -= pulso
    e = e[:P] if w < P else e
    if ruido_ataque > 0:
        n = min(e.size, int(0.002 * sr) + 1)
        e[:n] += ruido_ataque * 0.3 * ruido(n, rng)
    return e * vel * 0.8


def _excitacao(P: int, posicao: float, dureza: float, vel: float, ruido_ataque: float,
               rng: np.random.Generator, sr: int) -> np.ndarray:
    """Força na ponte de uma corda pinçada: onda retangular com ciclo = ponto do dedilhado.

    Coeficientes de Fourier ∝ sin(nπβ)/n (ponto β apaga as parciais múltiplas de 1/β).
    A largura do contato (dedo largo × unha fina) suaviza a borda e tira os agudos.
    """
    P = max(P, 4)
    k = int(np.clip(round(posicao * P), 1, P - 1))
    e = np.full(P, -posicao)
    e[:k] = 1.0 - posicao
    largura = 1 + int((1.0 - dureza) ** 1.5 * 0.08 * P + (1.0 - vel) * 0.02 * P)
    if largura > 1:
        jan = np.hanning(largura + 2)[1:-1]
        jan /= jan.sum()
        e = np.convolve(np.concatenate([e, e, e]), jan, mode="same")[P:2 * P]
    # brilho cresce com a força (pinçada forte = mais agudos, comportamento real das cordas)
    c = F.coef_um_polo(800 + 9000 * vel * (0.4 + 0.6 * dureza), sr)
    e = F.um_polo(np.concatenate([e, e]), c)[P:]
    e -= e.mean()
    if ruido_ataque > 0:
        r = ruido(P, rng) * np.exp(-np.arange(P) / max(P / 4, 1))
        e += ruido_ataque * r * (0.3 + dureza)
    return e * vel


def t60_golpe(p: ParamsCorda, sr: int) -> float:
    """T60 da fundamental (s) para este golpe."""
    f_ref = min(p.f0 * (p.harmonico if p.harmonico > 1 else 1), 0.45 * sr)
    t60 = float(p.material.t60(f_ref)) * p.t60_escala
    if p.harmonico > 1:
        # 泛音: o dedo encostado no nó mata as outras parciais; o que sobra é a série
        # n·f0 da corda inteira, então soa mais puro e um pouco mais longo.
        t60 *= 1.25
    return t60


def amostras_golpe(p: ParamsCorda, sr: int, n_max: int | None = None) -> int:
    """Quantas amostras o golpe precisa: até abafar + a soltura, ou até morrer sozinho (-60 dB)."""
    t60 = t60_golpe(p, sr)
    dur = min(p.dur, t60 * 1.05, p.cauda_max)
    n = int(dur * sr + p.t60_soltura * 1.2 * sr + 64)
    if n_max is not None:
        n = min(n, n_max)
    return max(n, 64)


def renderizar_corda(p: ParamsCorda, sr: int, rng: np.random.Generator,
                     n_max: int | None = None) -> np.ndarray:
    """Renderiza um golpe completo (ataque + sustentação + abafamento). Mono."""
    f_ref = min(p.f0 * (p.harmonico if p.harmonico > 1 else 1), 0.45 * sr)
    t60_f0 = t60_golpe(p, sr)
    t60_alt = float(p.material.t60(min(f_ref * 8, 0.4 * sr))) * p.t60_escala
    n = amostras_golpe(p, sr, n_max)
    n_soar = int(min(p.dur, t60_f0 * 1.05, p.cauda_max) * sr)

    t = np.arange(n) / sr
    cents = np.zeros(n) if p.cents is None else np.asarray(p.cents[:n], float)
    if cents.shape[0] < n:
        cents = np.concatenate([cents, np.full(n - cents.shape[0], cents[-1] if cents.size else 0.0)])
    if p.modulacao_tensao:
        tau = max(t60_f0 / 13.8, 0.03)  # energia decai 2× mais rápido que a amplitude
        cents = cents + p.modulacao_tensao * p.vel ** 2 * np.exp(-t / tau)
    f_inst = f_ref * 2.0 ** (cents / 1200.0)
    f_inst = np.minimum(f_inst, 0.45 * sr)

    B = float(p.material.B(p.f0, p.f_solta))
    estagios = 0 if B < 1e-6 else (2 if B < 1e-4 else 4)
    a_disp = _dispersao(round(f_ref, 1), round(B, 9), sr, estagios) if estagios else 0.0

    saida = np.zeros(n)
    t60_sol_alt = max(p.t60_soltura * 0.3, 0.01)
    polarizacoes = ((0.0, 0.62, 1.0 - p.mistura_pol), (p.detune_pol, 1.0, p.mistura_pol))
    if p.martelo:
        exc = _excitacao_martelo(int(round(sr / f_ref)), _posicao_efetiva(p), p.contato_ms, p.vel,
                                 p.ruido_ataque, rng, sr)
    else:
        exc = _excitacao(int(round(sr / f_ref)), _posicao_efetiva(p), p.dureza, p.vel, p.ruido_ataque, rng, sr)
    if p.reexcitacoes:
        fim = max(int(t * sr) for t, _ in p.reexcitacoes) + exc.size + 1
        total = np.zeros(min(fim, n))
        total[:exc.size] += exc[:total.size]
        for t, v in p.reexcitacoes:
            i0 = int(t * sr)
            if i0 >= total.size:
                continue
            if p.martelo:
                e = _excitacao_martelo(int(round(sr / f_ref)), _posicao_efetiva(p), p.contato_ms, v,
                                       p.ruido_ataque, rng, sr)
            else:
                e = _excitacao(int(round(sr / f_ref)), _posicao_efetiva(p), p.dureza, v, p.ruido_ataque, rng, sr)
            k = min(e.size, total.size - i0)
            total[i0:i0 + k] += e[:k]
        exc = total
    for detune, esc_t60, peso in polarizacoes:
        if peso <= 0:
            continue
        g1, p1 = F.projetar_perda(f_ref, t60_f0 * esc_t60, t60_alt * esc_t60, min(f_ref * 8, 0.4 * sr), sr)
        g2, p2 = F.projetar_perda(f_ref, p.t60_soltura, t60_sol_alt, min(f_ref * 8, 0.4 * sr), sr)
        comp = F.atraso_fase_um_polo(p1, f_ref, sr)
        if estagios:
            comp += estagios * float(F.atraso_fase_allpass(a_disp, f_ref, sr))
        atraso = sr / (f_inst * 2.0 ** (detune / 1200.0)) - comp
        atraso = np.maximum(atraso, 3.0)
        n_buf = int(atraso.max()) + 8
        y = kernel_corda(exc, atraso, g1, p1, g2, p2, n_soar, a_disp, estagios, n_buf,
                         float(p.contato), 0.6 * p.vel + 0.05)
        saida += peso * y
    # rampa final curtinha: a cauda depois do abafamento já está a -60 dB, só evita degrau
    k = min(n, int(0.004 * sr))
    saida[n - k:] *= np.linspace(1, 0, k)
    return saida


@lru_cache(maxsize=4096)
def _dispersao(f_ref: float, B: float, sr: int, estagios: int) -> float:
    # a busca custa alguns ms; um trêmulo de 200 notas repete a mesma corda/altura
    return F.projetar_dispersao(f_ref, B, sr, estagios)


def _posicao_efetiva(p: ParamsCorda) -> float:
    if p.harmonico > 1:
        # na série do harmônico n, o dedilhado em β vira β·n (mod 1) relativo ao novo período
        b = (p.posicao * p.harmonico) % 1.0
        return float(np.clip(b if b > 0.02 else 0.5, 0.03, 0.97))
    return float(np.clip(p.posicao, 0.02, 0.98))
