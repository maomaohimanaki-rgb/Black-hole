"""Os instrumentos da trilha v5 (do zero, 25/10/2026): órgão de tubos, coral e o relógio.
Referência de OFÍCIO (não de notas): o órgão de Interestelar. Um órgão não tem dinâmica por nota: a dinâmica vem
de quantos REGISTROS estão abertos (crescendo por soma) e da caixa expressiva (a "persiana" que abre e fecha).

Registros (o tamanho do tubo dá a altura; 8' = a nota escrita):
  32' ×0,25 · 16' ×0,5 · 10⅔' ×0,75 · 8' ×1 · 4' ×2 · 2⅔' ×3 · 2' ×4 · mistura (×6 e ×8)
O 32' RESULTANTE (acústico): 16' + 10⅔' juntos. As duas ondas (Ré 36,7 Hz e Lá 55 Hz, razão 2:3) só se repetem a
cada 1/18,35 s, e o ouvido ouve um Ré0 de 18,35 Hz que nenhum tubo toca (a fundamental fantasma). Os órgãos de
verdade fazem isso para não construir tubos de 10 m. Aqui ele vem junto com um 32' de verdade baixinho (fone e TV)
e com os harmônicos dos tubos, que levam a mesma periodicidade até o alto-falante do celular (P-48).
Tudo em float64, 44,1 kHz; mono por tubo (o estéreo vem da disposição dos tubos, ver music.py)."""
import numpy as np

import dsp
from dsp import SR, time

# espectros (amplitude por harmônico) de cada família de tubo
SPECTRA = {
    "principal": [1, .5, .32, .2, .14, .1, .07, .05, .035, .025, .018, .012],
    "flute": [1, .22, .07, .03, .015],
    "bourdon": [1, .03, .28, .02, .1, .01, .04],      # tubo tampado: quase só harmônicos ímpares
    "reed": [1, .85, .75, .68, .6, .52, .45, .4, .34, .3, .26, .22, .19, .16, .14, .12, .1, .08],
}
FEET = {"32": 0.25, "16": 0.5, "10.67": 0.75, "8": 1.0, "4": 2.0, "2.67": 3.0, "2": 4.0}
MIXTURE = (6.0, 8.0)  # 1⅓' e 1': o brilho do pleno


def _ranks(reg):
    """reg: [[pé, família, nível], …] → [(razão, família, nível)] (a mistura vira duas fileiras)."""
    out = []
    for foot, fam, lv in reg:
        if foot == "mix":
            out += [(r, fam, lv * (0.8 if i else 1.0)) for i, r in enumerate(MIXTURE)]
        else:
            out.append((FEET[foot], fam, lv))
    return out


def pipe(f, n, fam, rng, release=0.07):
    """Um tubo: aditivo, com a fala (ataque mais lento nos tubos grandes), o 'chiff' de ar dos tubos de boca e um
    vento que respira. n = duração da nota em amostras (o tubo fala enquanto a tecla está apertada)."""
    sp = SPECTRA[fam]
    nr = int(release * SR)
    m = n + nr
    t = time(m)
    wind = 1 + 0.0006 * np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6))
    ph = 2 * np.pi * np.cumsum(f * wind) / SR + rng.uniform(0, 6)
    nyq = SR / 2 * 0.9
    tau = float(np.clip(0.012 + 3.5 / f, 0.015, 0.22))  # tubo de 16' leva ~0,1 s para falar; de 2', ~0,02 s
    x = np.zeros(m)
    for k, a in enumerate(sp, start=1):
        if k * f >= nyq:
            break
        tk = tau / (1 + 0.25 * (k - 1))  # os harmônicos de cima falam antes (é o que dá o "ataque" de tubo)
        x += a * np.sin(k * ph + rng.uniform(0, 6)) * (1 - np.exp(-t / tk))
    if fam in ("principal", "flute") and f > 60:
        # chiff: o sopro de ar no começo da fala, em volta do 3º–6º harmônico
        lo, hi = min(f * 3, 9000), min(f * 7, 15000)
        if hi > lo * 1.2:
            x += dsp.bp(dsp.white(rng, m), lo, hi) * np.exp(-t / 0.018) * 0.12
    env = np.ones(m)
    env[n:] = np.exp(-np.arange(nr) / (release * SR / 4))
    return x * env


def note(freq, n, reg, rng, release=0.07):
    """Uma tecla com os registros `reg` puxados (cada fileira com desafinação própria de ±1,5 cent: o coro de
    tubos que faz o órgão 'brilhar')."""
    x = 0.0
    for ratio, fam, lv in _ranks(reg):
        f = freq * ratio * 2 ** (rng.uniform(-1.5, 1.5) / 1200)
        if f < 15 or f > SR * 0.4:
            continue
        x = x + lv * pipe(f, n, fam, rng, release)
    return x


# ------------------------------------------------------------------ coral


VOWELS = {"a": ((700, 1.0), (1220, 0.5), (2600, 0.25)), "o": ((450, 1.0), (800, 0.45), (2830, 0.12)),
          "u": ((325, 1.0), (700, 0.25), (2530, 0.06))}


def choir(freq, n, rng, vowel="a", voices=4, attack=0.35, release=0.5):
    """Coro por formantes: cada voz é um trem de harmônicos (fonte glotal) com vibrato e tremor próprios, passando
    pelas ressonâncias da vogal. Ataque lento (o coro "acende"), sem nada de sample."""
    nr = int(release * SR)
    m = n + nr
    t = time(m)
    out = np.zeros(m)
    for v in range(voices):
        det = 2 ** (rng.uniform(-9, 9) / 1200)
        vib = 1 + 0.0045 * np.sin(2 * np.pi * rng.uniform(4.6, 5.6) * t + rng.uniform(0, 6)) * np.clip(t / 0.6, 0, 1)
        ph = 2 * np.pi * np.cumsum(freq * det * vib) / SR
        src = np.zeros(m)
        for k in range(1, 30):
            if k * freq > 9000:
                break
            src += np.sin(k * ph + rng.uniform(0, 6)) / k
        src += dsp.bp(dsp.white(rng, m), 1500, 7000) * 0.02  # o ar da respiração
        y = sum(a * dsp.resonator(src, fc * rng.uniform(0.97, 1.03), 7) for fc, a in VOWELS[vowel])
        out += y
    env = np.clip(t / attack, 0, 1) ** 1.5
    env[n:] *= np.exp(-np.arange(nr) / (release * SR / 4))
    return out / voices * env


# ------------------------------------------------------------------ o relógio


def tick(rng, tock=False):
    """O tique de relógio de bolso: estalo seco em duas ressonâncias de metal e uma de madeira. O 'toc' é um
    pouco mais grave. Sem nota: é tempo, não música."""
    m = int(0.09 * SR)
    t = time(m)
    imp = np.zeros(m)
    q = int(0.0008 * SR)
    imp[:q] = rng.standard_normal(q)
    k = 0.86 if tock else 1.0
    x = (dsp.resonator(imp, 3100 * k, 18) * 1.0 + dsp.resonator(imp, 5200 * k, 22) * 0.6
         + dsp.resonator(imp, 1250 * k, 10) * 0.5)
    return x * np.exp(-t / 0.012) / (np.abs(x).max() + 1e-12)
