"""Ato VII (B20–B22): o som pelo ponto de audição (v0.2.6). Envelopes compartilhados pela trilha e pelos efeitos,
a partir de spec/music.json → act7 (v5: antes em spec/score.json; o Risset de subida era nota da trilha antiga e saiu):
- muffle:   o mundo abafado (embaixo d'água) voltando: passa-baixa que abre de 160 Hz até ~16 kHz;
- tinnitus: o zumbido do ouvido depois do horizonte, que desce e pousa na nota do coral;
- dropout:  3 ticks de quase-silêncio antes do clarão (o contraste que faz o impacto aterrissar);
- width:    o estéreo abrindo de quase mono para largo no clarão (a luz se espalhando).
Tudo em tempo ABSOLUTO do filme (ticks); `t0` é o tick da amostra 0 do sinal recebido."""
import json
from pathlib import Path

import numpy as np

import dsp
from dsp import SR, TICK, time

ROOT = Path(__file__).resolve().parents[2]
A7 = json.loads((ROOT / "spec/music.json").read_text(encoding="utf-8"))["act7"]
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def hz(name):
    n, rest = name[0], name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 440.0 * 2 ** ((NOTE[n] + acc + 12 * (int(rest) - 4)) / 12)


def ticks_of(n, t0):
    return t0 + np.arange(n) / TICK


def muffle(x, t0):
    """Passa-baixa variável do ponto de audição. Fora da janela, não mexe."""
    m = A7["muffle"]
    n = len(x)
    tk = ticks_of(n, t0)
    a = int(max(0, (m["from"] - t0) * TICK))
    b = int(min(n, (m["to"] + 4 - t0) * TICK))
    if b <= a:
        return x
    lo, hi = m["cutoff_hz"]
    u = np.clip((tk[a:b] - m["from"]) / (m["to"] - m["from"]), 0, 1)
    fc = lo * (hi / lo) ** (u ** 1.3)  # abre devagar no começo, depois rápido (o ouvido "destampa")
    y = x.copy()
    y[a:b] = np.stack([dsp.tv_filter(x[a:b, c], fc, "low") for c in range(2)], axis=1)
    return y


def tinnitus(n, t0, rng):
    """O zumbido: dois senos quase iguais (batimento lento), nascendo do silêncio e descendo de Ré8 a Ré6."""
    T = A7["tinnitus"]
    tk = ticks_of(n, t0)
    g0, g1 = T["glide"]
    f0, f1 = hz(T["notes"][0]), hz(T["notes"][1])
    u = np.clip((tk - g0) / (g1 - g0), 0, 1)
    f = f0 * (f1 / f0) ** (u * u * (3 - 2 * u))
    env = np.clip((tk - T["from"]) / T["fade_in_ticks"], 0, 1) * (tk >= T["from"])
    env *= np.interp(tk, [g1 - 6, g1 + 4], [1, 0])  # o coral assume
    ph = 2 * np.pi * np.cumsum(f) / SR
    ph2 = 2 * np.pi * np.cumsum(f + T["beat_hz"]) / SR
    x = (np.sin(ph) + 0.6 * np.sin(ph2 + 1.0)) * env * T["level"]
    return dsp.stereo(x)  # no meio da cabeça


def dropout(n, t0):
    d = A7["dropout"]
    tk = ticks_of(n, t0)
    g = 10 ** (d["gain_db"] / 20)
    return np.interp(tk, [d["from"] - 0.4, d["from"], d["to"] - 0.05, d["to"]], [1, g, g, 1])


def widen(x, t0):
    """Largura estéreo por M/S (soma mono intacta): quase mono "dentro da cabeça", abrindo no clarão."""
    tk = ticks_of(len(x), t0)
    ts, ws = zip(*A7["width"])
    w = np.where(tk >= ts[0], np.interp(tk, ts, ws), 1.0)  # antes do Ato VII, não mexe
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([mid + side, mid - side], axis=1)


def world(n, t0, rng):
    """A cratera e o vento, ouvidos de dentro (o muffle abafa)."""
    W = A7["world"]
    tk = ticks_of(n, t0)
    env = np.interp(tk, [W["from"], W["from"] + 6, W["to"] - 10, W["to"]], [0, 1, 1, 0]) * W["level"]
    wind = dsp.lp(dsp.brown(rng, n), 500)
    t = time(n)
    drone = sum(np.sin(2 * np.pi * hz(nm) * t + i) for i, nm in enumerate(W["drone"])) * 0.4
    return dsp.stereo((wind * 0.7 + drone) * env, 0.8)
