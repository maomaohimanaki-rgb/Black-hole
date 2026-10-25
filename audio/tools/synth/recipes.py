"""Receitas dos 16 efeitos do buraco negro (docs/AUDIO_DESIGN.md §3) + a trilha.
v0.2.3 "efeitos de cinema" (retorno do usuário: a trilha ficou boa, mas os efeitos soavam "SFX de YouTube
de 2015": secos, fora do tom, cliques e bitcrush por cima de uma catedral). Três regras para todos:
  1. o MESMO espaço da trilha: todo efeito passa pela catedral (dsp.cathedral, spec/score.json → reverb);
  2. o MESMO tom: afinados em Ré, nas notas dos acordes da trilha naquele instante;
  3. impacto TONAL em vez de explosão: "braam" de metais graves afinado, reverb invertido nas subidas,
     brilhos afinados no lugar de cliques de ruído.
Cada receita devolve Parts: uma "cama" e UM EVENTO POR ONSET PEDIDO. O render.py calibra os ganhos até o
analisador achar cada onset no tick e com o rms_norm pedidos. Toda operação depois da soma tem que ser
LINEAR (reverb, varispeed, pan, filtro): por isso a saturação fica DENTRO de cada parte."""
import json
from pathlib import Path

import numpy as np

import dsp
from dsp import SR, TICK, time

ROOT = Path(__file__).resolve().parents[2]
REVERB = json.loads((ROOT / "spec/score.json").read_text(encoding="utf-8"))["reverb"]
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def hz(name):
    """'C#3', 'Bb1', 'A4' → Hz (A4 = 440)."""
    n, rest = name[0], name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 440.0 * 2 ** ((NOTE[n] + acc + 12 * (int(rest) - 4)) / 12)


class Parts:
    def __init__(self, n):
        self.n = n
        self.bed = np.zeros((n, 2))
        self.events = {}
        self.marks = []  # (tick, Hz): brilho afinado de articulação, aplicado DEPOIS da calibração (nível fixo)

    def add_bed(self, x):
        self.bed += x if x.ndim == 2 else dsp.stereo(x)

    def add_event(self, tick, x):
        x = x if x.ndim == 2 else dsp.stereo(x)
        self.events[tick] = self.events.get(tick, 0) + x

    def mark(self, tick, note="D7"):
        self.marks.append((tick, hz(note)))

    def map(self, f):
        """Aplica uma operação LINEAR a tudo (cama e eventos)."""
        self.bed = f(self.bed)
        self.events = {k: f(v) for k, v in self.events.items()}
        return self

    def start_event(self, tick, ticks=1.5):
        """Onset no começo do arquivo sem ataque próprio: a janela inicial da cama vira o evento."""
        w = np.zeros(self.n)
        a = int(ticks * TICK)
        w[:a] = 1.0
        w[a:a + TICK] = np.linspace(1, 0, TICK)[: max(0, min(TICK, self.n - a))]
        ev = self.bed * w[:, None]
        self.bed = self.bed * (1 - w)[:, None]
        self.add_event(tick, ev)

    def room(self, wet, rng, tail_fade=0.25):
        """O espaço da trilha: a mesma catedral (pré-delay, cauda) para cama e eventos. A cauda some suave no
        fim do arquivo (o arquivo não pode terminar num degrau)."""
        seed = int(rng.integers(1 << 30))
        r = max(1, int(tail_fade * SR))

        def g(x):
            y = x * (1 - wet) + dsp.cathedral(x, REVERB, np.random.default_rng(seed)) * wet * 1.4
            y[-r:] *= np.cos(np.linspace(0, np.pi / 2, r))[:, None] ** 2
            return y
        return self.map(g)


def rng_for(sid):
    # semente fixa por som (hash() do Python muda entre execuções): build idempotente
    return np.random.default_rng(sum(map(ord, sid)) * 7919)


def at(tick, start):
    return (tick - start) * TICK


def sl(n, start):
    """Comprimento disponível a partir de start."""
    return max(0, n - start)


def place(n, start, x):
    out = np.zeros(n)
    m = min(len(x), n - start)
    if m > 0:
        out[start:start + m] = x[:m]
    return out


# ------------------------------------------------------------------ instrumentos de cinema


def braam(freqs, m, rng, open_s=0.35, decay=1.2, bright=2400):
    """Impacto de metais graves (o "braam"): dentes-de-serra desafinados em notas da tonalidade, filtro abrindo,
    saturação. É grande sem ser explosão."""
    t = time(m)
    x = np.zeros(m)
    for f in freqs:
        for det in (-0.006, 0.0, 0.007):
            x += dsp.saw_bl(f * (1 + det), m, 30)
    x /= 3 * len(freqs)
    fc = np.interp(t, [0, open_s, open_s + 1.5], [180, bright, bright * 0.4])
    x = dsp.tv_filter(x, fc, "low")
    env = np.clip(t / 0.012, 0, 1) * np.exp(-np.maximum(t - 0.1, 0) / decay)
    return dsp.sat(x * env * 2.2, 2.0)


def sub_drop(f0, f1, m, dur=0.6, decay=0.7):
    t = time(m)
    ph = dsp.phase_osc(np.interp(t, [0, dur], [f0, f1]))
    body = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph)  # 2º/3º harmônicos para o celular (P-48)
    return dsp.sat(body * 0.8, 1.6) * np.clip(t / 0.01, 0, 1) * np.exp(-t / decay)


def bell(f, m, rng, decay=1.6, partials=((1, 1.0), (2.0, 0.45), (3.0, 0.22), (4.2, 0.12), (5.4, 0.06))):
    """Sino/vidro AFINADO (parciais quase harmônicos): o "brilho de lente" no tom da trilha."""
    t = time(m)
    x = np.zeros(m)
    for k, (mult, a) in enumerate(partials):
        x += a * np.sin(2 * np.pi * f * mult * (1 + 0.0007 * k) * t + rng.uniform(0, 6)) * np.exp(-t / (decay / (1 + 0.6 * k)))
    return x * np.clip(t / 0.004, 0, 1)


def bloom(f, m, rng, attack=0.05, decay=0.7):
    """Floração tonal: um acorde de órgão/coro que acende (sem ataque de ruído)."""
    t = time(m)
    x = np.zeros(m)
    for mult, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18), (6, 0.08)):
        for det in (-0.002, 0.002):
            x += a * np.sin(2 * np.pi * f * mult * (1 + det) * t + rng.uniform(0, 6))
    air = dsp.bp(dsp.white(rng, m), f * 2, min(15000, f * 10)) * 0.08
    return (x / 4 + air) * np.clip(t / attack, 0, 1) * np.exp(-np.maximum(t - attack, 0) / decay)


def reverse_swell(notes, m, rng, length_s=1.2):
    """Reverb invertido de um acorde: o som cresce PARA DENTRO do impacto (a subida de trailer, no tom)."""
    k = min(m, int(length_s * SR))
    src = np.zeros(int(0.08 * SR))
    tt = time(len(src))
    for nm in notes:
        src += np.sin(2 * np.pi * hz(nm) * tt) * np.exp(-tt / 0.03)
    src = np.concatenate([src, np.zeros(k)])
    wet = dsp.mono(dsp.cathedral(dsp.stereo(src), REVERB, rng))[:k]
    out = np.zeros(m)
    out[m - k:] = wet[::-1] * np.linspace(0, 1, k) ** 1.5
    return out / (np.abs(out).max() + 1e-12)


def glint(f, m, decay=0.35):
    """Brilho curto afinado (substitui o clique de ruído)."""
    t = time(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.05)) * np.clip(t / 0.002, 0, 1) * np.exp(-t / decay)


# ------------------------------------------------------------------ Ato I


def void_in(s):
    """O ar sendo sugado: ruído rosa crescendo para dentro, o pedal da trilha se insinuando por baixo, e a
    massa chegando num sub que cai até o Ré1."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    cut = at(19, S) - int(0.03 * SR)
    noise = np.stack([dsp.pink(rng, n), dsp.pink(rng, n)], axis=1)
    fc = np.interp(t, [0, 19 / 20], [300, 1200])
    noise = np.stack([dsp.tv_filter(noise[:, c], fc, "low") for c in range(2)], axis=1)
    sw = np.interp(t, [0, 12 / 20, 18.6 / 20], [0.25, 0.6, 1.0]) ** 1.5
    sw[cut:] *= np.exp(-np.arange(n - cut) / (0.01 * SR))  # prende a respiração no 19
    hum = (np.sin(2 * np.pi * hz("D2") * t) + 0.6 * np.sin(2 * np.pi * hz("A2") * t)) * np.interp(t, [0, 0.9], [0, 0.15])
    hum[cut:] *= np.exp(-np.arange(n - cut) / (0.02 * SR))
    P.add_bed(noise * sw[:, None] * 0.5 + dsp.stereo(hum))
    P.add_event(0, dsp.stereo(dsp.lp(dsp.white(rng, n), 600) * dsp.env_ad(n, 0.03, 0.15), 0.6))
    i12 = at(12, S)
    sub = place(n, i12, sub_drop(hz("D2"), hz("D1"), sl(n, i12), 0.4, 0.3))
    sub[cut:] = 0
    P.add_event(12, dsp.stereo(sub))
    P.mark(12, "A6")
    i19 = at(19, S)
    gasp = dsp.bp(dsp.white(rng, n), 900, 3500) * dsp.env_ad(n, 0.004, 0.08, i19)
    P.room(0.2, rng)
    # a respiração presa no 19 corta também a sala (o gasp do 19 fica)
    hold = np.ones(n)
    hold[cut:] = np.exp(-np.arange(n - cut) / (0.01 * SR))
    P.bed *= hold[:, None]
    for k in (0, 12):
        P.events[k] = P.events[k] * hold[:, None]
    P.add_event(19, dsp.stereo(gasp, 0.5))
    P.mark(19, "D7")
    return P


def point(s, root="A", ratio=1.0):
    """Nascer de um ponto. v0.2.7 (identidade: "o plim parecia acertar questão do JLPT"): sem sino. Um buraco
    negro aparecendo é a FUSÃO TOCADA DE TRÁS PRA FRENTE: o gesto GW150914 invertido (a nota DESCE de 250 a
    35 Hz, "PWOOOM") com o sub; os brilhos de lente são o mesmo gesto como sopro de ar, sem nota.
    O gêmeo é o mesmo nascimento um tom abaixo (×0,85)."""
    import gw
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    for i, o in enumerate(s["onsets_intended"]):
        st = at(o["tick"], S)
        m = sl(n, st)
        if i == 0:
            birth = gw.gesture(T=0.3, f0=35 * ratio, f1=250 * ratio, ring_s=0.03, ring_tau=0.02, reverse=True, drive=1.5)
            birth *= np.exp(-time(len(birth)) / 0.11)  # nasce e some: os brilhos de lente vêm por cima
            x = place(m, 0, birth) + 0.9 * sub_drop(hz("D2") * ratio, hz("D1") * ratio, m, 0.15, 0.1)
            x += place(m, 0, gw.breath_gesture(rng, 0.12, 900, 6000, reverse=True)) * 0.5
        else:
            x = place(m, 0, gw.breath_gesture(rng, 0.07, 2200 * ratio, 9500 * ratio, reverse=(i % 2 == 1)))
            P.mark(o["tick"], "D7")
        P.add_event(o["tick"], dsp.stereo(place(n, st, x), 0.8))
    return P.room(0.3, rng)


def twin(s):
    return point(s, ratio=0.85)


# ------------------------------------------------------------------ Ato II–III


def chirp_phase(ticks):
    """Φ_gw (rad) com Φ_c = 0 no 240. τ em segundos até a fusão. Mesma fase da órbita (÷ 2S)."""
    tau = np.maximum((240 - ticks) / 20, 1e-6)
    return -2 * np.pi * 35 * 9 ** 0.375 * 1.6 * tau ** 0.625


def chirp(s):
    """O chirp do LIGO (GW150914), 35 → ~245 Hz em 9 s, com a MESMA fase da órbita visual.
    v0.2.3: menos "zumbido": as camadas de harmônicos passam por um passa-baixa que acompanha a frequência
    (o chirp canta em vez de serrar) e ele mora no mesmo espaço da trilha. Os acentos são brilhos afinados
    que dobram o relógio da trilha uma oitava acima."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    ticks = S + np.arange(n) / TICK
    tau = np.maximum((240 - ticks) / 20, 1e-6)
    f = 35 * (np.maximum(tau, 0.05) / 9) ** (-0.375)  # f para em 245 Hz (o valor do tick 239 no spec)
    ot = [o["tick"] for o in s["onsets_intended"]]
    ov = [o["rms_norm"] for o in s["onsets_intended"]]
    A_law = (f / 35) ** (2 / 3)
    A_law = A_law / A_law[int((ot[0] - S) * TICK)] * ov[0]
    A = np.where(ticks < ot[0], A_law, np.interp(ticks, ot, ov))  # T-16: o envelope segue o spec
    # v0.3.2: MORPH temporal no pre-drop (~10–12 s). A curva GW continua sendo a espinha dorsal,
    # mas a percepção não fica linear: há uma contração/expansão de velocidade, uma queda brusca e
    # uma pequena recuperação antes do corte em 240. A matéria é a mesma; só o tempo dela é deformado.
    morph = np.ones_like(f)
    u = np.clip((ticks - 198) / (240 - 198), 0, 1)
    # pulsos de velocidade: explosão -> freio -> explosão menor -> afundamento.
    knots = np.array([0.00, 0.18, 0.34, 0.48, 0.63, 0.78, 0.90, 1.00])
    vals  = np.array([1.00, 1.72, 0.62, 1.28, 0.48, 0.34, 0.72, 0.16])
    morph_zone = np.interp(u, knots, vals)
    morph[ticks >= 198] = morph_zone[ticks >= 198]
    # Mantém o gesto reconhecível, mas a fase passa a obedecer à velocidade morfada.
    fm = f * morph
    ph = np.zeros_like(fm)
    ph[0] = chirp_phase(ticks[0])
    ph[1:] = ph[0] + 2 * np.pi * np.cumsum(fm[:-1]) / SR
    k239 = int((239 - S) * TICK)
    ph[k239:] = ph[k239] + 2 * np.pi * np.cumsum(fm[k239:]) / SR  # depois do 239, fase com f limitado
    c = np.cos(ph)
    # O pico de velocidade ganha impacto, o afundamento ganha corpo.
    burst = 1.0 + 0.55 * np.exp(-((ticks - 205) / 4.0) ** 2) + 0.30 * np.exp(-((ticks - 218) / 3.0) ** 2)
    drop = np.interp(ticks, [198, 205, 212, 220, 232, 239], [1.0, 1.1, 0.95, 1.15, 0.75, 0.25])
    A_m = A * burst * drop
    h = 0.55 * c + 0.3 * dsp.sat(c, 2.5) + 0.35 * np.cos(2 * ph + 0.6) + 0.3 * np.cos(4 * ph)
    h = dsp.tv_filter(h, np.clip(fm * 7, 300, 3200), "low") * A_m
    # Pequeno fantasma reverso: o ataque original parece ser puxado para trás antes do corte.
    z0, z1 = int((228 - S) * TICK), int((239 - S) * TICK)
    if z1 > z0 + 16:
        ghost = h[z0:z1][::-1]
        ghost = ghost * np.linspace(0.0, 0.42, len(ghost)) * np.hanning(len(ghost))
        h[z0:z1] += ghost
    h *= np.clip(time(n) / 0.4, 0, 1)
    h[-int(0.002 * SR):] *= np.linspace(1, 0, int(0.002 * SR))  # termina seco no 240
    P.add_bed(dsp.stereo(h, 0.3) * 0.6)
    for o in s["onsets_intended"]:
        st = at(o["tick"], S)
        P.add_event(o["tick"], dsp.stereo(place(n, st, glint(hz("D7"), sl(n, st), 0.12)) * 0.15, 0.3))
        P.mark(o["tick"], "D7")
    # quase seco: o chirp é a coisa mais PERTO do filme (o espaço vem da trilha). Um IR de ruído tem espectro
    # irregular, e um tom que varre passa pelos picos e vales: com sala o chirp oscilava ±3 dB tick a tick.
    return P.room(0.05, rng, tail_fade=0.003)


def merge(s):
    """A fusão. v0.2.7 (identidade: "o whoosh do 12 s parecia transição do Discovery"): sem reverb invertido.
    O chirp do filme já é a subida; no 240 o GESTO GW150914 em velocidade física REAL (o "bwip" do LIGO, 0,2 s)
    por cima do mesmo gesto esticado 4× uma oitava abaixo (o corpo), com sub caindo até o Ré1. No 241, o
    espaço-tempo racha: o anel do ringdown em ruído granular caindo."""
    import gw
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    i240 = at(240, S)
    # pré-roll: só o ar ficando rarefeito (sem nota, sem whoosh)
    pre = dsp.hp(dsp.pink(rng, i240), 2500) * np.linspace(0, 1, i240) ** 3 * 0.15
    P.add_bed(dsp.stereo(place(n, 0, pre), 1.0))
    m = sl(n, i240)
    real = gw.gesture(T=0.2, f0=70, f1=500, ring_s=0.4, ring_tau=0.08, drive=2.5)       # o "bwip" (oitava acima, audível)
    body = gw.gesture(T=0.8, f0=35, f1=250, ring_s=1.2, ring_tau=0.35, drive=3.0)      # o mesmo gesto esticado 4×
    # os dois inspirals TERMINAM juntos no 240: a cama leva a subida, o evento leva o anel
    body_at = place(m, 0, body[int(0.8 * SR):])
    real_at = place(m, 0, real[int(0.2 * SR):])
    hit = body_at * 1.0 + real_at * 0.7 + 1.1 * sub_drop(hz("D2"), hz("D1"), m, 0.3, 0.4)
    P.add_event(240, dsp.stereo(place(n, i240, hit), 0.5))
    # o inspiral dos dois termina exatamente no 240 (vai na cama: é a subida final)
    insp = np.zeros(n)
    a = max(0, i240 - int(0.8 * SR))
    insp[a:i240] = body[int(0.8 * SR) - (i240 - a):int(0.8 * SR)] * 0.6
    a2 = max(0, i240 - int(0.2 * SR))
    insp[a2:i240] += real[int(0.2 * SR) - (i240 - a2):int(0.2 * SR)] * 0.5
    P.add_bed(dsp.stereo(insp, 0.4))
    P.mark(240, "D6")
    i241 = at(241, S)
    m2 = sl(n, i241)
    crack = dsp.tv_filter(dsp.white(rng, m2), np.interp(time(m2), [0, 0.5], [4000, 300]), "band", width=0.7)
    crack *= np.clip(time(m2) / 0.003, 0, 1) * np.exp(-time(m2) / 0.18)
    P.add_event(241, dsp.stereo(place(n, i241, crack), 1.0))
    P.mark(241, "A6")
    return P.room(0.3, rng)


def ringdown(s):
    """O sino se apagando: seno amortecido (τ 0,6 s; o real é 4 ms, esticado 150×), afinado em Ré4
    (v0.2.3: "virou um só" consonante com o Ré pedal da trilha), com shimmer e o parcial a 1,5×."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    f = hz("D4")
    dec = np.exp(-t / 0.6)
    dec *= np.interp(t, [0, (255 - S) / 20, (266 - S) / 20, 99], [1, 1, 0.12, 0.12])  # quase-silêncio a partir do 268
    strike = np.sin(2 * np.pi * f * t) * dec * np.clip(t / 0.004, 0, 1)
    P.add_event(241, dsp.stereo(strike, 0.2))
    P.mark(241, "D7")
    lfo = 1 + 0.004 * np.sin(2 * np.pi * 0.7 * t)
    sh = np.sin(dsp.phase_osc(f * lfo)) * dec * np.clip(t / 0.08, 0, 1) * 0.5 + 0.12 * np.sin(2 * np.pi * 1.5 * f * t) * dec
    P.add_bed(dsp.stereo(sh, 1.0))
    P.room(0.3, rng, tail_fade=0.6)
    # o vazio respira (268–279): o quase-silêncio vale também para a cauda da sala
    quiet = np.interp(t, [0, (255 - S) / 20, (267 - S) / 20, 99], [1, 1, 0.03, 0.03])
    return P.map(lambda x: x * quiet[:, None])


# ------------------------------------------------------------------ Ato IV


def roar(rng, n, lo=500, hi=3500, am_depth=0.3, stereo_pan=True, phase0=0.0, key=("D2", "A2", "D3", "F3")):
    """O rugido do disco: ruído marrom num passa-banda largo que CANTA em Ré (ressonâncias nas notas da
    trilha), com o Doppler de 1 Hz."""
    t = time(n)
    raw = dsp.brown(rng, n)
    # v0.2.3: mais canto, menos chiado (o ruído largo encobria a trilha no Ato IV–V)
    x = dsp.bp(raw, lo, min(hi, 2200)) * 0.35
    x += sum(dsp.resonator(raw, hz(k), 80) for k in key) * 0.8
    x += dsp.bp(dsp.white(rng, n), 2500, 6000) * 0.015
    x = x * (1 + am_depth * np.sin(2 * np.pi * 1.0 * t + phase0))
    if stereo_pan:
        return dsp.pan(x, 0.5 * np.sin(2 * np.pi * 1.0 * t + phase0))  # a matéria que se aproxima passa uma vez por segundo
    return dsp.stereo(x)


def disk_ignite(s):
    """O disco acendendo de fora para dentro: cada anel é uma floração tonal SUBINDO (Lá2 → Ré4: a temperatura
    sobe, a nota sobe), sobre o rugido que vai abrindo."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    fc = 300 * (3500 / 300) ** np.clip(t / 1.5, 0, 1)
    bed = dsp.tv_filter(dsp.brown(rng, n), fc, "band", width=1.5) * np.interp(t, [0, 1.5], [0.05, 0.25])
    P.add_bed(dsp.stereo(bed, 0.6))
    for o, nm in zip(s["onsets_intended"], ["A2", "D3", "F3", "A3", "D4"]):
        st = at(o["tick"], S)
        m = sl(n, st)
        x = bloom(hz(nm), m, rng, 0.012, 0.35) + 0.5 * bloom(hz(nm) * 2, m, rng, 0.012, 0.25)
        x += 0.5 * sub_drop(hz(nm) / 2, hz(nm) / 2, m, 0.1, 0.12)
        P.add_event(o["tick"], dsp.stereo(place(n, st, x), 0.6))
        P.mark(o["tick"], nm[:-1] + "7")  # uma oitava acima dos harmônicos da floração
    return P.room(0.4, rng)


def disk_loop(s):
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    P.add_bed(roar(rng, n, stereo_pan=not s["id"].endswith("_ext"), phase0=-0.8))
    P.start_event(s["onsets_intended"][0]["tick"])
    return P.room(0.3, rng)


def jet(s):
    """Jatos. v0.2.7 (identidade): sem reverb invertido. A pré-carga é o gesto GW como ar subindo; o disparo é o
    gesto PARA CIMA esticado e saturado (40 → 600 Hz), com sub; o estalo é o anel em ruído; o síncrotron
    continua afinado em Fá2."""
    import gw
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    i360, i362 = at(360, S), at(362, S)
    charge = gw.breath_gesture(rng, i360 / SR - 0.05, 300, 7000, reverse=False, q_oct=0.8)
    P.add_bed(dsp.stereo(place(n, i360 - len(charge) + int(0.05 * SR), charge) * 0.35, 1.0))
    m = sl(n, i360)
    t = time(m)
    up = gw.gesture(T=0.3, f0=hz("F1"), f1=hz("F4"), ring_s=0.9, ring_tau=0.12, drive=2.4)
    up = up[int(0.3 * SR) - int(0.02 * SR):]  # o disparo começa no fim do inspiral (o golpe)
    hit = (place(m, 0, up) + sub_drop(hz("F2"), hz("F1"), m, 0.2, 0.14)) * np.exp(-time(m) / 0.09)  # o peso no 1º tick
    P.add_event(360, dsp.stereo(place(n, i360, hit), 0.7))
    P.mark(360, "F6")
    m2 = sl(n, i362)
    crack = dsp.tv_filter(dsp.white(rng, m2), np.interp(time(m2), [0, 0.3], [6000, 1500]), "band", width=0.6)
    crack *= np.clip(time(m2) / 0.002, 0, 1) * np.exp(-time(m2) / 0.12)
    P.add_event(362, dsp.stereo(place(n, i362, crack), 0.9))
    P.mark(362, "C7")
    saw = dsp.saw_bl(hz("F2") * (1 + 0.006 * np.sin(2 * np.pi * 3 * t)), m)
    fc = 500 + 2000 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
    syn = dsp.tv_filter(saw, fc, "band", width=0.8) * np.exp(-t / 0.9) * np.clip(t / 0.15, 0, 1) * 0.8
    P.add_bed(dsp.stereo(place(n, i360, syn), 0.5))
    return P.room(0.4, rng)


def pad(s):
    """O único respiro musical dos efeitos: coral "aah" em Ré menor com 9ª, o mesmo acorde da trilha no 390."""
    import score
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    out = sum(score.choir_note(hz(nm), n, rng) for nm in ("D4", "A4", "E5", "F5"))
    out *= np.interp(t, [0, 0.6, 2.4, 3.0], [0.15, 1, 1, 0])
    P.add_bed(dsp.stereo(out, 1.0))
    P.start_event(400)
    return P.room(0.5, rng)


# ------------------------------------------------------------------ Ato V–VI


def tidal(s):
    """Maré: gemidos de terra e metal afinados em Ré menor (ressonâncias graves que cedem e caem de altura),
    sobre o ronco de 30–60 Hz."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    rum = dsp.sat(dsp.lp(dsp.brown(rng, n), 60) * 0.8, 2.0) + 0.3 * np.sin(2 * np.pi * hz("D1") * t)
    P.add_bed(dsp.stereo(rum * np.interp(t, [0, 2], [0.25, 0.45]), 0.3))
    for o, nm in zip(s["onsets_intended"], ["D2", "F2", "A1", "C#2", "Bb1", "A1"]):
        st = at(o["tick"], S)
        m = sl(n, st)
        f = hz(nm)
        tt = time(m)
        bend = f * np.interp(tt, [0, 0.6], [1.06, 0.94])  # a estrutura cede: a nota cai
        groan = sum(a * np.sin(dsp.phase_osc(bend * k)) for k, a in ((1, 1.0), (2, 0.6), (3, 0.4), (5, 0.2)))
        grit = dsp.bp(dsp.brown(rng, m), f * 2, f * 12) * 0.5
        x = dsp.sat((groan + grit) * np.clip(tt / 0.008, 0, 1) * np.exp(-tt / 0.18), 1.8)
        P.add_event(o["tick"], dsp.pan(place(n, st, x), rng.uniform(-0.5, 0.5)))
        P.mark(o["tick"], "D7")
    return P.room(0.12, rng)


STUTTER = [1, 1, 2, 2, 3, 4, 6, 8]  # o stutter da câmera no B17 (spec/storyboard.json); depois, 8 em 8 (B18)


def freeze_hit(rng, seconds=2.0):
    """O golpe do congelamento (o "ZA WARUDO" deste filme): o gesto GW150914 de trás pra frente, devagar e
    grave: o anel cresce num instante e a nota DESCE de Lá2 até o fundo, com sub."""
    import gw
    g = gw.gesture(T=seconds, f0=hz("A0") * 0.75, f1=hz("A2"), ring_s=0.05, ring_tau=0.03, reverse=True, drive=2.6)
    m = len(g)
    return g + 0.8 * sub_drop(hz("A1"), hz("A0") * 0.75, m, seconds, seconds * 0.6)


def moment(start_tick, end_tick):
    """O som do filme naquele instante (trilha + ritmo, tempo absoluto), para congelar e arranhar."""
    import rhythm
    import score
    a, b = int(start_tick * TICK), int(end_tick * TICK)
    return score.render_full()[a:b] + rhythm.render_full()[a:b]


def fall_speed(ticks):
    """Velocidade relativa do pedaço-herói (a mesma forma da câmera do B15–B16)."""
    return np.interp(ticks, [460, 500, 539], [0.3, 1.0, 0.7])


def fall(s):
    """Vento que acompanha a velocidade, a passagem pelo disco no 500 (um rasante afinado em Lá que dobra
    para baixo, Doppler) e, a partir do 510, o tempo dilatando (fita 1,0 → 0,5)."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    ticks = S + np.arange(n) / TICK
    v = fall_speed(ticks)
    wind = np.stack([dsp.tv_filter(dsp.white(rng, n), 400 + 1800 * v, "band", width=1.2) for _ in range(2)], axis=1)
    P.add_bed(wind * (0.2 + 0.3 * v)[:, None])
    g = dsp.bp(dsp.white(rng, n), 400, 2200) * dsp.env_ad(n, 0.01, 0.3)
    P.add_event(460, dsp.stereo(g, 0.6))
    P.mark(460, "A6")
    i500 = at(500, S)
    span = int(0.5 * SR)
    a, b = i500 - span, min(n, i500 + span)
    loc = np.arange(b - a) - span
    pitch = hz("A3") * np.where(loc < 0, 1.0, np.interp(loc, [0, 0.4 * SR], [1.0, 0.5]))  # Doppler: dobra para baixo
    tone = sum(a_ * np.sin(dsp.phase_osc(pitch * k)) for k, a_ in ((1, 1.0), (2, 0.5), (3, 0.3)))
    noise = dsp.tv_filter(dsp.white(rng, b - a), 900 + 2400 * np.exp(-(loc / (0.12 * SR)) ** 2), "band", width=0.8)
    env = np.where(loc < 0, np.exp(-(loc / (0.03 * SR)) ** 2), np.exp(-loc / (0.14 * SR)))
    w = np.zeros(n)
    w[a:b] = (tone * 0.6 + noise * 1.4) * env
    pn = np.clip((np.arange(n) - i500) / (0.25 * SR), -1, 1)
    P.add_event(500, dsp.pan(w, pn))
    P.mark(500, "A8")  # acima da banda do rasante
    rate = np.interp(ticks, [510, 539], [1.0, 0.5])
    P.room(0.35, rng, tail_fade=0.05)
    P.map(lambda x: dsp.varispeed(x, rate))
    # v0.2.7: o tempo sendo PUXADO: o golpe do congelamento de trás pra frente, terminando seco no 540
    suck = freeze_hit(rng)[::-1]
    suck = suck / (np.abs(suck).max() + 1e-12) * np.linspace(0, 1, len(suck)) ** 2
    P.add_bed(dsp.stereo(place(n, n - len(suck), suck) * 0.5, 0.6))
    return P


def horizon(s):
    """O horizonte, o tempo parando (o "ZA WARUDO" deste filme). v0.2.7 (identidade: "a dilatação não impressiona"):
    1. no 540, o GOLPE do congelamento (o gesto GW de trás pra frente, descendo até o fundo);
    2. o som do filme naquele instante CONGELA (congelamento espectral da trilha + ritmo de 530–540), um
       drone que vai afinando para baixo (redshift);
    3. em cima, o mesmo instante PULA como disco arranhado nos ticks do stutter da câmera [1,1,2,2,3,4,6,8]
       (depois 8 em 8), cada pulo mais grave e mais baixo;
    4. o coração abafado alongando (os onsets do spec);
    5. silêncio digital exato no 600."""
    import gw
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    hit = freeze_hit(rng)
    P.add_bed(dsp.stereo(place(n, 0, hit / (np.abs(hit).max() + 1e-12)) * 0.9, 0.5))
    src = moment(0, 541)  # absoluto até o 540
    fr = gw.freeze(src[int(530 * TICK):int(540 * TICK)], n / SR + 0.5, rng)
    rate = np.interp(t, [0, 3.0], [1.0, 0.35])
    drone = dsp.varispeed(np.concatenate([fr, fr]), rate)[:n] * np.interp(t, [0, 0.08, 1.2, 2.5, 2.98], [0, 0.55, 0.35, 0.15, 0])
    P.add_bed(dsp.stereo(dsp.lp(drone, 2500), 0.8))
    st = gw.stutter(src, 540, STUTTER, 600, pitch_step=0.93, gain_step=0.86, grain_ticks=3)
    st = st / (np.abs(st).max() + 1e-12) * 0.6
    P.add_bed(st * np.interp(t, [0, 2.5, 2.98], [1, 0.4, 0])[:, None])
    for o in s["onsets_intended"]:
        so = at(o["tick"], S)
        m = sl(n, so)
        tt = time(m)
        hb = dsp.sat(np.sin(2 * np.pi * hz("D1") * 1.5 * tt) * dsp.env_ad(m, 0.008, 0.14) * 1.6, 2.2)
        k2 = int(0.24 * SR)
        if k2 < m:
            hb[k2:] += 0.5 * dsp.sat(np.sin(2 * np.pi * hz("D1") * 1.4 * time(m - k2)) * dsp.env_ad(m - k2, 0.008, 0.12), 2.2)
        P.add_event(o["tick"], dsp.stereo(place(n, so, dsp.lp(hb, 600))))
        P.mark(o["tick"], "D6")
    P.room(0.35, rng, tail_fade=0.05)
    # silêncio digital exato no fim (o filme fica mudo de 600 a 619)
    P.map(lambda x: x * np.interp(t, [0, 2.97, 2.995], [1, 1, 0])[:, None])
    return P


# ------------------------------------------------------------------ Ato VII


PENTA = ["D", "E", "F#", "A", "B"]


def hawking(s):
    """Evaporação: ambiente quase inaudível e brilhos de vidro AFINADOS no pentatônico de Ré maior (o perdão da
    trilha), cada vez mais densos, e a temperatura subindo como um harmônico que sobe."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    bed = dsp.stereo(dsp.pink(rng, n) * 10 ** (-50 / 20) * 6, 0.8)

    def sparkle(level):
        nm = PENTA[int(rng.integers(len(PENTA)))] + str(int(rng.integers(6, 8)))
        d = int(rng.uniform(0.15, 0.4) * SR)
        return dsp.pan(bell(hz(nm), d, rng, 0.25, ((1, 1.0), (2.0, 0.3), (3.0, 0.1))) * level, rng.uniform(-0.8, 0.8))

    k = 0.0
    while True:
        rate = 3 + 30 * (k / n) ** 2  # Poisson com taxa subindo
        k += rng.exponential(SR / rate)
        if k >= n - 0.4 * SR:
            break
        sp = sparkle(0.008 * (0.2 + k / n) ** 2)
        bed[int(k):int(k) + len(sp)] += sp
    for _ in range(30):  # o enxame antes do clarão (é o pico do som); v0.2.6: 693–696, antes do drop-out
        sp = sparkle(0.8)
        i = at(693, S) + int(rng.uniform(0, 2.6) * TICK)
        e = min(n, i + len(sp))
        bed[i:e] += sp[: e - i]
    i660 = at(660, S)
    m = sl(n, i660)
    temp = np.zeros(n)
    temp[i660:] = dsp.sine_sweep(m, hz("D7"), hz("D8")) * np.linspace(0, 0.05, m)
    P.add_bed(bed + dsp.stereo(temp))
    for o, nm in zip(s["onsets_intended"], ["A6", "D7", "F#6", "A6", "D7", "F#7"]):
        st = at(o["tick"], S)
        P.add_event(o["tick"], dsp.pan(place(n, st, bell(hz(nm), int(0.5 * SR), rng, 0.3)), rng.uniform(-0.5, 0.5)))
    P.room(0.35, rng)
    # v0.2.6: ponto de audição: a cama sai abafada e some no drop-out; os brilhos marcados ficam (o do 699 é
    # o único som no vazio antes do clarão)
    import act7
    P.bed = act7.muffle(P.bed, S) * act7.dropout(n, S)[:, None]
    return P


def burst(s):
    """O último clarão: Ré maior com 9ª em vidro (sem sub violento) e um véu de luz que abre e entra no outro."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    glass = sum(bell(hz(nm), n, rng, 1.6) * a for nm, a in (("D5", 1.0), ("F#5", 0.7), ("A5", 0.7), ("E6", 0.5), ("D6", 0.5)))
    flash = sum(bell(hz(nm), n, rng, 0.06) for nm in ("D6", "A6", "D7"))  # o golpe de luz: tudo no primeiro tick
    # resolução da célula DOOMS DAY: Ab5 aparece por dezenas de ms e cai
    # para A5; o ouvido reconhece a mesma entidade que perseguiu a queda.
    sig_t = time(n)
    sig_env = np.exp(-sig_t / 0.32) * np.clip(sig_t / 0.006, 0, 1)
    signature = (np.sin(2*np.pi*hz("Ab5")*sig_t) * np.exp(-sig_t/0.035)
                 + np.sin(2*np.pi*hz("A5")*sig_t) * np.exp(-sig_t/0.45))
    signature *= sig_env
    P.add_event(700, dsp.stereo(glass * 0.55 + flash * 2.0 + signature * 0.8, 0.8))
    veil = dsp.tv_filter(dsp.pink(rng, n), np.interp(t, [0, 1.5], [800, 6000]), "band", width=2.0)
    veil *= np.interp(t, [0, 0.6, 1.2], [0, 0.12, 0.12]) * np.exp(-np.maximum(t - 1.2, 0) / 0.9)
    P.add_bed(dsp.stereo(veil, 1.0))
    P.room(0.35, rng, tail_fade=0.4)
    import act7
    return P.map(lambda x: act7.widen(x, S))  # v0.2.6: a luz se espalha: de quase mono a largo


def score_part(s):
    """A trilha (tools/synth/score.py + spec/score.json): sem eventos, só a cama (já tem o próprio espaço)."""
    import score
    n = (s["end_tick"] - s["tick"]) * TICK
    P = Parts(n)
    P.add_bed(score.part(s["tick"], s["end_tick"]))
    return P


def rhythm_part(s):
    """A camada rítmica (tools/synth/rhythm.py + spec/rhythm.json): só cama, com o espaço próprio."""
    import rhythm
    n = (s["end_tick"] - s["tick"]) * TICK
    P = Parts(n)
    P.add_bed(rhythm.part(s["tick"], s["end_tick"]))
    return P


RECIPES = {
    "sgx_void_in": void_in, "sgx_point": point, "sgx_twin": twin, "sgx_chirp": chirp, "sgx_merge": merge,
    "sgx_ringdown": ringdown, "sgx_disk_ignite": disk_ignite, "sgx_disk_loop": disk_loop, "sgx_disk_loop_ext": disk_loop,
    "sgx_jet": jet, "sgx_pad": pad, "sgx_tidal": tidal, "sgx_fall": fall, "sgx_horizon": horizon,
    "sgx_hawking": hawking, "sgx_burst": burst, "sgx_score_a": score_part, "sgx_score_b": score_part, "sgx_rhythm_a": rhythm_part, "sgx_rhythm_b": rhythm_part,
}
