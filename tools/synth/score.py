"""Trilha (score) do buraco negro a partir de spec/score.json: a camada musical contínua por baixo dos efeitos.
- Órgão de tubos por síntese aditiva: registros 16' / 8' / 4' / 2 2⁄3' / 2' (+ mistura) que abrem com "stops";
  coro leve (3 vozes desafinadas), vento do fole, ataque e soltura lentos, cruzamento entre acordes.
- Ostinato: notas curtas de órgão/celesta nas meias-órbitas (acelera com a dança), na maré e no arpejo final.
- Sub: Ré grave contínuo no Ato I–II.
- Reverb de catedral (convolução, 4,5 s) e a parada de fita do Ato VI.
O filme inteiro (0–760) é renderizado UMA vez (cache) e cortado em sgx_score_a (0–600) e sgx_score_b (620–760).
v0.2.1."""
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

import dsp
from dsp import SR, TICK, time

ROOT = Path(__file__).resolve().parents[2]
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def freq(name):
    """'C#3', 'Bb1', 'A4' → Hz (A4 = 440)."""
    n, rest = name[0], name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    octave = int(rest)
    semis = NOTE[n] + acc + 12 * (octave - 4)
    return 440.0 * 2 ** (semis / 12)


def sample_curve(keys, t):
    """Dinâmica por keyframes [{t, v, ease?}] (o ease diz como se chega no ponto)."""
    out = np.zeros_like(t, dtype=float)
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        m = (t >= a["t"]) & (t <= b["t"])
        u = (t[m] - a["t"]) / max(b["t"] - a["t"], 1e-9)
        e = b.get("ease", "linear")
        if e == "inQuad":
            u = u * u
        elif e == "inSine":
            u = 1 - np.cos(u * np.pi / 2)
        elif e == "outSine":
            u = np.sin(u * np.pi / 2)
        out[m] = a["v"] + (b["v"] - a["v"]) * u
    out[t > keys[-1]["t"]] = keys[-1]["v"]
    return out


# Registros do órgão: (múltiplo da fundamental, peso, a partir de quanto "stops" entra)
RANKS = [(0.5, 0.55, 0.0), (1.0, 1.0, 0.0), (2.0, 0.55, 0.15), (3.0, 0.3, 0.35), (4.0, 0.3, 0.5), (6.0, 0.16, 0.7), (8.0, 0.12, 0.85)]


def organ_note(f, n, stops, rng):
    """Uma nota sustentada de órgão (n amostras). stops: array (n,) 0–1 que abre os registros."""
    t = time(n)
    out = np.zeros(n)
    for mult, w, gate in RANKS:
        fm = f * mult
        if fm > 9000 or fm < 28:  # abaixo de 28 Hz ninguém ouve (o 16' do Ré1 cairia em 18 Hz)
            continue
        open_ = np.clip((stops - gate) / 0.15, 0, 1) if gate > 0 else np.ones(n)
        for det in (-0.0018, 0.0, 0.0021):  # coro: 3 tubos levemente desafinados
            out += w * open_ * np.sin(2 * np.pi * fm * (1 + det) * t + rng.uniform(0, 2 * np.pi)) / 3
    # vento do fole: ruído bem baixo no registro da nota
    out += 0.015 * dsp.bp(dsp.white(rng, n), max(40, f * 0.8), min(16000, f * 6))
    return out * f ** 0.15 / 6.0  # notas agudas um pouco mais presentes (o grave já soma muitos tubos)


def pluck(f, dur_s, rng):
    """Nota curta do ostinato: órgão de flauta + brilho de celesta, ataque firme, decaimento médio."""
    n = int(dur_s * SR)
    t = time(n)
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t / (0.35 * dur_s + 0.08))
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * f * 4.02 * t) * np.exp(-t / 0.06)
    return x * env


def _ostinato_times(o, half_orbits):
    if o["on"] == "half_orbits":
        h = [x for x in half_orbits if o["from"] <= x <= o["to"]]
        ts = []
        for i, x in enumerate(h):
            ts.append(float(x))
            if i + 1 < len(h):
                for k in range(1, o.get("subdivide", 1)):
                    ts.append(x + (h[i + 1] - x) * k / o["subdivide"])
        return ts
    if o["on"] == "every":
        return [float(x) for x in np.arange(o["from"], o["to"] + 1e-9, o["period_ticks"])]
    if o["on"] == "accel":
        p0, p1 = o["period_ticks"]
        ts, t = [], float(o["from"])
        while t <= o["to"]:
            ts.append(t)
            u = (t - o["from"]) / (o["to"] - o["from"])
            t += p0 + (p1 - p0) * u
        return ts
    raise ValueError(o["on"])


@lru_cache(maxsize=1)
def render_full(end_tick=760):
    S = json.loads((ROOT / "spec/score.json").read_text(encoding="utf-8"))
    LY = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(20150914)  # GW150914
    n = end_tick * TICK
    ticks = np.arange(n) / TICK
    dyn = sample_curve(S["dynamics"], ticks)

    # --- órgão: cada acorde soa do seu t até o próximo, com cruzamento de 0,25 s
    organ = np.zeros(n)
    chords = S["chords"]
    xf = int(0.25 * SR)
    for i, c in enumerate(chords):
        a = c["t"] * TICK
        b = chords[i + 1]["t"] * TICK if i + 1 < len(chords) else n
        b2 = min(n, b + xf)
        m = b2 - a
        stops = np.full(m, c["stops"])
        env = np.ones(m)
        env[:xf] = np.linspace(0, 1, xf) ** 0.7
        env[-xf:] = np.minimum(env[-xf:], np.linspace(1, 0, xf))
        seg = sum(organ_note(freq(nm), m, stops, rng) for nm in c["notes"])
        organ[a:b2] += seg * env
    organ *= dyn

    # --- sub: Ré grave por baixo do Ato I–II (saturado de leve para o celular ouvir o 2º harmônico)
    sub = np.zeros(n)
    a, b = 0, 240 * TICK
    sub[a:b] = dsp.sat(np.sin(2 * np.pi * freq("D1") * time(b - a)) * 0.9, 1.8) * 0.35
    sub *= np.clip(dyn * 1.5, 0, 1)

    # --- ostinato
    ost = np.zeros(n)
    for o in S["ostinato"]:
        ts = _ostinato_times(o, LY["binary"]["half_orbit_ticks"])
        for i, t0 in enumerate(ts):
            gap = (ts[i + 1] - t0) if i + 1 < len(ts) else 6
            note = freq(o["notes"][i % len(o["notes"])])
            p = pluck(note, max(0.12, gap / 20 * 1.6), rng)
            st = int(t0 * TICK)
            e = min(n, st + len(p))
            # o ostinato também respeita a dinâmica, mas nunca some de todo enquanto toca
            ost[st:e] += p[: e - st] * o["level"] * (0.35 + 0.65 * dyn[st])

    dry = organ + ost * 0.5 + sub
    # --- reverb de catedral POR TRECHO: o rabo não pode atravessar o corte seco do 240 nem o silêncio de
    # 600–619 (são parte da direção). Trechos: [0, 240) · [240, 600) · [620, fim).
    R = S["reverb"]
    ir = dsp.lp(dsp.reverb_ir(rng, R["seconds"], R["decay"]), R["lowpass_hz"])
    ir = ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))  # energia unitária: o molhado tem o nível do seco
    out = np.zeros((n, 2))
    T = S["tape_stop"]
    for a_t, b_t in ((0, 240), (240, 600), (620, end_tick)):
        a, b = a_t * TICK, b_t * TICK
        seg = np.zeros(n)
        seg[a:b] = dry[a:b]
        wet = dsp.convolve(dsp.lp(seg, 7000), ir)
        x = dsp.stereo(seg, 0.6) * (1 - R["wet"]) + wet * R["wet"]
        x[b:] = 0
        if b_t == 240:
            x[b - int(0.004 * SR):b] *= np.linspace(1, 0, int(0.004 * SR))[:, None]  # corte seco: a fusão assume
        if b_t == 600:
            # parada de fita no Ato VI: desacelera e afina para baixo, termina em zero exato no 600
            ta, tb = T["from"] * TICK, T["to"] * TICK
            rate = np.linspace(T["rate"][0], T["rate"][1], tb - ta)
            x[ta:tb] = dsp.varispeed(x[ta:tb], rate)
            x[ta:tb] *= np.interp(np.arange(tb - ta), [0, (tb - ta) * 0.75, tb - ta - 1], [1, 0.5, 0])[:, None]
        out += x
    return out


def part(start_tick, end_tick):
    full = render_full()
    return full[start_tick * TICK:end_tick * TICK].copy()
