"""Filtros: biquads (receitas RBJ), banco de ressonadores modais e projeto dos filtros de perda.

Os ressonadores modais são a base do "corpo" de cada instrumento: a caixa de paulównia
do pipa, a pele de cobra do erhu, o tubo de bambu do dizi. Cada modo é (freq, T60, ganho).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import lfilter, sosfilt

# ---------------------------------------------------------------- biquads RBJ


def _sos(b, a):
    b = np.asarray(b, float) / a[0]
    a = np.asarray(a, float) / a[0]
    return np.array([[b[0], b[1], b[2], 1.0, a[1], a[2]]])


def biquad(tipo: str, f: float, sr: int, q: float = 0.7071, ganho_db: float = 0.0) -> np.ndarray:
    """Retorna um SOS (1, 6). tipo: passa_baixa, passa_alta, passa_banda, rejeita, pico,
    prateleira_baixa, prateleira_alta."""
    f = float(np.clip(f, 1.0, 0.49 * sr))
    w0 = 2 * np.pi * f / sr
    cw, sw = np.cos(w0), np.sin(w0)
    alfa = sw / (2 * q)
    A = 10 ** (ganho_db / 40)
    if tipo == "passa_baixa":
        return _sos([(1 - cw) / 2, 1 - cw, (1 - cw) / 2], [1 + alfa, -2 * cw, 1 - alfa])
    if tipo == "passa_alta":
        return _sos([(1 + cw) / 2, -(1 + cw), (1 + cw) / 2], [1 + alfa, -2 * cw, 1 - alfa])
    if tipo == "passa_banda":
        return _sos([alfa, 0, -alfa], [1 + alfa, -2 * cw, 1 - alfa])
    if tipo == "rejeita":
        return _sos([1, -2 * cw, 1], [1 + alfa, -2 * cw, 1 - alfa])
    if tipo == "pico":
        return _sos([1 + alfa * A, -2 * cw, 1 - alfa * A], [1 + alfa / A, -2 * cw, 1 - alfa / A])
    raiz = 2 * np.sqrt(A) * alfa
    if tipo == "prateleira_baixa":
        return _sos([A * ((A + 1) - (A - 1) * cw + raiz), 2 * A * ((A - 1) - (A + 1) * cw),
                     A * ((A + 1) - (A - 1) * cw - raiz)],
                    [(A + 1) + (A - 1) * cw + raiz, -2 * ((A - 1) + (A + 1) * cw),
                     (A + 1) + (A - 1) * cw - raiz])
    if tipo == "prateleira_alta":
        return _sos([A * ((A + 1) + (A - 1) * cw + raiz), -2 * A * ((A - 1) + (A + 1) * cw),
                     A * ((A + 1) + (A - 1) * cw - raiz)],
                    [(A + 1) - (A - 1) * cw + raiz, 2 * ((A - 1) - (A + 1) * cw),
                     (A + 1) - (A - 1) * cw - raiz])
    raise ValueError(f"tipo de biquad desconhecido: {tipo}")


def filtrar(x: np.ndarray, sos: np.ndarray) -> np.ndarray:
    return sosfilt(sos, x, axis=-1)


def passa_baixa(x, f, sr, q=0.7071):
    return filtrar(x, biquad("passa_baixa", f, sr, q))


def passa_alta(x, f, sr, q=0.7071):
    return filtrar(x, biquad("passa_alta", f, sr, q))


def passa_banda(x, f, sr, q=1.0):
    return filtrar(x, biquad("passa_banda", f, sr, q))


def um_polo(x: np.ndarray, coef: float) -> np.ndarray:
    """Passa-baixa de um polo y = (1-c) x + c y[-1]  (0 <= c < 1)."""
    return lfilter([1 - coef], [1, -coef], x, axis=-1)


def coef_um_polo(fc: float, sr: int) -> float:
    return float(np.exp(-2 * np.pi * min(fc, 0.49 * sr) / sr))


def dc_block(x: np.ndarray, r: float = 0.995) -> np.ndarray:
    return lfilter([1, -1], [1, -r], x, axis=-1)


# ---------------------------------------------------------------- ressonadores modais


def ressonador_sos(f: float, t60: float, sr: int) -> np.ndarray:
    """Ressonador de 2ª ordem com zeros em DC e Nyquist e ganho ~1 no pico."""
    f = float(np.clip(f, 5.0, 0.48 * sr))
    r = np.exp(-6.907755 / (max(t60, 1e-4) * sr))
    th = 2 * np.pi * f / sr
    g = (1 - r * r) / 2
    return np.array([[g, 0.0, -g, 1.0, -2 * r * np.cos(th), r * r]])


def banco_modal(x: np.ndarray, sr: int, modos, direto: float = 0.0) -> np.ndarray:
    """Soma em paralelo de ressonadores. modos = [(freq, T60, ganho), ...]."""
    y = direto * x
    for f, t60, g in modos:
        if f >= 0.48 * sr or g == 0:
            continue
        y = y + g * sosfilt(ressonador_sos(f, t60, sr), x, axis=-1)
    return y


# ---------------------------------------------------------------- projeto da perda da corda


def t60_material(f, t60_ref_baixo, f_baixo, t60_ref_alto, f_alto):
    """Modelo de amortecimento sigma(f) = b1 + b3 f²  (Chaigne & Askenfelt / Bensa).

    Recebe dois pontos medidos (T60 em f_baixo e em f_alto) e devolve T60(f).
    """
    s_b = 6.907755 / t60_ref_baixo
    s_a = 6.907755 / t60_ref_alto
    b3 = max((s_a - s_b) / max(f_alto ** 2 - f_baixo ** 2, 1e-9), 0.0)
    b1 = max(s_b - b3 * f_baixo ** 2, 1e-4)
    return 6.907755 / (b1 + b3 * np.asarray(f, float) ** 2)


def projetar_perda(f0: float, t60_f0: float, t60_alta: float, f_alta: float, sr: int):
    """Filtro de perda de um polo H(z) = g (1-p) / (1 - p z^-1) da malha da corda.

    O ganho por volta na frequência f deve ser 10^(-3 / (T60(f) * f0)) (são f0 voltas por
    segundo). Ajusta g em f0 e p pela razão entre f_alta e f0. Retorna (g, p).
    """
    G0 = 10 ** (-3.0 / (max(t60_f0, 1e-3) * f0))
    Gh = 10 ** (-3.0 / (max(t60_alta, 1e-3) * f0))
    r = min(Gh / G0, 0.99999)
    w = 2 * np.pi * min(f_alta, 0.45 * sr) / sr
    c = np.cos(w)
    r2 = r * r
    if r > 0.99998:
        p = 0.0
    else:
        A = 1 - r2
        Bq = 1 - r2 * c
        p = (Bq - np.sqrt(max(Bq * Bq - A * A, 0.0))) / A
    p = float(np.clip(p, 0.0, 0.999))
    w0 = 2 * np.pi * f0 / sr
    mag0 = (1 - p) / np.sqrt(1 - 2 * p * np.cos(w0) + p * p)
    g = float(min(G0 / mag0, 0.99999))
    return g, p


def atraso_fase_um_polo(p: float, f: float, sr: int) -> float:
    """Atraso de fase (amostras) do passa-baixa de um polo na frequência f."""
    w = 2 * np.pi * f / sr
    fase = -np.arctan2(p * np.sin(w), 1 - p * np.cos(w))  # fase de 1/(1 - p e^-jw)
    return float(-fase / w) if w > 0 else p / (1 - p)


def atraso_fase_allpass(a: float, f, sr: int):
    """Atraso de fase de H(z) = (a + z^-1) / (1 + a z^-1)."""
    w = 2 * np.pi * np.asarray(f, float) / sr
    fase = -w + 2 * np.arctan2(a * np.sin(w), 1 + a * np.cos(w))
    return -fase / np.maximum(w, 1e-12)


def projetar_dispersao(f0: float, B: float, sr: int, estagios: int = 4, n_parciais: int = 16):
    """Coeficiente dos passa-tudo que imitam a rigidez da corda (inarmonicidade B).

    Parciais de uma corda rígida: f_n = n f0 sqrt(1 + B n²). Uma cascata de passa-tudos com
    a < 0 atrasa mais os graves do que os agudos, então as parciais altas "chegam antes" e
    sobem. Busca o coeficiente que minimiza o erro em cents nas primeiras parciais.
    Retorna 0.0 quando a rigidez é desprezível.
    """
    if B < 1e-7 or estagios == 0:
        return 0.0
    n = np.arange(1, n_parciais + 1)
    alvo = n * f0 * np.sqrt(1 + B * n * n)
    alvo = alvo[alvo < 0.45 * sr]
    if alvo.size < 3:
        return 0.0
    melhor, erro_min = 0.0, np.inf
    for a in np.linspace(-0.95, -0.01, 189):
        # comprimento total da malha calibrado para a fundamental exata
        D = sr / alvo[0]
        Dfix = D - estagios * atraso_fase_allpass(a, alvo[0], sr)
        if Dfix < 2:
            continue
        # frequência de cada parcial: resolve w * atraso(w) = 2 pi k (iteração de ponto fixo)
        k = np.arange(1, alvo.size + 1)
        f = alvo.copy()
        for _ in range(6):
            tau = Dfix + estagios * atraso_fase_allpass(a, f, sr)
            f = k * sr / tau
        erro = np.sum((1200 * np.log2(f / alvo)) ** 2)
        if erro < erro_min:
            melhor, erro_min = a, erro
    return float(melhor)
