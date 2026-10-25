"""Camada rítmica (rhythmic sound design) a partir de spec/rhythm.json: a terceira camada, entre a trilha e os
efeitos (v0.2.5, pedido do usuário: "como em Mountains: score + SFX + o ritmo que une os dois").
Instrumentos sintetizados (nada de sample):
- bass:   pulso de baixo (dente-de-serra + sub, filtro fechando a cada nota: o "bombeio");
- tom:    golpe grave tipo taiko (seno com queda de altura + corpo de ruído), afinado;
- shaker: grão de ruído agudo com ataque suave (não é clique);
- dust:   poeira granular: grãos ressonantes miúdos, espalhados no estéreo;
- tick:   tique de madeira/vidro afinado (o relógio que respira);
- riser:  subida de expectativa que termina SECA no tick do impacto.
Os padrões caem numa grade que vem da matemática do filme (meias-órbitas, Doppler de 1 Hz, aceleração da maré,
dilatação do tempo). O reverb é o da trilha (dsp.cathedral), por trecho, respeitando o corte do 240, o vazio
de 268–279 e o preto de 600–619. Renderizado uma vez e cortado em sgx_rhythm_a (0–600) e sgx_rhythm_b (620–760)."""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

import dsp
from dsp import SR, TICK, time
from score import freq

ROOT = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------ instrumentos


def bass(f, dur, rng, muffle=None):
    n = int(dur * SR)
    t = time(n)
    x = 0.6 * dsp.saw_bl(f, n, 20) + 0.8 * np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f / 2 * t)
    x = dsp.tv_filter(x, np.interp(t, [0, 0.08], [1400, 260]), "low")
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t / max(0.06, dur * 0.45))
    y = dsp.sat(x * env * 1.4, 1.6)
    return dsp.lp(y, muffle) if muffle else y


def tom(f, rng, decay=0.55, muffle=None):
    n = int((decay * 4 + 0.1) * SR)
    t = time(n)
    pitch = f * (1 + 1.4 * np.exp(-t / 0.035))  # o couro: a altura cai no ataque
    body = np.sin(dsp.phase_osc(pitch)) + 0.3 * np.sin(dsp.phase_osc(pitch * 2.3)) * np.exp(-t / 0.08)
    skin = dsp.bp(dsp.white(rng, n), f * 3, min(4000, f * 40)) * np.exp(-t / 0.03) * 0.6
    y = dsp.sat((body * np.exp(-t / decay) + skin) * np.clip(t / 0.002, 0, 1) * 1.3, 1.8)
    return dsp.lp(y, muffle) if muffle else y


def shaker(rng):
    n = int(0.12 * SR)
    t = time(n)
    env = np.clip(t / 0.012, 0, 1) * np.exp(-np.maximum(t - 0.012, 0) / 0.035)
    return dsp.bp(dsp.white(rng, n), 4000, 9000) * env * 0.5


def dust(rng):
    n = int(0.05 * SR)
    imp = np.zeros(n)
    imp[0] = 1.0
    f = rng.uniform(1500, 5000)
    return dsp.resonator(imp, f, 30) * 0.8


def tick(f, rng):
    n = int(0.3 * SR)
    t = time(n)
    imp = np.zeros(n)
    imp[:30] = rng.standard_normal(30) * np.hanning(60)[30:]
    wood = dsp.resonator(imp, f, 80) * 6
    tone = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06) * 0.5
    return (wood + tone) * np.clip(t / 0.0015, 0, 1)


def riser(length_ticks, rng, soft=False):
    """Subida que termina SECA no fim: ruído num passa-banda que sobe + o grave chupado para dentro."""
    n = int(length_ticks * TICK)
    t = time(n)
    u = t / t[-1]
    fc = (250 if soft else 400) * ((4000 if soft else 9000) / (250 if soft else 400)) ** (u ** 1.6)
    x = dsp.tv_filter(dsp.white(rng, n), fc, "band", width=1.0) * u ** 2.2
    suck = np.sin(dsp.phase_osc(np.interp(u, [0, 1], [30, 70]))) * u ** 3 * 0.6  # o ar sendo puxado para dentro
    y = (x + suck) * (0.6 if soft else 1.0)
    y[-int(0.003 * SR):] *= np.linspace(1, 0, int(0.003 * SR))
    return y


# ------------------------------------------------------------------ grades


def grid(g, half_orbits, rng):
    k = g["type"]
    if k == "list":
        return [float(x) for x in g["ticks"]]
    if k == "every":
        ts = list(np.arange(g["from"], g["to"] + 1e-9, g["period"]))
        j = g.get("jitter", 0)
        return [float(x + rng.uniform(-j / 2, j / 2)) if j else float(x) for x in ts]
    if k == "half_orbits":
        h = [x for x in half_orbits if g["from"] <= x <= g["to"]]
        out = []
        for i, x in enumerate(h):
            out.append(float(x))
            if i + 1 < len(h):
                out += [x + (h[i + 1] - x) * s / g["subdivide"] for s in range(1, g["subdivide"])]
        return out
    if k == "accel":
        p0, p1 = g["periods"]
        out, t = [], float(g["from"])
        while t <= g["to"]:
            out.append(t)
            u = (t - g["from"]) / (g["to"] - g["from"])
            t += p0 + (p1 - p0) * u
        return out
    raise ValueError(k)


def _level(pts, t):
    ts, vs = zip(*pts)
    return float(np.interp(t, ts, vs))


def _note(notes, t, i):
    if isinstance(notes[0], list):
        cur = notes[0][1]
        for tt, nm in notes:
            if t >= tt:
                cur = nm
        return cur
    return notes[i % len(notes)]


@lru_cache(maxsize=1)
def render_full(end_tick=760):
    R = json.loads((ROOT / "spec/rhythm.json").read_text(encoding="utf-8"))
    S = json.loads((ROOT / "spec/score.json").read_text(encoding="utf-8"))
    LY = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(1915)  # a relatividade geral
    n = end_tick * TICK
    dry = np.zeros((n, 2))

    def put(t0, x, pan=0.0, end_at=None):
        st = int(round(t0 * TICK)) if end_at is None else end_at - len(x)
        st = max(0, st)
        e = min(n, st + len(x))
        if e > st:
            dry[st:e] += dsp.pan(x[: e - st], pan)

    for p in R["patterns"]:
        ts = grid(p["grid"], LY["binary"]["half_orbit_ticks"], rng)
        for i, t0 in enumerate(ts):
            lv = _level(p["level"], t0)
            inst = p["inst"]
            gap = (ts[i + 1] - t0) / 20 if i + 1 < len(ts) else 0.25
            if inst == "bass":
                put(t0, bass(freq(_note(p["notes"], t0, i)), max(0.08, gap * 0.95), rng, p.get("muffle")) * lv * 0.75, 0.0)
            elif inst == "tom":
                put(t0, tom(freq(_note(p["notes"], t0, i)), rng, p.get("decay", 0.55), p.get("muffle")) * lv * 1.1, rng.uniform(-0.15, 0.15))
            elif inst == "shaker":
                put(t0, shaker(rng) * lv * 0.5, 0.35 if i % 2 else -0.35)
            elif inst == "dust":
                put(t0, dust(rng) * lv * 0.35, rng.uniform(-0.8, 0.8))
            elif inst == "tick":
                put(t0, tick(freq(_note(p["notes"], t0, i)), rng) * lv * 0.4, rng.uniform(-0.5, 0.5))
            elif inst == "riser":
                x = riser(p["length_ticks"], rng, p.get("soft", False)) * lv * 0.6
                put(t0, x, 0.0, end_at=int(round(t0 * TICK)))
            else:
                raise ValueError(inst)

    # reverb da trilha por trecho (mesmos cortes da direção)
    out = np.zeros((n, 2))
    wet = R["reverb_wet"]
    for a_t, b_t in S["segments"]:
        a, b = a_t * TICK, min(n, b_t * TICK)
        seg = np.zeros((n, 2))
        seg[a:b] = dry[a:b]
        x = seg * (1 - wet) + dsp.cathedral(seg, S["reverb"], rng) * wet * 1.4
        x[b:] = 0
        if b_t == 268:
            r = int(0.35 * SR)
            x[b - r:b] *= np.cos(np.linspace(0, np.pi / 2, r))[:, None] ** 2
        if b_t in (240, 600):
            r = int(0.004 * SR) if b_t == 240 else int(0.15 * SR)
            x[b - r:b] *= np.linspace(1, 0, r)[:, None]
        out += x
    return out


def part(start_tick, end_tick):
    return render_full()[start_tick * TICK:end_tick * TICK].copy()
