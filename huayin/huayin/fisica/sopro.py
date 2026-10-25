"""Sopros: flauta de jato (dizi 笛子, xiao 箫), palheta dupla cônica (suona 唢呐) e cilíndrica
(guanzi 管子), palheta livre (sheng 笙, hulusi 葫芦丝, bawu 巴乌) e flauta de vaso (xun 埙).
"""
from __future__ import annotations

import numpy as np

from ..dsp import filtros as F
from ..dsp.kernels import kernel_flauta, kernel_membrana, kernel_palheta_conica, kernel_palheta_cilindrica
from ..dsp.util import ruido

# v1.0: compensações medidas em tests/test_afinacao_fisica.py
_COMP_FLAUTA = 1.0
_COMP_CONICA = -0.1
_COMP_CILINDRICA = 0.0


def _p_refl(brilho: float, sr: int) -> float:
    return float(np.clip((0.75 - 0.5 * brilho) * (44100.0 / sr) ** 0.5, 0.02, 0.95))


# Correção de afinação da flauta (cents a subtrair) medida com razao_jato=0.32 e brilho=0.5.
# O modelo de jato soa a ~1,5× a ressonância do tubo (o jato alimenta o modo cuja fase "fecha"
# com meio período de trânsito), por isso o tubo é ajustado para 2/3 da nota, como no STK.
_CORR_FLAUTA_F = np.array([261.6, 330, 440, 550, 660, 880, 1100, 1320, 1760, 2640])
_CORR_FLAUTA_C = np.array([28, 30, 32, 34, 37, 43, 49, 56, 70, 98], float)


def renderizar_flauta(f_hz, sopro, sr, rng, razao_jato=0.32, ruido_sopro=0.08, brilho=0.5,
                      refl_jato=0.5, refl_fim=0.5):
    """Flauta de jato. sopro = pressão (0–1) por amostra; ruído de respiração é somado aqui."""
    n = f_hz.shape[0]
    p = _p_refl(brilho, sr)
    corr = np.interp(f_hz, _CORR_FLAUTA_F, _CORR_FLAUTA_C) * (48000.0 / sr)
    f_tubo = f_hz * 2.0 ** (-corr / 1200.0) * 0.666667
    comp = F.atraso_fase_um_polo(p, float(np.median(f_tubo)), sr) + _COMP_FLAUTA
    atraso = np.maximum(sr / np.maximum(f_tubo, 20.0) - comp, 6.0)
    r = F.passa_banda(ruido(n, rng), 2500, sr, 0.5)
    s = sopro * (1.0 + ruido_sopro * r)
    n_buf = int(atraso.max()) + 8
    y = kernel_flauta(atraso, float(razao_jato), s, p, float(refl_jato), float(refl_fim), n_buf)
    # ruído de ar que escapa pela embocadura (ouvido mesmo quando o tubo já soa)
    ar = F.passa_alta(ruido(n, rng), 1500, sr) * sopro * ruido_sopro * 0.15
    return F.dc_block(y + ar)


def membrana_dimo(y, sr, f_m=3200.0, zeta=0.08, kappa=4.0, ganho=1.0, mistura=0.35):
    """笛膜: a membrana de junco colada no furo do dizi vibra com a pressão do tubo e reforça os
    harmônicos altos com um zumbido leve (Tsai 2003). Retorna o sinal já misturado."""
    if mistura <= 0:
        return y
    m = kernel_membrana(np.asarray(y, float), float(sr), float(f_m), float(zeta), float(kappa),
                        float(ganho * f_m * 2 * np.pi))
    m = F.passa_alta(m, 900, sr)
    esc = (np.sqrt(np.mean(y * y)) + 1e-9) / (np.sqrt(np.mean(m * m)) + 1e-9)
    return y + mistura * esc * m


def renderizar_palheta_conica(f_hz, sopro, sr, rng, posicao=0.4, brilho=0.6, ruido_sopro=0.05,
                              offset=0.7, incl=0.3):
    """Estável (sem pular oitava) com sopro entre ~0,45 e 0,75 e posicao ~0,4 (medido)."""
    n = f_hz.shape[0]
    p = _p_refl(brilho, sr)
    comp = F.atraso_fase_um_polo(p, float(np.median(f_hz)), sr) + _COMP_CONICA
    atraso = np.maximum(sr / np.maximum(f_hz, 30.0) - comp, 8.0)
    s = sopro * (1.0 + ruido_sopro * F.passa_baixa(ruido(n, rng), 4000, sr))
    n_buf = int(atraso.max()) + 8
    y = kernel_palheta_conica(atraso, float(posicao), s, p, 0.95, float(offset), float(incl), n_buf)
    return F.dc_block(y)


def renderizar_palheta_cilindrica(f_hz, sopro, sr, rng, brilho=0.5, ruido_sopro=0.04,
                                  offset=0.7, incl=-0.3):
    n = f_hz.shape[0]
    p = _p_refl(brilho, sr)
    comp = F.atraso_fase_um_polo(p, float(np.median(f_hz)), sr) + _COMP_CILINDRICA
    # tubo fechado numa ponta: meia volta = quarto de onda, a malha percorre 2× o tubo
    atraso = np.maximum(0.5 * sr / np.maximum(f_hz, 30.0) - comp, 6.0)
    s = sopro * (1.0 + ruido_sopro * F.passa_baixa(ruido(n, rng), 4000, sr))
    n_buf = int(atraso.max()) + 8
    y = kernel_palheta_cilindrica(atraso, s, p, 0.95, float(offset), float(incl), n_buf)
    return F.dc_block(y)


def renderizar_palheta_livre(f_hz, amp, sr, rng, abertura=0.35, ressonancia=0.6, impar=0.0,
                             ruido_sopro=0.03, batimento_cents=0.0):
    """Palheta livre de latão (sheng/hulusi/bawu): a lingueta passa pela fenda e solta pulsos de
    ar curtos. O fluxo é um pulso assimétrico (abertura = fração do ciclo com a fenda aberta);
    o tubo acima da palheta reforça os harmônicos dele (ressonancia).
    impar > 0 puxa para harmônicos ímpares (hulusi: som de clarinete doce)."""
    n = f_hz.shape[0]
    dt = 1.0 / sr
    fase = np.cumsum(f_hz) * dt
    fase += rng.uniform(0, 1)
    ph = fase % 1.0
    # pulso de fluxo: meia senoide alargada, só quando a lingueta está fora da fenda
    a = float(np.clip(abertura, 0.1, 0.9))
    pulso = np.where(ph < a, np.maximum(np.sin(np.pi * ph / a), 0.0) ** 1.5, 0.0)
    if impar > 0:
        quadr = np.tanh(4 * np.sin(2 * np.pi * fase))
        pulso = (1 - impar) * pulso + impar * 0.5 * (quadr + 1)
    if batimento_cents:
        fase2 = fase * 2 ** (batimento_cents / 1200)
        ph2 = fase2 % 1.0
        pulso = 0.5 * pulso + 0.5 * np.where(ph2 < a, np.maximum(np.sin(np.pi * ph2 / a), 0.0) ** 1.5, 0.0)
    y = np.diff(pulso, prepend=pulso[0]) * sr / (2 * np.pi * np.maximum(f_hz, 20))  # radiação ∝ d/dt
    # ressonância do tubo: pente suave nos harmônicos do próprio tubo
    if ressonancia > 0:
        f_ref = float(np.median(f_hz))
        modos = [(f_ref * k, 0.03 + 0.05 / k, ressonancia / k ** 0.6) for k in range(1, 12)
                 if f_ref * k < 0.45 * sr]
        y = F.banco_modal(y, sr, modos, direto=1.0 - 0.5 * ressonancia)
    y += ruido_sopro * F.passa_banda(ruido(n, rng), 3000, sr, 0.6)
    return F.dc_block(y * amp)


def renderizar_vaso(f_hz, amp, sr, rng, ruido_sopro=0.12, harmonicos=(1.0, 0.08, 0.03, 0.015)):
    """Flauta de vaso (xun 埙 de cerâmica): ressonador de Helmholtz, quase senoidal, muito ar."""
    n = f_hz.shape[0]
    fase = 2 * np.pi * np.cumsum(f_hz) / sr
    y = sum(h * np.sin((k + 1) * fase) for k, h in enumerate(harmonicos))
    r = F.passa_banda(ruido(n, rng), float(np.median(f_hz)) * 2.5, sr, 1.5)
    r2 = F.passa_alta(ruido(n, rng), 2000, sr) * 0.12
    return (y + ruido_sopro * (r + r2)) * amp
