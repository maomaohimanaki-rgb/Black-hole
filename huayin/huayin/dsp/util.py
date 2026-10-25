"""Utilidades de áudio: conversões, envelopes, ruído, pan, normalização e loudness.

Tudo aqui é numpy puro (vetorizado). Convenção do motor: áudio estéreo é um array
(2, N) float64; mono é (N,).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- conversões


def db_para_lin(db):
    return 10.0 ** (np.asarray(db, dtype=float) / 20.0)


def lin_para_db(x, piso=-200.0):
    x = np.maximum(np.abs(np.asarray(x, dtype=float)), 1e-12)
    return np.maximum(20.0 * np.log10(x), piso)


def cents_para_razao(c):
    return 2.0 ** (np.asarray(c, dtype=float) / 1200.0)


def razao_para_cents(r):
    return 1200.0 * np.log2(np.asarray(r, dtype=float))


def midi_para_hz(m, la4=440.0):
    return la4 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def hz_para_midi(f, la4=440.0):
    return 69.0 + 12.0 * np.log2(np.asarray(f, dtype=float) / la4)


def t60_para_raio(t60, sr):
    """Raio do polo que decai 60 dB em t60 segundos."""
    return np.exp(-6.907755 / (np.maximum(t60, 1e-6) * sr))


# ---------------------------------------------------------------- ruído


def ruido(n: int, rng: np.random.Generator, cor: str = "branco") -> np.ndarray:
    """Ruído de média zero e RMS ~1. cor: branco | rosa | marrom | azul."""
    if n <= 0:
        return np.zeros(0)
    w = rng.standard_normal(n)
    if cor == "branco":
        return w
    W = np.fft.rfft(w)
    f = np.arange(len(W), dtype=float)
    f[0] = 1.0
    expo = {"rosa": -0.5, "marrom": -1.0, "azul": 0.5}[cor]
    W *= f ** expo
    W[0] = 0.0
    x = np.fft.irfft(W, n)
    rms = np.sqrt(np.mean(x * x)) + 1e-12
    return x / rms


# ---------------------------------------------------------------- envelopes


def adsr(n: int, sr: int, a=0.01, d=0.1, s=0.7, r=0.2, n_soltar: int | None = None,
         curva: float = 3.0) -> np.ndarray:
    """Envelope ADSR com segmentos exponenciais (curva>0 deixa mais natural).

    n_soltar: amostra em que a nota é solta (padrão: n - r*sr).
    """
    env = np.zeros(n)
    if n == 0:
        return env
    na, nd, nr = max(1, int(a * sr)), max(1, int(d * sr)), max(1, int(r * sr))
    if n_soltar is None:
        n_soltar = max(0, n - nr)
    t = np.arange(n)
    # ataque
    m = t < na
    env[m] = (1 - np.exp(-curva * t[m] / na)) / (1 - np.exp(-curva))
    # decaimento até o sustain
    m = (t >= na) & (t < na + nd)
    env[m] = s + (1 - s) * np.exp(-curva * (t[m] - na) / nd)
    env[t >= na + nd] = s
    # soltura a partir do nível em que estava
    if n_soltar < n:
        nivel = env[min(n_soltar, n - 1)]
        m = t >= n_soltar
        env[m] = nivel * np.exp(-6.9 * (t[m] - n_soltar) / nr)
    return env


def interp_pontos(pontos, t: np.ndarray, forma: str = "linear") -> np.ndarray:
    """Interpola uma lista [(t, valor), ...] nos instantes t.

    forma: linear | suave (cosseno entre pontos) | degrau.
    """
    if not pontos:
        return np.zeros_like(t, dtype=float)
    ps = sorted(pontos, key=lambda p: p[0])
    xs = np.array([p[0] for p in ps], dtype=float)
    ys = np.array([p[1] for p in ps], dtype=float)
    if len(xs) == 1:
        return np.full(t.shape, ys[0])
    if forma == "degrau":
        idx = np.clip(np.searchsorted(xs, t, side="right") - 1, 0, len(ys) - 1)
        return ys[idx]
    if forma == "suave":
        idx = np.clip(np.searchsorted(xs, t, side="right") - 1, 0, len(xs) - 2)
        x0, x1 = xs[idx], xs[idx + 1]
        u = np.clip((t - x0) / np.maximum(x1 - x0, 1e-12), 0, 1)
        u = 0.5 - 0.5 * np.cos(np.pi * u)
        return ys[idx] + (ys[idx + 1] - ys[idx]) * u
    return np.interp(t, xs, ys)


def fade(x: np.ndarray, sr: int, entrada_ms=2.0, saida_ms=5.0) -> np.ndarray:
    """Rampa de entrada e saída (evita clique). Funciona em mono e estéreo."""
    y = np.array(x, dtype=float, copy=True)
    n = y.shape[-1]
    ni = min(n, int(entrada_ms * sr / 1000))
    no = min(n, int(saida_ms * sr / 1000))
    if ni > 0:
        y[..., :ni] *= np.sin(0.5 * np.pi * np.arange(ni) / ni) ** 2
    if no > 0:
        y[..., n - no:] *= np.cos(0.5 * np.pi * np.arange(no) / no) ** 2
    return y


# ---------------------------------------------------------------- estéreo


def pan_ganhos(pan):
    """Pan de potência constante: -1 = esquerda, 0 = centro, +1 = direita."""
    p = np.clip(np.asarray(pan, dtype=float), -1, 1)
    ang = (p + 1) * np.pi / 4
    return np.cos(ang), np.sin(ang)


def pan_mono(x: np.ndarray, pan=0.0) -> np.ndarray:
    gl, gr = pan_ganhos(pan)
    return np.vstack([x * gl, x * gr])


def para_estereo(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return np.vstack([x, x]) * np.sqrt(0.5)
    return x


def largura_estereo(x: np.ndarray, largura: float) -> np.ndarray:
    """0 = mono, 1 = original, >1 = mais aberto (técnica mid/side)."""
    m = 0.5 * (x[0] + x[1])
    s = 0.5 * (x[0] - x[1]) * largura
    return np.vstack([m + s, m - s])


# ---------------------------------------------------------------- níveis


def pico(x) -> float:
    return float(np.max(np.abs(x))) if np.size(x) else 0.0


def normalizar_pico(x: np.ndarray, alvo_db: float = -1.0) -> np.ndarray:
    p = pico(x)
    if p < 1e-12:
        return x
    return x * (db_para_lin(alvo_db) / p)


def lufs_integrado(x: np.ndarray, sr: int) -> float:
    """Loudness integrado (ITU-R BS.1770-4): ponderação K, blocos de 400 ms, porta absoluta e relativa."""
    from scipy.signal import lfilter

    x = np.atleast_2d(x)
    # estágio 1: prateleira alta (efeito da cabeça); estágio 2: passa-alta RLB.
    # Coeficientes recalculados para qualquer sr (forma bilinear dos filtros da norma).
    f0, g, q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    k = np.tan(np.pi * f0 / sr)
    vh = 10 ** (g / 20)
    vb = vh ** 0.4996667741545416
    a0 = 1 + k / q + k * k
    b1 = [(vh + vb * k / q + k * k) / a0, 2 * (k * k - vh) / a0, (vh - vb * k / q + k * k) / a0]
    a1 = [1, 2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0]
    f0, q = 38.13547087602444, 0.5003270373238773
    k = np.tan(np.pi * f0 / sr)
    a0 = 1 + k / q + k * k
    b2 = [1, -2, 1]
    a2 = [1, 2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0]
    y = lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)
    bloco, passo = int(0.4 * sr), int(0.1 * sr)
    if y.shape[-1] < bloco:
        ms = np.mean(y ** 2, axis=-1).sum()
        return -0.691 + 10 * np.log10(ms + 1e-12)
    inicios = np.arange(0, y.shape[-1] - bloco + 1, passo)
    ms = np.array([np.mean(y[:, i:i + bloco] ** 2, axis=-1).sum() for i in inicios])
    lz = -0.691 + 10 * np.log10(ms + 1e-12)
    ms = ms[lz > -70]
    if ms.size == 0:
        return -70.0
    rel = -0.691 + 10 * np.log10(np.mean(ms)) - 10
    lz = -0.691 + 10 * np.log10(ms + 1e-12)
    ms = ms[lz > rel]
    return float(-0.691 + 10 * np.log10(np.mean(ms) + 1e-12))


def normalizar_lufs(x: np.ndarray, sr: int, alvo=-16.0, teto_db=-1.0) -> np.ndarray:
    """Leva ao loudness alvo sem passar do teto de pico (usa o que for mais baixo)."""
    atual = lufs_integrado(x, sr)
    ganho = db_para_lin(alvo - atual)
    p = pico(x) * ganho
    if p > db_para_lin(teto_db):
        ganho *= db_para_lin(teto_db) / p
    return x * ganho
