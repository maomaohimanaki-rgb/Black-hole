"""Trilha (score) do buraco negro a partir de spec/score.json, a camada musical contínua por baixo dos efeitos.
v0.2.2 "escala" (pedido do usuário: o poder do buraco negro, angelical e destrutivo, sem explosão):
- pedal: o "32 pés resultante" dos órgãos grandes (fundamental + quinta: o ouvido reconstrói uma oitava
  abaixo) + batimento lento (a massa "respirando");
- órgão: síntese aditiva por registros (8' → mistura) que abrem com "stops", coro de 3 tubos e vento do fole;
- coral: "aah" sintetizado (vozes desafinadas, vibrato, formantes de soprano), o lado angelical no agudo;
- relógio: a mesma nota repetida (o tique de Interestelar), preso às meias-órbitas;
- Shepard–Risset descendo na queda: um som que cai para sempre;
- espaço: reverb de 9 s com pré-delay de 95 ms e reflexões esparsas, agudos abafados (distância);
  aplicado POR TRECHO para não atravessar o corte seco do 240 nem o silêncio de 600–619.
O filme inteiro é renderizado UMA vez (cache) e cortado em sgx_score_a (0–600) e sgx_score_b (620–760)."""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

import act7
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
    return 440.0 * 2 ** ((NOTE[n] + acc + 12 * (int(rest) - 4)) / 12)


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


def spans(events, n):
    """[(início, fim, evento)] em amostras: cada evento soa até o próximo (+ 0,4 s de cruzamento)."""
    out = []
    xf = int(0.4 * SR)
    for i, e in enumerate(events):
        a = e["t"] * TICK
        b = events[i + 1]["t"] * TICK if i + 1 < len(events) else n
        out.append((a, min(n, b + xf), e))
    return out


def xfade_env(m, attack, release=0.4):
    env = np.ones(m)
    a, r = min(m, int(attack * SR)), min(m, int(release * SR))
    env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    env[m - r:] = np.minimum(env[m - r:], np.cos(np.linspace(0, np.pi / 2, r)) ** 2)
    return env


# ------------------------------------------------------------------ vozes

# (múltiplo da fundamental, peso, a partir de quanto "stops" entra)
RANKS = [(1.0, 1.0, 0.0), (2.0, 0.55, 0.12), (3.0, 0.32, 0.3), (4.0, 0.3, 0.45), (6.0, 0.16, 0.65), (8.0, 0.12, 0.8), (0.5, 0.45, 0.55)]


def organ_note(f, n, stops, rng):
    """Nota de órgão: registros que abrem com stops (0–1), coro de 3 tubos e vento do fole."""
    t = time(n)
    out = np.zeros(n)
    for mult, w, gate in RANKS:
        fm = f * mult
        if fm > 9000 or fm < 28:  # abaixo de 28 Hz ninguém ouve
            continue
        open_ = np.clip((stops - gate) / 0.15, 0, 1) if gate > 0 else 1.0
        for det in (-0.0018, 0.0, 0.0021):
            out += w * open_ * np.sin(2 * np.pi * fm * (1 + det) * t + rng.uniform(0, 2 * np.pi)) / 3
    out += 0.012 * dsp.bp(dsp.white(rng, n), max(40, f * 0.8), min(16000, f * 6))
    return out / 5.0


def pedal_note(f, n, rng):
    """O "32 pés resultante": f + quinta (1,5 f) faz o ouvido ouvir f/2, mais dois tubos quase iguais
    batendo devagar. Para o celular (P-48), o 2º e o 3º harmônicos carregam a nota."""
    t = time(n)
    beat = 1 + 0.18 * np.sin(2 * np.pi * 0.23 * t + rng.uniform(0, 6))  # a massa respirando
    x = (np.sin(2 * np.pi * f * t) + 0.75 * np.sin(2 * np.pi * 1.5 * f * t + 0.4)
         + 0.45 * np.sin(2 * np.pi * f * 1.003 * t)
         + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.22 * np.sin(2 * np.pi * 3 * f * t))
    return dsp.sat(x * 0.45, 1.6) * beat


def choir_note(f, n, rng, voices=6):
    """'Aah' de coral: vozes desafinadas (±9 cents) com vibrato, por formantes de soprano/contralto."""
    t = time(n)
    src = np.zeros(n)
    for _ in range(voices):
        cents = rng.uniform(-9, 9)
        vib = 1 + 0.0045 * np.sin(2 * np.pi * rng.uniform(4.6, 5.6) * t + rng.uniform(0, 6)) * np.clip(t / 1.2, 0, 1)
        ph = np.cumsum(f * 2 ** (cents / 1200) * vib) / SR + rng.uniform(0, 1)
        src += 2 * (ph % 1.0) - 1  # dente-de-serra: rico em harmônicos para os formantes
    src /= voices
    breath = dsp.bp(dsp.white(rng, n), 2000, 7000) * 0.04
    form = ((800, 7, 1.0), (1150, 8, 0.55), (2900, 12, 0.3), (3900, 14, 0.12)) if f > 500 else ((700, 6, 1.0), (1100, 8, 0.6), (2600, 10, 0.25))
    out = sum(a * dsp.resonator(src + breath, fr, q) for fr, q, a in form)
    return dsp.lp(out, 6000) * 0.6


def clock(f, dur_s, accent=False):
    """O tique: nota curta e limpa (piano abafado / celesta), a mesma nota repetida."""
    n = int(dur_s * SR)
    t = time(n)
    env = np.clip(t / 0.003, 0, 1) * np.exp(-t / (0.22 if accent else 0.14))
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.05) + 0.08 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.03)
    return x * env * (1.3 if accent else 1.0)


def risset(n, cfg, rng):
    """Glissando de Shepard–Risset: oitavas deslizando juntas sob uma janela fixa no espectro.
    Descendo: cada voz cai, some no grave e renasce no agudo, então a queda nunca termina."""
    t = time(n)
    V = cfg["voices"]
    sign = -1 if cfg["direction"] == "down" else 1
    pos = (np.arange(V)[:, None] / V + sign * cfg["octaves_per_second"] * t[None, :] / V) % 1.0
    lo = cfg["center_hz"] / 2 ** (V / 2)
    out = np.zeros(n)
    for v in range(V):
        fv = lo * 2 ** (pos[v] * V)
        amp = np.sin(np.pi * pos[v]) ** 2  # janela: some nas pontas
        out += amp * np.sin(2 * np.pi * np.cumsum(fv) / SR + rng.uniform(0, 6))
    return out / V * 2


def _ostinato_times(o, half_orbits):
    """[(tick, é_tempo_forte)]."""
    if o["on"] == "half_orbits":
        h = [x for x in half_orbits if o["from"] <= x <= o["to"]]
        ts = []
        for i, x in enumerate(h):
            ts.append((float(x), True))
            if i + 1 < len(h):
                for k in range(1, o.get("subdivide", 1)):
                    ts.append((x + (h[i + 1] - x) * k / o["subdivide"], False))
        return ts
    if o["on"] == "every":
        return [(float(x), False) for x in np.arange(o["from"], o["to"] + 1e-9, o["period_ticks"])]
    if o["on"] == "accel":
        p0, p1 = o["period_ticks"]
        ts, t = [], float(o["from"])
        while t <= o["to"]:
            ts.append((t, len(ts) % 4 == 0))
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
    D = {k: sample_curve(v, ticks) for k, v in S["dynamics"].items()}

    pedal = np.zeros(n)
    for a, b, e in spans(S["pedal"], n):
        pedal[a:b] += pedal_note(freq(e["note"]), b - a, rng) * xfade_env(b - a, 0.6)
    pedal *= D["pedal"]

    organ = np.zeros(n)
    for a, b, e in spans(S["organ"], n):
        m = b - a
        organ[a:b] += sum(organ_note(freq(nm), m, np.full(m, e["stops"]), rng) for nm in e["notes"]) * xfade_env(m, 0.35)
    organ *= D["organ"]

    choir = np.zeros(n)
    for a, b, e in spans(S["choir"], n):
        m = b - a
        choir[a:b] += sum(choir_note(freq(nm), m, rng) for nm in e["notes"]) / max(1, len(e["notes"])) ** 0.5 * xfade_env(m, 0.9)
    choir *= D["choir"]

    ost = np.zeros(n)
    for o in S["ostinato"]:
        ts = _ostinato_times(o, LY["binary"]["half_orbit_ticks"])
        for i, (t0, acc) in enumerate(ts):
            gap = (ts[i + 1][0] - t0) if i + 1 < len(ts) else 6
            name = o["accent"] if acc and "accent" in o else o["notes"][i % len(o["notes"])]
            p = clock(freq(name), max(0.15, gap / 20 * 1.8), accent=acc)
            st = int(t0 * TICK)
            e_ = min(n, st + len(p))
            ost[st:e_] += p[: e_ - st] * o["level"]

    ris = np.zeros(n)
    rc = S["risset"]
    a, b = rc["from"] * TICK, rc["to"] * TICK
    ris[a:b] = risset(b - a, rc, rng) * rc["level"] * sample_curve(rc["dynamics"], ticks[a:b])

    ris += act7.risset_up(n, 0, rng, risset, sample_curve)  # v0.2.6: a subida sem fim do Ato VII

    # Estéreo: pedal no centro (o grave largo vem do reverb), coral e órgão abertos, relógio um pouco à direita.
    dry = (dsp.stereo(pedal) * 0.9 + dsp.stereo(organ, 0.6) + dsp.stereo(choir, 1.0) * 0.8
           + dsp.pan(ost * 0.5, 0.25) + dsp.stereo(ris, 0.8))
    dry += act7.world(n, 0, rng)  # v0.2.6: a cratera e o vento, ouvidos de dentro

    R = S["reverb"]
    T = S["tape_stop"]
    out = np.zeros((n, 2))
    for a_t, b_t in S["segments"]:
        a, b = a_t * TICK, min(n, b_t * TICK)
        seg = np.zeros((n, 2))
        seg[a:b] = dry[a:b]
        x = seg * (1 - R["wet"]) + dsp.cathedral(seg, R, rng) * R["wet"] * 1.4
        x[b:] = 0
        if b_t == 268:
            # o vazio respira: a cauda do Ato III some suave até o 268 (quase-silêncio até o 279)
            r = int(0.35 * SR)
            x[b - r:b] *= np.cos(np.linspace(0, np.pi / 2, r))[:, None] ** 2
        if b_t == 240:
            x[b - int(0.004 * SR):b] *= np.linspace(1, 0, int(0.004 * SR))[:, None]  # corte seco: a fusão assume
        if b_t == 600:
            # parada de fita no Ato VI: desacelera e afina para baixo, termina em zero exato no 600
            ta, tb = T["from"] * TICK, T["to"] * TICK
            rate = np.linspace(T["rate"][0], T["rate"][1], tb - ta)
            x[ta:tb] = dsp.varispeed(x[ta:tb], rate)
            x[ta:tb] *= np.interp(np.arange(tb - ta), [0, (tb - ta) * 0.75, tb - ta - 1], [1, 0.5, 0])[:, None]
        out += x
    # v0.2.6: Ato VII pelo ponto de audição: abafado → zumbido → drop-out → o estéreo abre no clarão
    out = act7.muffle(out, 0)
    out += act7.tinnitus(n, 0, rng)
    out *= act7.dropout(n, 0)[:, None]
    return act7.widen(out, 0)


def part(start_tick, end_tick):
    return render_full()[start_tick * TICK:end_tick * TICK].copy()
