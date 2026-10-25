"""O ouvido automático (v0.4.0): mede o mixdown do jeito que o corpo sente e REPROVA o que não tiver impacto.
A ida e volta (analyze.py) garante que o som bate com o storyboard; este garante que ele FUNCIONA:
  - o impacto é a coisa mais alta da vizinhança (loudness de 400 ms, como o LUFS momentâneo);
  - o grave VOLTA no golpe (sub < 120 Hz no golpe × no vácuo);
  - o celular ouve o golpe (banda 150–600 Hz, P-48);
  - o golpe é o ataque mais nítido da vizinhança (fluxo espectral);
  - o relógio do mundo não é linear (antecipação, despencada, ricochete, balanço, assíntota);
  - o filme tem respiração (faixa dinâmica) e o 600–619 é mudo.
Uso: python3 tools/synth/psycho.py [mix.wav]  (sem argumento: build/singularity_mix.wav). Gera
build/psycho_report.md e build/psycho.png. O render.py chama check() e falha o build se reprovar."""
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dsp  # noqa: E402
from dsp import SR, TICK  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _db(p):
    return 10 * np.log10(p + 1e-12)


def _tick_power(y):
    n = len(y) // TICK
    return (y[: n * TICK].reshape(n, TICK) ** 2).mean(1)


def _band(m, lo, hi):
    # 8ª ordem: com 4ª, um chirp a 240 Hz vazava −24 dB para a banda do sub e "enchia" o vácuo
    if lo <= 0:
        sos = signal.butter(8, hi / (SR / 2), "low", output="sos")
    else:
        sos = signal.butter(8, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos")
    return _db(_tick_power(signal.sosfilt(sos, m)))


def measure(mix):
    """Curvas por tick (20/s): loudness de 400 ms, sub, corpo do celular, agudo e fluxo espectral."""
    m = dsp.mono(mix)
    p = _tick_power(m)
    # 200 ms: a integração temporal da loudness para sons curtos fica na casa de 100–200 ms. Com 400 ms (o
    # LUFS momentâneo) a média engolia o vácuo de 80 ms junto com o golpe e media o desenho, não o golpe.
    mom = _db(np.convolve(p, np.ones(4) / 4, "same"))
    f, _, S = signal.spectrogram(m, SR, nperseg=2048, noverlap=2048 - TICK)
    # força de ataque em 24 bandas críticas (escala Bark, como o ouvido divide o espectro): soma das subidas de
    # energia em dB, só acima de −80 dB (somar as 1025 raias lineares media o chiado de fundo, não o golpe)
    edges = 600 * np.sinh(np.linspace(np.arcsinh(40 / 600), np.arcsinh(16000 / 600), 25))
    B = np.stack([S[(f >= a) & (f < b)].sum(0) for a, b in zip(edges[:-1], edges[1:])])
    Bd = np.maximum(10 * np.log10(B + 1e-14), -80)
    flux = np.r_[0, np.maximum(np.diff(Bd, axis=1), 0).sum(0)]
    n = len(p)
    flux = np.pad(flux, (0, max(0, n - len(flux))))[:n]
    side = (mix[:, 0] - mix[:, 1]) / 2
    width = _db(_tick_power(side)) - _db(p)  # v5.2: largura estéreo (lado − meio, dB): a parede fecha o estéreo
    return {"rms": _db(p), "mom": mom, "sub": _band(m, 0, 120), "body": _band(m, 150, 600),
            "hi": _band(m, 4000, 16000), "air": _band(m, 1000, 8000), "width": width, "flux": flux}


def _w(a, b):
    return slice(int(round(a)), int(round(b)))


def check_moment(M, C, rate=None):
    imp = M["impact"]
    K = M["checks"]
    ph = {p["type"]: p for p in M["phases"]}
    vac = ph["vacuum"]
    inh = ph["inhale"]
    build = _w(imp - 60, vac["from"])
    after = _w(imp, imp + 10)
    rows = []

    def row(name, val, want, ok, unit="dB"):
        rows.append({"name": name, "val": round(float(val), 2), "want": want, "unit": unit, "ok": bool(ok)})

    d = C["mom"][after].max() - C["mom"][build].max()
    row("impacto acima do build (200 ms)", d, f"≥ {K['impact_over_build_db']}", d >= K["impact_over_build_db"])
    d = C["sub"][_w(imp, imp + 6)].max() - C["sub"][_w(vac["from"], imp)].mean()
    row("grave volta no golpe (sub golpe − vácuo)", d, f"≥ {K['sub_return_db']}", d >= K["sub_return_db"])
    d = C["body"][_w(imp, imp + 4)].max() - np.percentile(C["body"][build], 90)
    row("celular ouve o golpe (150–600 Hz)", d, f"≥ {K['body_over_build_db']}", d >= K["body_over_build_db"])
    w = int(K["flux_is_max_s"] * 20)
    nb = C["flux"][_w(imp - w, imp + w)]
    top = C["flux"][_w(imp - 1, imp + 2)].max()
    row("ataque mais nítido da vizinhança (fluxo)", top / (nb.max() + 1e-12), "= 1,0", top >= nb.max() - 1e-9, "×")
    d = C["sub"][_w(inh["to"] - 6, inh["to"])].mean() - C["sub"][_w(inh["from"] - 8, inh["from"])].mean()
    row("inspiração tira o grave (sub fim − começo)", d, "< 0", d < 0)
    if rate is not None and "rate" in K:
        R = K["rate"]
        tk = np.arange(len(rate)) / TICK
        pre = rate[(tk > vac["from"] - 3) & (tk < imp)]  # só a inspiração (os soluços antes não contam)
        row("antecipação: o mundo acelera antes", pre.max(), f"≥ {R['anticipation_min']}", pre.max() >= R["anticipation_min"], "×")
        slam = rate[(tk >= imp) & (tk < imp + 3)].min()
        row("despencada no golpe (taxa mínima, 3 ticks)", slam, f"≤ {R['slam_max']}", slam <= R["slam_max"], "×")
        post = rate[(tk >= imp) & (tk < imp + 10)]
        reb = post[np.argmin(post):].max() - slam
        row("ricochete depois da despencada", reb, f"≥ {R['rebound_min']}", reb >= R["rebound_min"], "×")
        seg = rate[(tk >= imp + 1) & (tk < imp + 30)][:: TICK // 10]
        ext = int(((np.diff(np.sign(np.diff(seg))) != 0)).sum())
        row("balanço (extremos da taxa em 1,5 s)", ext, f"≥ {R['wobble_extrema_min']}", ext >= R["wobble_extrema_min"], "")
        endr = rate[(tk >= 596) & (tk < 598)].mean()
        row("assíntota: a taxa tende a zero no horizonte", endr, f"≤ {R['end_max']}", endr <= R["end_max"], "×")
    if "wall" in K:
        # v5.2: a parede do ZA WARUDO (volume constante que aperta por dentro e é cortada)
        W = K["wall"]
        a, c = W["from"], W["cut"]
        mom = C["mom"][_w(a, c - 2)]
        rng_db = np.percentile(mom, 90) - np.percentile(mom, 10)
        row("parede: volume constante (p90 − p10)", rng_db, f"≤ {W['flat_range_db']}", rng_db <= W["flat_range_db"])
        d = C["width"][_w(a - 4, a + 4)].mean() - C["width"][_w(c - 8, c)].mean()
        row("parede: o estéreo fecha (largura início − fim)", d, f"≥ {W['narrow_db']}", d >= W["narrow_db"])
        d = C["air"][_w(c - 3, c)].mean() - C["air"][_w(c + 1, c + 4)].mean()
        row("corte: o mundo some (1–8 kHz, antes − depois)", d, f"≥ {W['cut_drop_db']}", d >= W["cut_drop_db"])
    return rows


def check(mix, write=True):
    """Mede o mix (estéreo, 0 = tick 0) e devolve (ok, linhas). Escreve o relatório e o gráfico."""
    import director
    D = director.spec()
    C = measure(mix)
    rate = director.curves()["rate"]
    out, ok = [], True
    for M in D["moments"]:
        rows = check_moment(M, C, rate)
        ok &= all(r["ok"] for r in rows)
        out.append((M["id"], rows))
    G = D["global_checks"]
    live = np.r_[C["mom"][20:262], C["mom"][282:596], C["mom"][624:740]]
    dr = np.percentile(live, 97) - np.percentile(live, 10)
    sil = 20 * np.log10(np.abs(mix[600 * TICK:620 * TICK]).max() + 1e-20)
    grows = [{"name": "respiração do filme (loudness p97 − p10)", "val": round(float(dr), 2), "want": f"≥ {G['dynamic_range_db']}",
              "unit": "dB", "ok": bool(dr >= G["dynamic_range_db"])},
             {"name": "silêncio 600–619", "val": round(float(sil), 1), "want": f"< {G['silence_600_619_dbfs']}", "unit": "dBFS",
              "ok": bool(sil < G["silence_600_619_dbfs"])}]
    ok &= all(r["ok"] for r in grows)
    out.append(("global", grows))
    if write:
        report(out, ok)
        plot(C, rate, D)
    return ok, out


def report(out, ok):
    L = ["# Relatório psicoacústico (gerado por tools/synth/psycho.py)", "",
         f"Resultado: **{'aprovado' if ok else 'REPROVADO'}**. Regras e porquês: `docs/SOUND_DIRECTION.md`.", ""]
    for mid, rows in out:
        L += [f"## {mid}", "", "| Medida | Valor | Meta | OK |", "|---|---|---|---|"]
        L += [f"| {r['name']} | {r['val']} {r['unit']} | {r['want']} | {'✅' if r['ok'] else '❌'} |" for r in rows]
        L.append("")
    p = ROOT / "build/psycho_report.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L) + "\n", encoding="utf-8")


def plot(C, rate, D, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ts = np.arange(len(C["mom"])) / 20
    fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True, dpi=70)
    ax[0].plot(ts, C["rms"], lw=0.6, alpha=0.6, label="rms por tick")
    ax[0].plot(ts, C["mom"], lw=1.6, label="loudness 200 ms")
    ax[0].set_ylim(-60, 0)
    ax[1].plot(ts, C["sub"], label="sub < 120 Hz")
    ax[1].plot(ts, C["body"], label="celular 150–600 Hz")
    ax[1].plot(ts, C["hi"], label="> 4 kHz")
    ax[1].set_ylim(-75, 0)
    ax[2].plot(ts, C["flux"] / (np.percentile(C["flux"], 99.5) + 1e-12), lw=0.7)
    ax[2].set_ylabel("fluxo (ataques)")
    tr = np.arange(len(rate)) / SR
    ax[3].plot(tr[::64], rate[::64], color="crimson")
    ax[3].set_ylabel("relógio do mundo (taxa)")
    ax[3].set_ylim(-0.05, 1.3)
    for a in ax:
        a.grid(alpha=0.3)
        for M in D["moments"]:
            a.axvline(M["impact"] / 20, color="k", lw=0.8, ls="--")
    ax[0].legend(loc="lower left")
    ax[1].legend(loc="lower left")
    ax[3].set_xticks(np.arange(0, 39, 1))
    fig.tight_layout()
    fig.savefig(path or ROOT / "build/psycho.png")
    plt.close(fig)


def load_wav(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32767
        return x.reshape(-1, w.getnchannels())


if __name__ == "__main__":
    x = load_wav(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/singularity_mix.wav")
    ok, out = check(x)
    for mid, rows in out:
        print(f"{mid}:")
        for r in rows:
            print(f"  {'✓' if r['ok'] else '✗'} {r['name']}: {r['val']} {r['unit']} (meta {r['want']})")
    sys.exit(0 if ok else 1)
