#!/usr/bin/env python3
"""Confere o 32' resultante (v5): toca só 16' + 10⅔' (sem o 32' de verdade) e mede a periodicidade do sinal pela
autocorrelação. Se a engenharia funciona, o período é o do Ré0 (18,35 Hz), uma nota que nenhum tubo toca. Mede de
novo depois de um passa-alta de 150 Hz (o alto-falante do celular, P-48): a periodicidade tem que continuar lá,
carregada só pelos harmônicos. Uso: python3 tools/synth/check_organ.py (sai 1 se falhar)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dsp  # noqa: E402
import organ  # noqa: E402
from dsp import SR  # noqa: E402


def period_hz(x, fmin=12, fmax=120):
    """Frequência da periodicidade mais forte (autocorrelação normalizada, entre fmin e fmax)."""
    x = x - x.mean()
    n = len(x)
    X = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(np.abs(X) ** 2)[:n]
    ac /= ac[0]
    lo, hi = int(SR / fmax), int(SR / fmin)
    lag = lo + int(np.argmax(ac[lo:hi]))
    return SR / lag, float(ac[lag])


def main():
    rng = np.random.default_rng(32)
    n = int(1.5 * SR)
    d2 = 440 * 2 ** (-31 / 12)  # tecla Ré2 (8')
    only16 = organ.note(d2, n, [["16", "bourdon", 0.8]], rng)[int(0.4 * SR):n]
    res = organ.note(d2, n, [["16", "bourdon", 0.8], ["10.67", "bourdon", 0.5]], rng)[int(0.4 * SR):n]
    ok = True
    print("alvo: Ré0 = 18,35 Hz (32'), Ré1 = 36,71 Hz (16')")
    for nome, x in (("só 16'", only16), ("16' + 10⅔' (32' resultante)", res),
                    ("16' + 10⅔', passa-alta 150 Hz (celular)", dsp.hp(res, 150, 8))):
        f, r = period_hz(x)
        print(f"  {nome:42s} periodicidade {f:6.2f} Hz (força {r:.2f})")
        if "resultante" in nome or "celular" in nome:
            ok &= abs(f - 18.35) < 0.5
    print("✓ o 32' resultante existe" if ok else "✗ o 32' resultante NÃO apareceu")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
