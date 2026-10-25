"""Primitivas de síntese (numpy + scipy). Tudo em float64, 44,1 kHz; estéreo = array (n, 2).
v0.2.0: escrito para o motor de áudio da F2 (docs/AUDIO_DESIGN.md)."""
import numpy as np
from scipy import signal

SR = 44100
TICK = SR // 20  # 2205 amostras por tick


def n_ticks(t):
    return int(round(t * TICK))


def time(n):
    return np.arange(n) / SR


# ------------------------------------------------------------------ ruídos


def white(rng, n):
    return rng.standard_normal(n)


def pink(rng, n):
    """1/f por filtro na frequência (exato e rápido)."""
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    y = np.fft.irfft(X / np.sqrt(f), n)
    return y / (np.std(y) + 1e-12)


def brown(rng, n):
    y = np.cumsum(rng.standard_normal(n))
    y = hp(y, 20)
    return y / (np.std(y) + 1e-12)


# ------------------------------------------------------------------ filtros


def _sos(btype, f, order=2):
    nyq = SR / 2
    if btype == "band":
        lo, hi = f
        lo = max(10.0, lo)
        hi = min(nyq * 0.95, hi)
        return signal.butter(order, [lo / nyq, hi / nyq], "bandpass", output="sos")
    return signal.butter(order, min(f, nyq * 0.95) / nyq, btype, output="sos")


def lp(x, f, order=2):
    return signal.sosfilt(_sos("low", f, order), x, axis=0)


def hp(x, f, order=2):
    return signal.sosfilt(_sos("high", f, order), x, axis=0)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_sos("band", (lo, hi), order), x, axis=0)


def tv_filter(x, fc, btype="low", width=1.0, block=256, order=2):
    """Filtro variando no tempo: coeficientes trocados a cada bloco, com o estado carregado.
    fc: array (n,) da frequência de corte (ou central, para 'band', com largura em oitavas = width)."""
    out = np.zeros_like(x)
    zi = None
    for i in range(0, len(x), block):
        c = float(np.mean(fc[i:i + block]))
        if btype == "band":
            sos = _sos("band", (c / 2 ** (width / 2), c * 2 ** (width / 2)), order)
        else:
            sos = _sos(btype, c, order)
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0.0
        out[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return out


def resonator(x, f, q):
    """Ressonância estreita (passa-banda de 2ª ordem, Q alto): madeira, metal, formante."""
    b, a = signal.iirpeak(f, q, fs=SR)
    return signal.lfilter(b, a, x)


# ------------------------------------------------------------------ envelopes e formas


def env_ad(n, attack, decay, start=0, shape="exp"):
    """Ataque linear (s) + decaimento exponencial (τ em s), começando na amostra start."""
    e = np.zeros(n)
    if start >= n:
        return e
    t = time(n - start)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - attack, 0) / decay) if shape == "exp" else np.clip(1 - (t - attack) / decay, 0, 1)
    e[start:] = a * d
    return e


def ramp(n, points):
    """Curva por pontos [(s, valor), …] interpolada linearmente."""
    ts, vs = zip(*points)
    return np.interp(time(n), ts, vs)


def fade(x, fin=0.002, fout=0.002):
    n = len(x)
    e = np.ones(n)
    a, b = int(fin * SR), int(fout * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if b:
        e[-b:] = np.minimum(e[-b:], np.linspace(1, 0, b))
    return x * (e[:, None] if x.ndim == 2 else e)


def sat(x, k=3.0):
    """Saturação suave: gera 2º/3º harmônicos para o alto-falante do celular (P-48)."""
    return np.tanh(k * x) / np.tanh(k)


def sine_sweep(n, f0, f1, curve="exp", start=0):
    """Seno com frequência variando (fase integrada)."""
    t = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** t if curve == "exp" else f0 + (f1 - f0) * t
    return np.sin(2 * np.pi * np.cumsum(f) / SR + start)


def phase_osc(freq):
    """Fase (rad) de um oscilador com frequência por amostra."""
    return 2 * np.pi * np.cumsum(freq) / SR


def bell(n, freqs, amps, decay, start=0, attack=0.002, rng=None, jitter=0.0):
    """Sino inarmônico: parciais com decaimentos levemente diferentes."""
    out = np.zeros(n)
    if start >= n:
        return out
    t = time(n - start)
    for i, (f, a) in enumerate(zip(freqs, amps)):
        d = decay * (1.0 - 0.15 * i)
        ph = rng.uniform(0, 2 * np.pi) if rng is not None else 0.0
        out[start:] += a * np.sin(2 * np.pi * f * (1 + jitter * i) * t + ph) * np.exp(-t / d)
    out[start:] *= np.clip(t / attack, 0, 1)
    return out


def saw_bl(freq, n, harmonics=24):
    """Dente-de-serra com banda limitada (soma de senos)."""
    ph = phase_osc(np.full(n, freq) if np.isscalar(freq) else freq)
    out = np.zeros(n)
    for k in range(1, harmonics + 1):
        out += np.sin(k * ph) / k
    return out * (2 / np.pi)


def pulse_train(freq, n, width=0.08):
    ph = (np.cumsum(np.full(n, freq) if np.isscalar(freq) else freq) / SR) % 1.0
    return (ph < width).astype(float) - width


def reverb_ir(rng, seconds, decay, stereo=True):
    n = int(seconds * SR)
    t = time(n)
    e = np.exp(-t / decay)
    if stereo:
        return np.stack([white(rng, n) * e, white(rng, n) * e], axis=1) * 0.05
    return white(rng, n) * e * 0.05


def convolve(x, ir):
    if x.ndim == 1 and ir.ndim == 2:
        return np.stack([signal.fftconvolve(x, ir[:, c])[: len(x)] for c in range(2)], axis=1)
    if x.ndim == 2:
        return np.stack([signal.fftconvolve(x[:, c], ir[:, c] if ir.ndim == 2 else ir)[: len(x)] for c in range(2)], axis=1)
    return signal.fftconvolve(x, ir)[: len(x)]


def bitcrush(x, bits=5, hold=6):
    y = np.repeat(x[::hold], hold, axis=0)[: len(x)]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q


def varispeed(x, rate):
    """Reprodução com taxa variável (fita): integra a taxa e reamostra. Afina e desacelera juntos."""
    pos = np.cumsum(rate) - rate[0]
    pos = np.clip(pos, 0, len(x) - 1)
    if x.ndim == 2:
        return np.stack([np.interp(pos, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
    return np.interp(pos, np.arange(len(x)), x)


# ------------------------------------------------------------------ estéreo


def pan(x, p):
    """p em [-1, 1] (escalar ou array), potência constante."""
    a = (np.asarray(p) + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def _allpass(x, delay_s, g):
    d = max(1, int(delay_s * SR))
    b = np.zeros(d + 1)
    a = np.zeros(d + 1)
    b[0], b[d] = -g, 1.0
    a[0], a[d] = 1.0, -g
    return signal.lfilter(b, a, x)


def stereo(x, width=0.0, rng=None):
    """Mono → estéreo compatível com mono: L = x + s, R = x − s, com s = x descorrelacionado por
    allpass. A soma (L + R)/2 é x EXATO. v0.2.0: antes era uma cópia atrasada de 3 ms, que virava filtro
    pente na soma mono (o chirp afundava ~6 dB ao passar por 150 Hz, e o _m posicional também)."""
    if width <= 0:
        return np.stack([x, x], axis=1)
    side = _allpass(_allpass(_allpass(x, 0.0071, 0.6), 0.0113, 0.6), 0.0173, 0.5)
    side = side * (0.5 * width)
    return np.stack([x + side, x - side], axis=1)


def mono(x):
    return x.mean(axis=1) if x.ndim == 2 else x
