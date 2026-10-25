"""O gesto GW150914: a identidade sonora do filme (v0.2.7).
Retorno do usuário: os efeitos eram bem feitos mas GENÉRICOS ("plim do JLPT", "transição do Discovery",
"até o ZA WARUDO é mais insano"). Como o BRAAAM de A Origem nasceu de uma música tocada em câmera lenta, aqui
todo grande evento nasce de UM material: a onda gravitacional da fusão (subida que acelera, para seca, e o anel
do ringdown), em escalas, velocidades e sentidos diferentes:
  gesture(...)             a fusão (para frente) ou o nascimento (de trás pra frente, descendo);
  breath_gesture(...)      o mesmo gesto como varredura de ar (sem nota): os brilhos de lente;
  freeze(x)                congelamento espectral (o instante pendurado, a dilatação);
  stutter(src, holds, ...) o disco arranhado nos ticks do stutter da câmera, cada pulo mais grave."""
import numpy as np

import dsp
from dsp import SR, TICK, time


def gw_freq(t_rel, T, f0=35.0, f1=250.0):
    """f(τ) da fase de inspiral (f ∝ τ^(-3/8)), normalizada para ir de f0 a f1 em T segundos."""
    tau = np.maximum(T - t_rel, 1e-4)
    k = (f1 / f0) ** (-8 / 3)  # τ_final / τ_inicial para dar f1/f0
    tau_end = T * k / (1 - k)
    return f0 * ((tau + tau_end) / (T + tau_end)) ** (-0.375)


def gesture(T=0.2, f0=35.0, f1=250.0, ring_s=0.25, ring_tau=0.06, harm=0.5, reverse=False, drive=2.0):
    """Inspiral (T s, f0 → f1) + ringdown (f1, τ). reverse=True: o nascimento (o anel cresce e a nota DESCE).
    Amplitude ∝ f^(2/3) (como a onda de verdade); harmônicos por saturação para o celular ouvir (P-48)."""
    n1 = int(T * SR)
    t = time(n1)
    f = gw_freq(t, T, f0, f1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    a = (f / f1) ** (2 / 3)
    n2 = int(ring_s * SR)
    t2 = time(n2)
    ph2 = ph[-1] + 2 * np.pi * f1 * t2
    ring = np.exp(-t2 / ring_tau)
    phase = np.concatenate([ph, ph2])
    amp = np.concatenate([a, ring])
    x = np.sin(phase) * amp + harm * np.sin(2 * phase + 0.4) * amp ** 1.3
    x = dsp.sat(x * drive, drive) / 1.0
    x[: int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return x[::-1].copy() if reverse else x


def breath_gesture(rng, T=0.08, f0=1800.0, f1=9000.0, reverse=True, q_oct=0.5):
    """O gesto como AR: ruído num passa-banda estreito que segue a varredura do chirp. Sem nota, sem 'plim'."""
    n = int((T + 0.05) * SR)
    t = time(n)
    f = np.where(t < T, gw_freq(np.minimum(t, T), T, f0, f1), f1)
    if reverse:
        f = f[::-1]
    x = dsp.tv_filter(dsp.white(rng, n), f, "band", width=q_oct, block=64)
    env = np.interp(t, [0, T * 0.7, T, T + 0.05], [0.2, 1.0, 0.6, 0.0])
    if reverse:
        env = env[::-1]
    return x * env


def freeze(grain, seconds, rng, frame=4096, hop=1024):
    """Congelamento espectral: a magnitude de um instante, com fase aleatória a cada quadro (overlap-add).
    O som 'para no tempo' sem parar de soar."""
    g = dsp.mono(grain) if grain.ndim == 2 else grain
    if len(g) < frame:
        g = np.pad(g, (0, frame - len(g)))
    w = np.hanning(frame)
    mag = np.abs(np.fft.rfft(g[:frame] * w))
    n = int(seconds * SR)
    out = np.zeros(n + frame)
    for i in range(0, n, hop):
        ph = rng.uniform(0, 2 * np.pi, len(mag))
        out[i:i + frame] += np.fft.irfft(mag * np.exp(1j * ph), frame) * w
    out = out[:n]
    return out / (np.abs(out).max() + 1e-12)


def stutter(src, start_tick, holds, end_tick, pitch_step=0.93, gain_step=0.88, grain_ticks=3):
    """Disco arranhado: a partir de start_tick, o MESMO pedaço (grain_ticks antes do start) se repete; cada
    repetição dura o 'hold' do stutter da câmera (o último se repete até end_tick) e sai mais grave e mais baixa
    (o redshift). src em tempo absoluto: amostra 0 = tick 0."""
    g = src[int((start_tick - grain_ticks) * TICK):int(start_tick * TICK)].copy()
    n = int((end_tick - start_tick) * TICK)
    out = np.zeros((n, 2)) if g.ndim == 2 else np.zeros(n)
    t, k, i = 0, 0, 0
    while t < n:
        h = holds[min(i, len(holds) - 1)]
        m = min(int(h * TICK), n - t)
        rate = np.full(m, pitch_step ** k)
        loop = np.concatenate([g] * (int(m / max(1, len(g)) * 1.2) + 2))
        piece = dsp.varispeed(loop, rate)[:m]
        f = min(int(0.004 * SR), m // 2)
        env = np.ones(m)
        env[:f] = np.linspace(0, 1, f)
        env[m - f:] = np.linspace(1, 0, f)
        out[t:t + m] += (piece * (env[:, None] if piece.ndim == 2 else env)) * gain_step ** k
        t += m
        k += 1
        i += 1
    return out
