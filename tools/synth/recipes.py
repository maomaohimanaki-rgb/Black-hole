"""Receitas dos 16 sons do buraco negro (docs/AUDIO_DESIGN.md §3).
Cada receita devolve Parts: uma "cama" e UM EVENTO POR ONSET PEDIDO (estéreo, comprimento do som).
O render.py soma cama + Σ ganho·evento e calibra os ganhos até o analisador achar cada onset no tick e com
o rms_norm pedidos. Toda operação depois da soma tem que ser linear (varispeed, pan, filtro): por isso a
saturação fica DENTRO de cada parte.
v0.2.0."""
import numpy as np

import dsp
from dsp import SR, TICK, time, n_ticks


class Parts:
    def __init__(self, n):
        self.n = n
        self.bed = np.zeros((n, 2))
        self.events = {}
        self.marks = []  # (tick, lo, hi): ataque de articulação, aplicado DEPOIS da calibração (nível fixo)

    def mark(self, tick, lo=4000, hi=9000):
        self.marks.append((tick, lo, hi))

    def add_bed(self, x):
        self.bed += x if x.ndim == 2 else dsp.stereo(x)

    def add_event(self, tick, x):
        x = x if x.ndim == 2 else dsp.stereo(x)
        self.events[tick] = self.events.get(tick, 0) + x

    def map(self, f):
        """Aplica uma operação LINEAR a tudo (cama e eventos)."""
        self.bed = f(self.bed)
        self.events = {k: f(v) for k, v in self.events.items()}
        return self

    def start_event(self, tick, ticks=1.5):
        """Onset no começo do arquivo sem ataque próprio: a janela inicial da cama vira o evento,
        para o calibrador ajustar o nível do primeiro tick sem mexer no resto."""
        w = np.zeros(self.n)
        a = int(ticks * TICK)
        w[:a] = 1.0
        w[a:a + TICK] = np.linspace(1, 0, TICK)[: max(0, min(TICK, self.n - a))]
        ev = self.bed * w[:, None]
        self.bed = self.bed * (1 - w)[:, None]
        self.add_event(tick, ev)


def rng_for(sid):
    # semente fixa por som (hash() do Python muda entre execuções): build idempotente
    return np.random.default_rng(sum(map(ord, sid)) * 7919)


def at(tick, start):
    return (tick - start) * TICK


def transient(rng, n, start, lo=1500, hi=6000, dur=0.006, amp=1.0):
    """Clique filtrado curto: marca o onset no agudo (o analisador acha) sem pesar no RMS."""
    x = np.zeros(n)
    m = int(dur * SR)
    if start >= n:
        return x
    m = min(m, n - start)
    burst = dsp.white(rng, m) * np.hanning(m * 2)[m:] * amp
    x[start:start + m] = burst
    return dsp.bp(x, lo, hi)


# ------------------------------------------------------------------ Ato I


def void_in(s):
    """O ar sendo sugado: ruído rosa crescendo para dentro (reverb invertido), queda de sub no 12."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    cut = at(19, S) - int(0.02 * SR)
    # cama: rosa estéreo, passa-baixa varrendo 400 → 1 500, envelope crescendo (swell) até o 19
    noise = np.stack([dsp.pink(rng, n), dsp.pink(rng, n)], axis=1)
    fc = np.interp(t, [0, 19 / 20], [400, 1500])
    noise = np.stack([dsp.tv_filter(noise[:, c], fc, "low") for c in range(2)], axis=1)
    sw = np.interp(t, [0, 12 / 20, 18.6 / 20], [0.25, 0.6, 1.0]) ** 1.5
    sw[cut:] *= np.exp(-np.arange(n - cut) / (0.004 * SR))  # corta quase a zero no 19 (respiração)
    sw[at(19, S):] += 0.02
    # "reverb invertido": rabo de reverb tocado de trás para frente, entrando no 19
    rev = dsp.convolve(dsp.white(rng, int(0.05 * SR)), dsp.reverb_ir(rng, 0.9, 0.3))[::-1]
    tail = np.zeros((n, 2))
    m = min(len(rev), cut)
    tail[cut - m:cut] = rev[-m:] * 6
    P.add_bed(noise * sw[:, None] * 0.5 + dsp.lp(tail, 2500))
    # onset 0: entrada de ar
    P.add_event(0, dsp.stereo(dsp.lp(dsp.white(rng, n), 900) * dsp.env_ad(n, 0.01, 0.12) + transient(rng, n, 0, 800, 3000, amp=0.5), 0.6))
    # onset 12: queda de sub 55 → 32 Hz em 0,4 s, com 2º e 3º harmônicos (P-48)
    i12 = at(12, S)
    m = n - i12
    sub = np.zeros(n)
    f = np.interp(time(m), [0, 0.4], [55, 32])
    ph = dsp.phase_osc(f)
    body = dsp.sat(np.sin(ph) * 0.9, 2.5) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    sub[i12:] = body * dsp.env_ad(m, 0.003, 0.25)
    sub[cut:] *= 0.0
    P.add_event(12, dsp.stereo(sub + transient(rng, n, i12, 200, 1200, amp=0.4)))
    # onset 19: a inspiração presa
    i19 = at(19, S)
    gasp = dsp.bp(dsp.white(rng, n), 1500, 5000) * dsp.env_ad(n, 0.002, 0.05, i19)
    P.add_event(19, dsp.stereo(gasp, 0.5))
    return P


def point(s, ratio=1.0):
    """Nascer de um ponto: sino inarmônico + soco de 40 Hz saturado, depois pings."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    partials = [2100 * ratio, 3400 * ratio, 5700 * ratio]
    for i, o in enumerate(s["onsets_intended"]):
        st = at(o["tick"], S)
        b = dsp.bell(n, partials, [1.0, 0.6, 0.35], 0.4, start=st, rng=rng)
        if i:
            P.mark(o["tick"], 8000, 13000)  # o "tic" do ping: se ouve por cima do rabo do anterior
        x = dsp.stereo(b, 0.4)
        if i == 0:
            m = n - st
            k = np.zeros(n)
            k[st:] = dsp.sat(np.sin(2 * np.pi * 40 * ratio * time(m)) * dsp.env_ad(m, 0.002, 0.08) * 1.4, 3.0)
            x = x + dsp.stereo(k)
        P.add_event(o["tick"], x)
    # brilho de fundo bem baixo entre os pings
    P.add_bed(dsp.stereo(dsp.hp(dsp.pink(rng, n), 3000) * 0.004))
    return P


def twin(s):
    return point(s, ratio=0.85)  # um tom abaixo: ×0,85 na frequência, não no tempo


# ------------------------------------------------------------------ Ato II–III


def chirp_phase(ticks):
    """Φ_gw (rad) com Φ_c = 0 no 240. τ em segundos até a fusão. Mesma fase da órbita (÷ 2S)."""
    tau = np.maximum((240 - ticks) / 20, 1e-6)
    return -2 * np.pi * 35 * 9 ** 0.375 * 1.6 * tau ** 0.625


def chirp(s):
    """O chirp do LIGO (GW150914), 35 → ~245 Hz em 9 s, com a MESMA fase da órbita visual."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    ticks = S + np.arange(n) / TICK
    tau = np.maximum((240 - ticks) / 20, 1e-6)
    # v0.2.0: f → ∞ quando τ → 0; sem limite, o pico de A nos últimos ms achatava o chirp inteiro para 1/4.
    # f para em 245 Hz (o valor do tick 239 no spec); a FASE continua a fórmula exata.
    f = 35 * (np.maximum(tau, 0.05) / 9) ** (-0.375)
    # Envelope: a curva de rms_norm do spec (os onsets), que bate com A ∝ f^(2/3) até ~200 e achata no
    # grito final (o spec pede 0,92 no 232; a lei daria 0,6). O JSON manda nos números (DECISIONS T-16).
    ot = [o["tick"] for o in s["onsets_intended"]]
    ov = [o["rms_norm"] for o in s["onsets_intended"]]
    A_law = (f / 35) ** (2 / 3)
    A_law = A_law / A_law[int((ot[0] - S) * TICK)] * ov[0]
    A = np.where(ticks < ot[0], A_law, np.interp(ticks, ot, ov))
    ph = chirp_phase(ticks)
    # v0.2.0: no último tick a frequência instantânea da fórmula vai ao infinito (aliasing na camada 4Φ).
    # Depois do 239 a fase é integrada com f limitado; a última meia-órbita (236) não muda.
    k239 = int((239 - S) * TICK)
    ph[k239:] = ph[k239] + 2 * np.pi * np.cumsum(f[k239:]) / SR
    c = np.cos(ph)
    h = A * (0.45 * c + 0.35 * dsp.sat(c, 3.0))  # harmônicos gerados na onda unitária, depois × A
    # v0.2.0: as camadas 2Φ e 4Φ (70–980 Hz) carregam o chirp no ouvido e no celular (P-48); só com a
    # fundamental de 35–60 Hz o B04–B06 media −40 LUFS no mixdown, quase mudo.
    h += 0.35 * A * np.cos(2 * ph + 0.6) + 0.45 * A * np.cos(4 * ph)
    h *= np.clip(time(n) / 0.3, 0, 1)
    h[-int(0.002 * SR):] *= np.linspace(1, 0, int(0.002 * SR))  # termina seco no 240
    P.add_bed(dsp.stereo(h, 0.3) * 0.6)
    # acento em cada meia-órbita: clique 2–4 kHz de 6 ms. v0.2.0: sem "thump" (cópia do próprio chirp):
    # ele não mudava as proporções, o calibrador o inflava e o pico segurava o master (B04–B06 a −40 LUFS).
    # A lei A ∝ f^(2/3) já dá a curva 0,3 → 1,0 pedida; o acento só articula.
    for o in s["onsets_intended"]:
        st = at(o["tick"], S)
        P.add_event(o["tick"], dsp.stereo(transient(rng, n, st, 2000, 4000, dur=0.006, amp=0.3), 0.3))
        P.mark(o["tick"], 2000, 4000)
    return P


def merge(s):
    """A fusão: prato invertido subindo até o 240, boom de sub + estouro de ruído, tape crunch no 241."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    i240 = at(240, S)
    # pré-roll: prato metálico invertido + ruído subindo (232 → 240)
    m = i240
    cym = sum(dsp.resonator(dsp.white(rng, m), f, 25) for f in (3100, 4700, 6300, 8900))
    cym = (cym * np.exp(-time(m) / 0.12))[::-1]
    rise = dsp.hp(dsp.white(rng, m), 1200) * np.linspace(0, 1, m) ** 3
    pre = np.zeros(n)
    pre[:m] = cym / (np.abs(cym).max() + 1e-9) * 0.5 + rise * 0.25
    P.add_bed(dsp.stereo(pre, 0.8))
    # 240: boom de sub saturado + ruído branco 30 ms
    mm = n - i240
    boom = np.zeros(n)
    ph = dsp.phase_osc(np.interp(time(mm), [0, 0.5], [60, 38]))
    boom[i240:] = dsp.sat(np.sin(ph) * dsp.env_ad(mm, 0.002, 0.35) * 1.3, 2.5)
    burst = dsp.white(rng, n) * dsp.env_ad(n, 0.001, 0.012, i240)
    P.add_event(240, dsp.stereo(boom * 0.9 + burst * 0.8, 0.5))
    # 241: tape crunch (bitcrush curtinho)
    i241 = at(241, S)
    cr = dsp.bitcrush(dsp.bp(dsp.white(rng, n), 300, 6000), 4, 8) * dsp.env_ad(n, 0.001, 0.03, i241)
    P.add_event(241, dsp.stereo(cr, 0.6))
    P.mark(241, 1500, 6000)
    # rabo: ruído grave decaindo até o 252
    tail = dsp.lp(dsp.brown(rng, n), 400) * dsp.env_ad(n, 0.01, 0.25, i240) * 0.3
    P.add_bed(dsp.stereo(tail, 0.5))
    return P


def ringdown(s):
    """O sino se apagando: seno amortecido de 250 Hz (τ 0,6 s; o real é 4 ms, esticado 150×) + shimmer."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    dec = np.exp(-t / 0.6)
    dec *= np.interp(t, [0, (255 - S) / 20, (268 - S) / 20, 99], [1, 1, 0.25, 0.25])  # quase-silêncio a partir do 268
    strike = np.sin(2 * np.pi * 250 * t) * dec * np.clip(t / 0.002, 0, 1)
    P.add_event(241, dsp.stereo(strike + transient(rng, n, 0, 200, 1500, amp=0.3), 0.2))
    # shimmer: eco com chorus lento que floresce em ~80 ms, e o parcial a 1,5×
    lfo = 1 + 0.004 * np.sin(2 * np.pi * 0.7 * t)
    sh = np.sin(dsp.phase_osc(250 * lfo)) * dec * np.clip(t / 0.08, 0, 1) * 0.5
    sh += 0.12 * np.sin(2 * np.pi * 375 * t) * dec
    P.add_bed(np.stack([sh, np.roll(sh, int(0.017 * SR))], axis=1))
    return P


# ------------------------------------------------------------------ Ato IV


def roar(rng, n, lo=600, hi=4000, am_depth=0.3, stereo_pan=True, phase0=0.0):
    """O rugido do disco: ruído marrom + chiado num passa-banda largo, com o Doppler de 1 Hz."""
    t = time(n)
    x = dsp.bp(dsp.brown(rng, n), lo, hi) * 0.8 + dsp.bp(dsp.white(rng, n), 2500, 7000) * 0.12
    am = 1 + am_depth * np.sin(2 * np.pi * 1.0 * t + phase0)
    x = x * am
    if stereo_pan:
        return dsp.pan(x, 0.5 * np.sin(2 * np.pi * 1.0 * t + phase0))  # a matéria que se aproxima passa uma vez por segundo
    return dsp.stereo(x)


def disk_ignite(s):
    """O disco acendendo: passa-banda varrendo 300 → 4 000 Hz (o centroide sobe com a cor), um whoomp por anel."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    fc = 300 * (4000 / 300) ** np.clip(t / 1.5, 0, 1)
    # o marrom tem muito grave: com o filtro em 300 Hz o começo pesava mais que os whoomps
    bed = dsp.tv_filter(dsp.brown(rng, n), fc, "band", width=1.5) * np.interp(t, [0, 1.5], [0.06, 0.3])
    # estalos granulares (30 → 80 por segundo)
    cr = np.zeros(n)
    k = 0.0
    while k < n:
        rate = 30 + 50 * k / n
        k += rng.exponential(SR / rate)
        i = int(k)
        if i < n - 200:
            cr[i:i + 200] += rng.uniform(-1, 1) * np.exp(-np.arange(200) / 30)
    P.add_bed(dsp.stereo(bed, 0.6) + dsp.pan(dsp.hp(cr, 2000) * 0.25, rng.uniform(-0.6, 0.6)))
    for o in s["onsets_intended"]:
        st = at(o["tick"], S)
        m = n - st
        w = np.zeros(n)
        # whoomp: ruído com o filtro abrindo em 25 ms + soco de 80 Hz; a energia cai NO tick do onset
        body = dsp.tv_filter(dsp.white(rng, m), np.interp(time(m), [0, 0.025], [500, 3000]), "low")
        body = body / (np.abs(body).max() + 1e-12) + 0.8 * np.sin(2 * np.pi * 80 * time(m))
        w[st:] = body * dsp.env_ad(m, 0.003, 0.06)
        P.add_event(o["tick"], dsp.stereo(w, 0.5))
        P.mark(o["tick"], 3000, 9000)
    return P


def disk_loop(s):
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    P.add_bed(roar(rng, n, stereo_pan=not s["id"].endswith("_ext"), phase0=-0.8))
    P.start_event(s["onsets_intended"][0]["tick"])
    return P


def jet(s):
    """Jatos: assobio de pré-carga, explosão no 360, zumbido de síncrotron decaindo até o 400."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    i360, i362 = at(360, S), at(362, S)
    wh = np.zeros(n)
    wh[:i360] = dsp.sine_sweep(i360, 400, 3000) * np.linspace(0.1, 0.6, i360)
    P.add_bed(dsp.stereo(wh))
    m = n - i360
    t = time(m)
    # explosão: ruído largo + sub saturado
    ex = np.zeros(n)
    ex[i360:] = dsp.white(rng, m) * dsp.env_ad(m, 0.001, 0.08) * 0.9
    ex[i360:] += dsp.sat(np.sin(2 * np.pi * 42 * t) * dsp.env_ad(m, 0.002, 0.3) * 1.5, 2.5)
    P.add_event(360, dsp.stereo(ex, 0.7))
    # 362: segunda frente de choque (crepitar)
    cr = dsp.bp(dsp.white(rng, n), 800, 5000) * dsp.env_ad(n, 0.002, 0.06, i362)
    P.mark(362, 5000, 10000)
    P.add_event(362, dsp.stereo(cr, 0.8))
    # síncrotron: dente-de-serra de 90 Hz num passa-banda ressonante varrendo devagar
    syn = np.zeros(n)
    saw = dsp.saw_bl(90 * (1 + 0.01 * np.sin(2 * np.pi * 3 * t)), m)
    fc = 600 + 2500 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t))
    syn[i360:] = dsp.tv_filter(saw, fc, "band", width=0.7) * np.exp(-t / 0.9) * np.clip(t / 0.05, 0, 1) * 1.2
    P.add_bed(dsp.stereo(syn, 0.5))
    return P


def pad(s):
    """O único momento musical: coral em "ah" (formantes 700 / 1 220 / 2 600 Hz), Lá1–Mi2–Dó3."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    voice = np.zeros(n)
    for f0 in (55.0, 82.41, 130.81):
        for det in (-0.004, 0.0, 0.005):
            fr = f0 * (1 + det) * (1 + 0.006 * np.sin(2 * np.pi * (5.0 + rng.uniform(-0.4, 0.4)) * t))
            voice += dsp.pulse_train(fr, n, 0.06)
    out = sum(a * dsp.resonator(voice, f, q) for f, q, a in ((700, 6, 1.0), (1220, 8, 0.6), (2600, 10, 0.25)))
    out *= np.interp(t, [0, 0.6, 2.4, 3.0], [0.15, 1, 1, 0])
    P.add_bed(dsp.stereo(out, 0.8))
    P.start_event(400)
    return P


# ------------------------------------------------------------------ Ato V–VI


def tidal(s):
    """Estalos de maré: impulsos em ressonâncias de madeira e pedra (esticados), ronco de 30–60 Hz por baixo."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    rum = dsp.sat(dsp.lp(dsp.brown(rng, n), 60) * 0.8, 2.0) + 0.3 * np.sin(2 * np.pi * 45 * t)
    P.add_bed(dsp.stereo(rum * np.interp(t, [0, 2], [0.25, 0.45]), 0.3))
    for i, o in enumerate(s["onsets_intended"]):
        st = at(o["tick"], S)
        imp = np.zeros(n)
        imp[st:st + 40] = rng.standard_normal(40)
        wood = sum(dsp.resonator(imp, f, 40) for f in rng.uniform(180, 600, 3))
        stone = sum(dsp.resonator(imp, f, 30) for f in rng.uniform(80, 300, 2))
        x = (wood + stone) * 8 * dsp.env_ad(n, 0.001, 0.35, st)
        x = dsp.sat(x, 1.5)
        P.mark(o["tick"], 3000, 9000)
        P.add_event(o["tick"], dsp.pan(x, rng.uniform(-0.5, 0.5)))
    return P


def fall_speed(ticks):
    """Velocidade relativa do pedaço-herói (a mesma forma da câmera do B15–B16)."""
    return np.interp(ticks, [460, 500, 539], [0.3, 1.0, 0.7])


def fall(s):
    """Vento que acompanha a velocidade, whoosh Doppler no 500 e, a partir do 510, o tempo dilatando (fita 1,0 → 0,5)."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    ticks = S + np.arange(n) / TICK
    v = fall_speed(ticks)
    wind = np.stack([dsp.tv_filter(dsp.white(rng, n), 400 + 2200 * v, "band", width=1.2) for _ in range(2)], axis=1)
    P.add_bed(wind * (0.25 + 0.35 * v)[:, None])
    # 460: rajada de entrada
    i460 = 0
    g = dsp.bp(dsp.white(rng, n), 500, 3000) * dsp.env_ad(n, 0.004, 0.25, i460)
    P.add_event(460, dsp.stereo(g, 0.6))
    # 500: whoosh Doppler (sobe e desce, pan L → R, pico no 500)
    i500 = at(500, S)
    span = int(0.5 * SR)
    a, b = i500 - span, i500 + span
    w = np.zeros(n)
    loc = np.arange(b - a) - span
    fc_w = 900 + 2600 * np.exp(-(loc / (0.12 * SR)) ** 2)
    seg = dsp.tv_filter(dsp.white(rng, b - a), fc_w, "band", width=0.8)
    env = np.where(loc < 0, np.exp(-(loc / (0.03 * SR)) ** 2), np.exp(-loc / (0.12 * SR)))
    w[a:b] = seg * env * 2.2
    pn = np.clip((np.arange(n) - i500) / (0.25 * SR), -1, 1)
    P.add_event(500, dsp.pan(w, pn) + dsp.stereo(transient(rng, n, i500, 1500, 5000, amp=0.6)))
    # dilatação: taxa 1,0 → 0,5 do 510 ao 539 (afina e desacelera juntos)
    rate = np.interp(ticks, [510, 539], [1.0, 0.5])
    P.map(lambda x: dsp.varispeed(x, rate))
    return P


def horizon(s):
    """O roar + o pad numa parada de fita (0,5 → 0,05), batidas de coração alongando, silêncio exato no 600."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    src_n = n * 3
    mix = roar(rng, src_n, 300, 2500, 0.2) * 0.8
    tp = time(src_n)
    mix += dsp.stereo(sum(np.sin(2 * np.pi * f * tp) for f in (110, 164.8, 261.6)) * 0.08)
    rate = np.interp(t, [0, 3.0], [0.5, 0.05]) ** 1.2
    bed = dsp.varispeed(mix, rate) * np.interp(t, [0, 0.12, 0.6, 1.3, 2.2, 2.98], [0.6, 1.0, 0.4, 0.26, 0.13, 0])[:, None]
    P.add_bed(dsp.lp(bed, 1800))
    for o in s["onsets_intended"]:
        st = at(o["tick"], S)
        m = n - st
        hb = np.zeros(n)
        hb[st:] = dsp.sat(np.sin(2 * np.pi * 50 * time(m)) * dsp.env_ad(m, 0.004, 0.12) * 1.6, 2.5)
        second = st + int(0.22 * SR)  # "tum-tum"
        if second < n:
            hb[second:] += 0.5 * dsp.sat(np.sin(2 * np.pi * 46 * time(n - second)) * dsp.env_ad(n - second, 0.004, 0.1), 2.5)
        P.add_event(o["tick"], dsp.stereo(hb))
        P.mark(o["tick"], 1500, 4000)
    # silêncio digital exato no fim (o filme fica mudo de 600 a 619)
    P.map(lambda x: x * np.interp(t, [0, 2.97, 2.995], [1, 1, 0])[:, None])
    return P


# ------------------------------------------------------------------ Ato VII


def hawking(s):
    """Evaporação: ambiente quase inaudível, brilhos de 6–14 kHz cada vez mais densos e a temperatura subindo."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    amb = dsp.pink(rng, n) * 10 ** (-50 / 20) * 20
    bed = dsp.stereo(amb, 0.8)
    k = 0.0
    while True:
        rate = 3 + 40 * (k / n) ** 2  # Poisson com taxa subindo
        k += rng.exponential(SR / rate)
        if k >= n - 2000:
            break
        i = int(k)
        d = int(rng.uniform(0.015, 0.04) * SR)
        sp = np.sin(2 * np.pi * rng.uniform(6000, 14000) * time(d)) * np.hanning(d) * 0.12 * (0.3 + k / n)
        bed[i:i + d] += dsp.pan(sp, rng.uniform(-0.8, 0.8))
    # o último instante antes do clarão: um aglomerado denso de brilhos (é o pico de energia do som)
    for _ in range(40):
        i = at(697, S) + int(rng.uniform(0, 1.9) * TICK)
        d = int(0.02 * SR)
        if i + d < n:
            bed[i:i + d] += dsp.pan(np.sin(2 * np.pi * rng.uniform(8000, 13000) * time(d)) * np.hanning(d) * 0.3, rng.uniform(-0.9, 0.9))
    i660 = at(660, S)
    m = n - i660
    temp = np.zeros(n)
    temp[i660:] = dsp.sine_sweep(m, 2000, 8000) * np.linspace(0, 0.08, m)
    P.add_bed(bed + dsp.stereo(temp))
    for o in s["onsets_intended"]:
        st = at(o["tick"], S)
        d = int(0.035 * SR)
        x = np.zeros(n)
        seg = sum(np.sin(2 * np.pi * f * time(d)) for f in rng.uniform(7000, 12000, 3)) * np.hanning(2 * d)[d:] * np.clip(np.arange(d) / 30, 0, 1)
        x[st:st + d] = seg[: n - st]
        P.add_event(o["tick"], dsp.pan(x, rng.uniform(-0.5, 0.5)))
    return P


def burst(s):
    """O último clarão: Ré maior com 9ª (Ré–Fá♯–Lá–Mi), ataque de vidro e pad abrindo; sem sub violento."""
    S = s["tick"]
    n = (s["end_tick"] - S) * TICK
    rng = rng_for(s["id"])
    P = Parts(n)
    t = time(n)
    notes = (293.66, 369.99, 440.0, 659.25)
    glass = sum(dsp.bell(n, [f * 2, f * 2 * 2.76, f * 2 * 5.4], [0.6, 0.25, 0.1], 0.9, rng=rng) for f in notes)
    P.add_event(700, dsp.stereo(glass, 0.6))
    padv = np.zeros(n)
    for f in notes + (146.83,):
        for det in (-0.003, 0.003):
            padv += dsp.saw_bl(f * (1 + det), n, 12)
    padv = dsp.tv_filter(padv, np.interp(t, [0, 1.2], [300, 3500]), "low")
    padv *= np.interp(t, [0, 0.5, 1.2], [0, 0.6, 0.6]) * np.exp(-np.maximum(t - 1.2, 0) / 0.9)
    P.add_bed(dsp.stereo(padv * 0.12, 0.8))
    P.map(lambda x: dsp.fade(x, 0.0, 0.05))
    return P


def score_part(s):
    """A trilha (tools/synth/score.py + spec/score.json): sem eventos, só a cama; o onset é o começo."""
    import score
    n = (s["end_tick"] - s["tick"]) * TICK
    P = Parts(n)
    P.add_bed(score.part(s["tick"], s["end_tick"]))
    return P


RECIPES = {
    "sgx_void_in": void_in, "sgx_point": point, "sgx_twin": twin, "sgx_chirp": chirp, "sgx_merge": merge,
    "sgx_ringdown": ringdown, "sgx_disk_ignite": disk_ignite, "sgx_disk_loop": disk_loop, "sgx_disk_loop_ext": disk_loop,
    "sgx_jet": jet, "sgx_pad": pad, "sgx_tidal": tidal, "sgx_fall": fall, "sgx_horizon": horizon,
    "sgx_hawking": hawking, "sgx_burst": burst, "sgx_score_a": score_part, "sgx_score_b": score_part,
}
