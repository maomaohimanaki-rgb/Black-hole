"""Análise do áudio renderizado (docs/AUDIO_DESIGN.md §1, regra de ida e volta).
- rms_norm: RMS da janela de 1 tick (50 ms) que COMEÇA no tick, dividido pelo maior RMS de tick do som.
- onsets: subidas de energia em 4 bandas (< 300 Hz, 300–2 000, 2 000–7 000, > 7 000), janelas de 5 ms;
  o começo do arquivo (primeira janela acima de −60 dB do pico) também conta como onset.
- check(): cada onset pedido tem que aparecer a ±0,5 tick, com rms_norm a ±0,15 do pedido.
v0.2.0."""
import numpy as np

from dsp import SR, TICK, mono, lp, hp, bp

HOP = 220  # ~5 ms
TOL_TICKS = 0.5
TOL_RMS = 0.15


def tick_rms(x):
    m = mono(x)
    n = int(np.ceil(len(m) / TICK))
    pad = np.zeros(n * TICK)
    pad[: len(m)] = m
    return np.sqrt(np.mean(pad.reshape(n, TICK) ** 2, axis=1))


def rms_norm(x):
    r = tick_rms(x)
    return r / (r.max() + 1e-12)


def _band_energy(m):
    n = len(m) // HOP
    out = []
    for y in (lp(m, 300, 4), bp(m, 300, 2000, 2), bp(m, 2000, 7000, 2), hp(m, 7000, 4)):
        y = y[: n * HOP].reshape(n, HOP)
        out.append(np.mean(y ** 2, axis=1))
    return np.array(out)  # (4, n)


def detect_onsets(x, rise_db=4.0, look=4, min_gap_s=0.03):
    """Tempos (s) de onsets: janela cuja energia, em alguma banda, sobe ≥ rise_db sobre o MÁXIMO das
    `look` janelas anteriores (≈ 20 ms) e é relevante (≥ −45 dB do pico daquela banda)."""
    m = mono(x)
    E = _band_energy(m) + 1e-14
    peak = E.max(axis=1, keepdims=True)
    db = 10 * np.log10(E)
    rel = 10 * np.log10(E / peak)
    nov = np.full(E.shape[1], -np.inf)
    for i in range(1, E.shape[1]):
        prev = db[:, max(0, i - look):i].max(axis=1)
        jump = db[:, i] - prev
        ok = rel[:, i] > -45
        if ok.any():
            nov[i] = np.where(ok, jump, -np.inf).max()
    out, strength = [], []
    i = 1
    while i < len(nov):
        if nov[i] >= rise_db:
            # pico local da novidade na vizinhança
            j = i + int(np.argmax(nov[i:i + look]))
            t = j * HOP / SR
            if not out or t - out[-1] >= min_gap_s:
                out.append(t)
                strength.append(float(nov[j]))
            elif nov[j] > strength[-1]:
                # v0.2.0: dois onsets colados → fica o mais forte (um ronco não "ocupa" a vaga de um estalo)
                out[-1], strength[-1] = t, float(nov[j])
            i = j + look
        else:
            i += 1
    # começo do arquivo
    lin = np.mean(m[: (len(m) // HOP) * HOP].reshape(-1, HOP) ** 2, axis=1)
    first = int(np.argmax(lin > lin.max() * 1e-6))
    t0 = first * HOP / SR
    if not out or out[0] - t0 > min_gap_s:
        out.insert(0, t0)
        strength.insert(0, 60.0)
    return np.array(out), np.array(strength)


def spectral(x, frame_ticks=1):
    """Por tick: frequência dominante e centroide (Hz)."""
    m = mono(x)
    n = int(np.ceil(len(m) / TICK))
    dom, cen = [], []
    win = np.hanning(TICK)
    f = np.fft.rfftfreq(TICK, 1 / SR)
    for k in range(n):
        seg = m[k * TICK:(k + 1) * TICK]
        if len(seg) < TICK:
            seg = np.pad(seg, (0, TICK - len(seg)))
        S = np.abs(np.fft.rfft(seg * win))
        if S.sum() < 1e-9:
            dom.append(0.0)
            cen.append(0.0)
            continue
        dom.append(float(f[np.argmax(S)]))
        cen.append(float((f * S).sum() / S.sum()))
    return np.array(dom), np.array(cen)


def check(sound, x):
    """Compara onsets pedidos × medidos. Retorna (lista de linhas, ok)."""
    start = sound["tick"]
    rn = rms_norm(x)
    times, _ = detect_onsets(x)
    det_ticks = times * 20
    rows, ok = [], True
    for o in sound["onsets_intended"]:
        k = o["tick"] - start
        near = det_ticks[np.abs(det_ticks - k) <= TOL_TICKS] if len(det_ticks) else []
        dt = float(min(near, key=lambda d: abs(d - k)) - k) if len(near) else None
        meas = float(rn[k]) if k < len(rn) else 0.0
        good = dt is not None and abs(meas - o["rms_norm"]) <= TOL_RMS
        ok &= good
        rows.append({"tick": o["tick"], "want": o["rms_norm"], "rms": round(meas, 3), "dt": None if dt is None else round(dt, 2), "ok": good})
    return rows, ok
