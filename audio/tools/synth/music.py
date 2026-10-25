"""A trilha v5 (do zero, 25/10/2026) a partir de spec/music.json: órgão de tubos (pedal, grande órgão, ostinato),
coral e o relógio. Substitui a trilha (score.py) e a camada rítmica (rhythm.py) das versões até a v4.
A música vem PRIMEIRO: tudo está numa grade de 80 BPM (15 ticks por tempo), e os eventos do filme caem nos tempos
fortes. A dinâmica é de órgão: registros somando (crescendo por soma) e a caixa expressiva de cada divisão.
Os tubos ficam como num órgão de verdade: notas de Dó, Ré, Mi… de um lado e Dó♯, Ré♯… do outro (o "lado C" e o
"lado C♯" da caixa), então o arpejo anda pelo estéreo sozinho. Renderizada uma vez e cortada em sgx_music_a
(0–600) e sgx_music_b (620–760)."""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

import act7
import dsp
import organ
from dsp import SR, TICK

ROOT = Path(__file__).resolve().parents[2]
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def hz(name):
    n, rest = name[0], name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 440.0 * 2 ** ((NOTE[n] + acc + 12 * (int(rest) - 4)) / 12)


def spec():
    return json.loads((ROOT / "spec/music.json").read_text(encoding="utf-8"))


def pos(p, M):
    """'A4:1' → tick (grade A, compasso 4, tempo 1; tempo fracionário vale). Número = tick absoluto."""
    if isinstance(p, (int, float)):
        return float(p)
    g, rest = p[0], p[1:]
    bar, beat = rest.split(":")
    G = M["grids"][g]
    return G["origin"] + (int(bar) * G["beats_per_bar"] + float(beat) - 1) * G["ticks_per_beat"]


def _at(steps, t, M):
    """Valor em vigor no tick t numa lista [[posição, valor], …]."""
    cur = steps[0][1]
    for p, v in steps:
        if t + 1e-6 >= pos(p, M):
            cur = v
    return cur


def side(f):
    """Lado da caixa: semitom par à esquerda, ímpar à direita (como os tubos de um órgão)."""
    midi = int(round(69 + 12 * np.log2(f / 440)))
    return -0.35 if midi % 2 == 0 else 0.35


LEGATO_TICKS = 1.2  # 60 ms: quanto uma nota invade a próxima na troca de acorde


def legato(notes):
    """v5.1 (retorno: a música "dá uns engasgos"): o organista não solta o acorde antes do próximo. Medido: em cada
    troca, os tubos paravam e os novos levavam até 0,2 s para falar (o tubo grande fala devagar), um buraco de
    8–11 dB. Agora (1) a nota que continua no acorde seguinte fica PRESA (não é tocada de novo) e (2) as outras
    invadem a próxima em 60 ms. Onde não há acorde seguinte (o vácuo, o fim do trecho), a nota acaba no tempo."""
    notes = sorted(notes)
    starts = {round(a, 3) for a, *_ in notes}
    out = []
    for a, b, nm, reg, lv in notes:
        tied = next((o for o in out if o[2] == nm and o[3] == reg and o[4] == lv and abs(o[1] - a) < 1e-3), None)
        if tied:
            tied[1] = b
        else:
            out.append([a, b, nm, reg, lv])
    for o in out:
        if round(o[1], 3) in starts:
            o[1] += LEGATO_TICKS
    return [tuple(o) for o in out]


@lru_cache(maxsize=1)
def render_full(end_tick=760):
    M = spec()
    R = M["registrations"]
    rng = np.random.default_rng(2014)  # Interestelar
    n = end_tick * TICK
    bus = {k: np.zeros((n, 2)) for k in ("pedal", "great", "ostinato", "choir", "clock")}

    def put(b, t0, x, p=0.0):
        st = int(round(t0 * TICK))
        e = min(n, st + len(x))
        if e > st:
            bus[b][st:e] += dsp.pan(x[: e - st], p) if x.ndim == 1 else x[: e - st]

    for a, b, nm, reg, lv in legato([(pos(e["at"], M), pos(e["to"], M), e["note"], e["reg"], 1.0) for e in M["pedal"]]):
        put("pedal", a, dsp.stereo(organ.note(hz(nm), int((b - a) * TICK), R[reg], rng, release=0.12), 0.3))
    for e in M["pulse"]:
        a, b = pos(e["from"], M), pos(e["to"], M)
        t, i = a, 0
        while t < b - 0.5:
            d = int(e["every"] * e["gate"] * TICK)
            put("pedal", t, dsp.stereo(organ.note(hz(e["notes"][i % len(e["notes"])]), d, R[e["reg"]], rng, 0.05), 0.3))
            t += e["every"]
            i += 1
    chord_notes = [(pos(e["at"], M), pos(e["to"], M), nm, e["reg"], e.get("level", 1.0)) for e in M["chords"] for nm in e["notes"]]
    for a, b, nm, reg, lv in legato(chord_notes):
        f = hz(nm)
        put("great", a, organ.note(f, int((b - a) * TICK), R[reg], rng) * lv, side(f))
    for o in M["ostinatos"]:
        a, b = pos(o["from"], M), pos(o["to"], M)
        t, i = a, 0
        while t < b - 0.5:
            sub = _at(o["subdivision"], t, M)
            tones = _at(o["tones"], t, M)
            f = hz(tones[o["cell"][i % len(o["cell"])]]) * 2 ** _at(o["octave"], t, M)
            d = int(min(sub * o["gate"], b - t) * TICK)
            put("ostinato", t, organ.note(f, d, R[_at(o["reg_steps"], t, M)], rng, 0.05) * o.get("level", 1.0), side(f))
            t += sub
            i += 1
    for e in M["choir"]:
        a, b = pos(e["at"], M), pos(e["to"], M)
        for j, nm in enumerate(e["notes"]):
            x = organ.choir(hz(nm), int((b - a) * TICK), rng, e["vowel"]) * e["level"]
            put("choir", a, x, -0.5 + j / max(1, len(e["notes"]) - 1))
    for e in M["clock"]:
        a, b = pos(e["from"], M), pos(e["to"], M)
        t, i = a, 0
        while t < b - 0.5:
            put("clock", t, organ.tick(rng, tock=i % 2 == 1) * e["level"], 0.12 if i % 2 else -0.12)
            t += e["every"]
            i += 1

    # a caixa expressiva: 0 → −20 dB e escuro (700 Hz); 1 → aberto
    tk = np.arange(n) / TICK
    sw = M["swell"]
    for k in ("pedal", "great", "ostinato"):
        ts, vs = zip(*sw[k])
        v = np.interp(tk, ts, vs)
        fc = 700 * 16 ** v
        bus[k] = np.stack([dsp.tv_filter(bus[k][:, c], fc, "low") for c in range(2)], axis=1) * (10 ** (-20 * (1 - v) / 20))[:, None]

    dry = bus["pedal"] * 0.9 + bus["great"] * 0.6 + bus["ostinato"] * 0.5 + bus["choir"] * 0.35
    dry += act7.world(n, 0, rng)  # a cratera e o vento, ouvidos de dentro (Ato VII)

    room = M["room"]
    out = np.zeros((n, 2))
    for a_t, b_t in M["segments"]:
        a, b = a_t * TICK, min(n, b_t * TICK)
        seg = np.zeros((n, 2))
        seg[a:b] = dry[a:b] + bus["clock"][a:b] * 0.25  # o relógio é seco e perto (o relógio de bolso de Mountains)
        x = seg * (1 - room["wet"]) + dsp.cathedral(seg, room, rng) * room["wet"] * 1.4
        x[b:] = 0
        if b_t == 268:
            r = int(1.0 * SR)  # v5.1: 0,35 s soava como corte; a caixa já vem fechando desde o 248
            x[b - r:b] *= np.cos(np.linspace(0, np.pi / 2, r))[:, None] ** 2
        if b_t == 240:
            x[b - int(0.004 * SR):b] *= np.linspace(1, 0, int(0.004 * SR))[:, None]
        if b_t == 600:
            x[b - int(0.05 * SR):b] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
        out += x
        out[a:b] += bus["clock"][a:b] * 0.25 * 0.6  # mais tique seco por cima da sala
    # Ato VII pelo ponto de audição: abafado → zumbido → drop-out → o estéreo abre no clarão
    out = act7.muffle(out, 0)
    out += act7.tinnitus(n, 0, rng)
    out *= act7.dropout(n, 0)[:, None]
    return act7.widen(out, 0)


def part(start_tick, end_tick):
    return render_full()[start_tick * TICK:end_tick * TICK].copy()
