"""Ferramentas de medição usadas pelos testes (estimativa de altura, nível)."""
import numpy as np


def yin(x, sr, fmin=60, fmax=4000, limiar=0.12):
    """Estimador de frequência fundamental YIN (de Cheveigné & Kawahara 2002), simplificado."""
    x = np.asarray(x, float) - np.mean(x)
    W = min(len(x) // 2, 4096)
    maxlag, minlag = int(sr / fmin), int(sr / fmax)
    x = x[:W + maxlag + 1]
    d = np.array([np.sum((x[:W] - x[l:l + W]) ** 2) for l in range(maxlag)])
    cm = d.copy()
    cm[1:] = d[1:] * np.arange(1, maxlag) / np.maximum(np.cumsum(d[1:]), 1e-12)
    cm[0] = 1
    for l in range(minlag, maxlag - 1):
        if cm[l] < limiar and cm[l] <= cm[l + 1]:
            a, b, c = cm[l - 1], cm[l], cm[l + 1]
            den = a - 2 * b + c
            return sr / (l + (0.5 * (a - c) / den if den else 0))
    return sr / (minlag + np.argmin(cm[minlag:]))


def cents(f, ref):
    return 1200 * np.log2(f / ref)


def pico_espectral(x, sr, fmin, fmax):
    n = len(x)
    X = np.abs(np.fft.rfft(x * np.hanning(n), 8 * n))
    fr = np.fft.rfftfreq(8 * n, 1 / sr)
    m = (fr >= fmin) & (fr <= fmax)
    return fr[m][np.argmax(X[m])]
