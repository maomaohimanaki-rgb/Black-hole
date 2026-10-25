"""O diretor (v0.4.0): a camada de dramaturgia, lida de spec/dramaturgy.json.
Não cria som: dirige o que já existe, no tempo ABSOLUTO do filme, para cada stem conforme o papel dele:
  world  → relógio do mundo (soluços, inspiração, contorção, congelamento) + passa-alta (o grave sugado) +
           passa-baixa (o desvio para o vermelho) + pente (o espaço-tempo esticando) + fader de tensão;
  signal → só os soluços (que devolvem o tempo: a fase do chirp continua batendo com a órbita);
  resto  → intacto (eventos e corpo: a receita já nasce dirigida).
Por que no stem e não no mix: o jogo toca cada stem separado. Toda operação aqui é LINEAR e variante no tempo
(ganho, filtro, reamostragem, pente), então aplicar a mesma cadeia em cada stem do mundo é o mesmo que aplicar
no barramento do mundo, e o filme no jogo soa igual ao mixdown.
Teoria e vocabulário das fases: docs/SOUND_DIRECTION.md."""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

import dsp
from dsp import SR, TICK

ROOT = Path(__file__).resolve().parents[2]
NEUTRAL_HP = 12.0     # Hz: transparente (só tira o DC que a taxa perto de zero deixaria)
NEUTRAL_LP = 20000.0


def spec():
    return json.loads((ROOT / "spec/dramaturgy.json").read_text(encoding="utf-8"))


def role(sid):
    R = spec()["roles"]
    return "world" if sid in R["world"] else "signal" if sid in R["signal"] else "event"


def warp_phase(impact):
    for M in spec()["moments"]:
        if M["impact"] == impact:
            return next(P for P in M["phases"] if P["type"] == "warp")
    raise KeyError(impact)


def _smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def _seg(tk, a, b):
    return (tk >= a) & (tk < b)


@lru_cache(maxsize=2)
def curves(end_tick=760):
    """Curvas por amostra, tick 0 → end_tick: rate (mundo), rate_signal (chirp), gain_db, hp, lp e o pente."""
    D = spec()
    n = end_tick * TICK
    tk = np.arange(n) / TICK
    ts, vs = zip(*D["tension_db"]["keys"])
    gain_db = np.interp(tk, ts, vs)
    rate = np.ones(n)
    rate_sig = np.ones(n)
    hp = np.full(n, NEUTRAL_HP)
    lp = np.full(n, NEUTRAL_LP)
    comb = []
    for M in D["moments"]:
        imp = M["impact"]
        for P in M["phases"]:
            k = P["type"]
            if k == "hiccup":
                # soluço que devolve o tempo: a taxa afunda e depois corre na mesma medida (∫(r − 1) = 0)
                for t0, d, L in zip(P["ticks"], P["depth"], P["length_ticks"]):
                    m = _seg(tk, t0, t0 + L)
                    u = (tk[m] - t0) / L
                    dip = -d * np.sin(2 * np.pi * u) * (1 - 0.15 * np.cos(2 * np.pi * u))
                    dip -= dip.mean()
                    rate[m] += dip
                    rate_sig[m] += dip
            elif k == "inhale":
                a, b = P["from"], P["to"]
                m = _seg(tk, a, imp)
                u = _smooth((tk[m] - a) / (b - a))
                h0, h1 = P["highpass_hz"]
                hp[m] = h0 * (h1 / h0) ** (u ** 1.5)  # o grave vai embora cada vez mais rápido
                g0, g1 = P.get("gain_db", [0, 0])
                gain_db[m] += g0 + (g1 - g0) * u
                if "rate_to" in P:
                    rate[m] = 1 + (P["rate_to"] - 1) * u ** 2
            elif k == "vacuum":
                a, b = P["from"], P["to"]
                ramp = 0.06  # ticks (3 ms): sem estalo na entrada e na saída do vácuo
                gain_db += P["gain_db"] * np.clip(np.minimum((tk - a) / ramp, (b - tk) / ramp), 0, 1) * _seg(tk, a - ramp, b + ramp)
            elif k == "warp":
                a = P["from"]
                m = tk >= a
                kt, kv = zip(*P["rate_keys"])
                base = PchipInterpolator(kt, kv, extrapolate=False)(np.clip(tk[m], kt[0], kt[-1]))
                W = P["wobble"]
                dt = (tk[m] - kt[1]) / 20
                wob = np.where(dt > 0, W["depth"] * np.exp(-dt / W["tau_s"]) * np.sin(2 * np.pi * W["hz"] * dt), 0.0)
                rate[m] = np.clip(base * (1 + wob), 0, None)
                gt, gv = zip(*P["gain_db"])
                gain_db[m] += np.interp(tk[m], gt, gv)
                lt, lv = zip(*P["lowpass_hz"])
                lp[m] = np.exp(np.interp(tk[m], lt, np.log(lv)))
                # o golpe devolve o grave (release), mas o grave do mundo esticado vira lama embaixo do golpe:
                # o mundo contorcido mora nos médios; o sub depois do 540 é do golpe e do coração
                ht, hv = zip(*P.get("highpass_hz", [[a, NEUTRAL_HP]]))
                hp[m] = np.interp(tk[m], ht, hv)
                if "comb" in P:
                    comb.append(P["comb"])
            elif k == "release":
                pass  # o fim da inspiração e do vácuo já é a volta do mundo inteiro
            else:
                raise ValueError(f"fase desconhecida: {k}")
    sig_gain_db = np.interp(tk, ts, vs)
    return {"tk": tk, "rate": rate, "sig_gain_db": sig_gain_db, "rate_signal": rate_sig, "gain_db": gain_db, "hp": hp, "lp": lp, "comb": comb}


def world_clock(rate):
    """P(t): onde o relógio do mundo está (em amostras) quando o ouvinte está em t. Com r = 1, P = t."""
    P = np.empty_like(rate)
    P[0] = 0.0
    np.cumsum(rate[:-1], out=P[1:])
    return P


def warp(x, P_abs, start):
    """Lê o stem pelo relógio do mundo: saída(t) = x(P(t) − início). Afina e desacelera juntos, como fita."""
    n = len(x)
    pos = P_abs[start:start + n] - start
    ok = (pos >= 0) & (pos <= n - 1)
    idx = np.arange(n)
    y = np.zeros_like(x)
    for c in range(x.shape[1]):
        y[ok, c] = np.interp(pos[ok], idx, x[:, c])
    return y


def warp_from(x, start_tick, follow=1.0):
    """Um som que NASCE em start_tick e vive no relógio do mundo dali em diante (a cauda do golpe do 540).
    follow < 1: segue o relógio só em parte (taxa = 1 − follow·(1 − taxa do mundo))."""
    P = world_clock(1 - follow * (1 - curves()["rate"]))
    a = start_tick * TICK
    pos = P[a:a + len(x)] - P[a]
    idx = np.arange(len(x))
    return np.stack([np.interp(pos, idx, x[:, c], right=0.0) for c in range(x.shape[1])], axis=1)


def comb_sweep(x, C, start):
    """O espaço-tempo esticando: pente com atraso que varre (flanger lento) e realimentação, só na janela."""
    a = max(0, int(C["from"] * TICK) - start)
    b = min(len(x), int(C["to"] * TICK) - start)
    if b <= a:
        return x
    m = b - a
    u = np.linspace(0, 1, m)
    d = np.interp(u, [0, 1], C["delay_ms"]) / 1000 * SR
    env = np.sin(np.pi * u) ** 0.5  # entra e sai sem degrau
    y = x.copy()
    seg = x[a:b]
    out = seg.copy()
    fb = C["feedback"]
    for c in range(x.shape[1]):
        buf = out[:, c]
        src = seg[:, c]
        for i in range(m):
            j = i - d[i]
            if j >= 1:
                j0 = int(j)
                fr = j - j0
                buf[i] = src[i] + fb * env[i] * (buf[j0] * (1 - fr) + buf[j0 + 1] * fr)
    y[a:b] = seg * (1 - C["mix"] * env[:, None]) + out * (C["mix"] * env[:, None])
    return y


def _filt(x, fc, btype, neutral):
    if (np.abs(fc - neutral) < 1e-6).all():
        return x
    return np.stack([dsp.tv_filter(x[:, c], fc, btype, block=128) for c in range(x.shape[1])], axis=1)


def apply(x, sid, start_tick):
    """A cadeia do papel do stem, no tempo absoluto. x: (n, 2), já masterizado e conferido na ida e volta."""
    r = role(sid)
    if r == "event":
        return x
    C = curves()
    start = start_tick * TICK
    sl = slice(start, start + len(x))
    if r == "signal":
        g = 10 ** (C["sig_gain_db"][sl] / 20)  # o fader de tensão sim, o vácuo não: o chirp É o riser
        return warp(x, world_clock(C["rate_signal"]), start) * g[:, None]
    y = warp(x, world_clock(C["rate"]), start)
    for cb in C["comb"]:
        y = comb_sweep(y, cb, start)
    y = _filt(y, C["hp"][sl], "high", NEUTRAL_HP)
    y = _filt(y, C["lp"][sl], "low", NEUTRAL_LP)
    g = 10 ** (C["gain_db"][sl] / 20)
    g[C["gain_db"][sl] <= -89] = 0.0
    return y * g[:, None]
