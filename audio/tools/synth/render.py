#!/usr/bin/env python3
"""Motor de áudio da F2 (docs/AUDIO_DESIGN.md §1), tudo num passo idempotente:
  1. render: cada receita (recipes.py) → cama + eventos;
  2. calibração: ajusta o ganho de cada evento até o rms_norm de cada onset pedido bater (±0,15);
  3. master: −16 LUFS integrado, pico ≤ −1 dBFS; .ogg estéreo (2D) e _m.ogg mono (posicional);
  4. análise: ida e volta (onset a ±0,5 tick) → build/timeline.json + build/report.md + espectrogramas;
  5. mixdown: build/singularity_mix.wav (o filme inteiro como se ouve na cutscene) + silêncio em 600–619;
  6. o som de teste do S-05 (estéreo L → R).
FALHA (exit 1) se algum onset não bater ou se houver som em 600–619. Uso: python3 tools/synth/render.py [--quick]
v0.2.0."""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import pyloudnorm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import director  # noqa: E402
import dsp  # noqa: E402
import psycho  # noqa: E402
from dsp import SR, TICK  # noqa: E402
from recipes import RECIPES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
AU = json.loads((ROOT / "spec/audio_cues.json").read_text(encoding="utf-8"))
P = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
NS = P["namespace"]
OUT = ROOT / "RP/sounds/singularity"
BUILD = ROOT / "build"
SD = ROOT / "RP/sounds/sound_definitions.json"
QUICK = "--quick" in sys.argv
METER = pyloudnorm.Meter(SR)


def write_wav(x, path, bits=16):
    x = np.clip(x, -1, 1)
    ch = 1 if x.ndim == 1 else x.shape[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def to_ogg(x, path):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "x.wav"
        write_wav(x, wav)
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "6",
                        "-fflags", "+bitexact", "-flags:a", "+bitexact", str(path)], check=True)


# ------------------------------------------------------------------ calibração


def _marks(s, parts, peak):
    """Marcas de articulação. v0.2.7: um TIQUE MECÂNICO (impulso em ressonância larga, sem nota) e não mais um
    brilho afinado: os brilhos afinados soavam "pim pom" de campainha. Nível relativo ao TRECHO (45 % do pico
    local, ±2 ticks), não ao pico do arquivo; a nota da marca só dá a cor da ressonância."""
    out = np.zeros((parts.n, 2))
    m = int(0.05 * SR)
    t = dsp.time(m)
    rng = np.random.default_rng(sum(map(ord, s["id"])))
    for tick, f in parts.marks:
        st = (tick - s["tick"]) * TICK
        k = min(m, parts.n - st)
        if k <= 0:
            continue
        local = np.abs(peak[max(0, st - 2 * TICK):st + 2 * TICK]).max()
        imp = np.zeros(m)
        q = int(0.001 * SR)
        imp[:q] = rng.standard_normal(q)
        g = dsp.resonator(imp, min(f, 6000), 5) * np.exp(-t / 0.008)
        g = g / (np.abs(g).max() + 1e-12)
        out[st:st + k] += dsp.stereo(g[:k] * 0.45 * local)
    return out


def calibrate(s, parts, iters=80):
    """Ganho por evento (multiplicativo) até cada rms_norm pedido bater. A cama fica fixa.
    Com marcas: calibra, põe as marcas na cama (nível pelo pico) e calibra de novo."""
    start = s["tick"]
    # v0.2.0: o rms_norm é relativo ao pico, então "todos os eventos maiores" também bate; começando
    # pequeno, a solução fica perto da cama e cada evento só cresce o necessário (o chirp ficava 10×
    # abaixo dos próprios acentos).
    # v5: a receita pode sugerir o ponto de partida (parts.hints). Começando todos iguais, o horizonte caía num
    # mínimo ruim: o solver baixava o golpe até o nível da cama e a ida e volta reprovava os batimentos.
    gains = {k: getattr(parts, "hints", {}).get(k, 0.05) for k in parts.events}
    want = {o["tick"]: o["rms_norm"] for o in s["onsets_intended"]}
    bed = parts.bed.copy()

    def mix():
        x = bed.copy()
        for k, e in parts.events.items():
            x += gains[k] * e
        return x

    def err():
        rn = analyze.rms_norm(mix())
        return max((abs(rn[k - start] - want[k]) for k in gains if k in want), default=0.0)

    def rescale():
        """Busca 1D do fator comum de todos os eventos: o ajuste por onset sozinho não enxerga que
        subir todos juntos abafa a cama (o disk_ignite parava com a cama dominando)."""
        base = dict(gains)
        best = (err(), 1.0)
        for c in np.geomspace(1 / 64, 64, 25):
            for k in gains:
                gains[k] = float(np.clip(base[k] * c, 1e-4, 1e4))
            best = min(best, (err(), c))
        for k in gains:
            gains[k] = float(np.clip(base[k] * best[1], 1e-4, 1e4))

    def solve(scale=True):
        for it in range(iters):
            if scale and it % 10 == 0 and gains and not getattr(parts, "hints", None):
                rescale()  # com dica, a escala já é a pretendida
            rn = analyze.rms_norm(mix())
            worst = 0.0
            for k in gains:
                if k not in want:
                    continue
                meas = rn[k - start]
                worst = max(worst, abs(meas - want[k]))
                # v5: zona morta de 0,03 (a tolerância é 0,15). Sem ela, um onset cuja razão é fixada pela forma do
                # próprio evento (o 540 do horizonte: TÁ 0,82 × BOOM 1,0) puxava o ganho para baixo até a cama
                if abs(meas - want[k]) > 0.03:
                    gains[k] = float(np.clip(gains[k] * (want[k] / max(meas, 1e-4)) ** 0.9, 1e-4, 1e4))
            if worst < 0.02:
                break

    solve()
    if parts.marks:
        bed += _marks(s, parts, mix())
        solve(scale=False)  # só ajuste fino: um reescalonamento grande afogaria as marcas
    return mix(), gains


def master(x, sid=None):
    """−16 LUFS integrado com pico ≤ −1 dBFS (o que limitar primeiro).
    v0.4.0: os GOLPES (spec/dramaturgy.json → master.impact_stems) não entram na régua de −16 LUFS. Normalizar
    um golpe de 1 s ao mesmo loudness de uma cama de 30 s era o que deixava a fusão 3 dB abaixo do build: o
    volume do jogo só abaixa, então quem tem que ser maior tem que nascer maior. Golpe = só o pico em −1 dBFS
    (linear: a calibração dos onsets continua valendo); a densidade vem da saturação dentro do próprio golpe."""
    if sid in director.spec().get("master", {}).get("impact_stems", []):
        return x * 10 ** (-1 / 20) / (np.abs(x).max() + 1e-12)
    lufs = METER.integrated_loudness(x if len(x) >= 0.4 * SR else np.pad(x, ((0, int(0.4 * SR)), (0, 0))))
    g_lufs = 10 ** ((-16 - lufs) / 20) if np.isfinite(lufs) else 1.0
    g_peak = 10 ** (-1 / 20) / (np.abs(x).max() + 1e-12)
    return x * min(g_lufs, g_peak)


# ------------------------------------------------------------------ análise para o timeline


def library_entry(x, fname):
    dom, cen = analyze.spectral(x)
    rn = analyze.rms_norm(x)
    times, strength = analyze.detect_onsets(x)
    onsets = []
    for t, st in zip(times, strength):
        k = min(int(t * 20), len(rn) - 1)
        onsets.append({"t_local_s": round(float(t), 4), "strength": round(float(st), 2), "rms_norm": round(float(rn[k]), 3), "dominant_hz": round(float(dom[k]), 1)})
    m = dsp.mono(x)
    S = np.abs(np.fft.rfft(m))
    f = np.fft.rfftfreq(len(m), 1 / SR)
    return {
        "duration_s": round(len(x) / SR, 4), "sample_rate": SR, "rms_peak": round(float(analyze.tick_rms(x).max()), 5),
        "dominant_hz": round(float(f[np.argmax(S)]), 1), "spectral_centroid_hz": round(float((f * S).sum() / S.sum()), 1),
        "onsets": onsets,
        "envelope_rms_norm_20fps": [round(float(v), 3) for v in rn],
        "envelope_dominant_hz_20fps": [round(float(v), 1) for v in dom],
        "envelope_centroid_hz_20fps": [round(float(v), 1) for v in cen],
    }


def spectrogram(x, sid, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = dsp.mono(x)
    fig, ax = plt.subplots(figsize=(10, 3), dpi=80)
    ax.specgram(m + 1e-9, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-120)
    ax.set_ylim(20, 16000)
    ax.set_yscale("log")
    ax.set_title(sid)
    ax.set_xlabel("s")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


# ------------------------------------------------------------------ principal


def main():
    # v5: o 32' resultante tem que existir antes de qualquer coisa (tools/synth/check_organ.py)
    if subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "check_organ.py")]).returncode:
        sys.exit("✗ o 32' resultante do órgão não apareceu")
    events, library, report, failed = [], {}, [], []
    stems = {}
    for i, s in enumerate(AU["sounds"], start=1):
        sid = s["id"]
        parts = RECIPES[sid](s)
        x, gains = calibrate(s, parts)
        x = master(x, sid)
        if s["channels"]["cutscene_2d"] == "mono" or not s["heard_in_cutscene"]:
            x = dsp.stereo(dsp.mono(x))
        rows, ok = analyze.check(s, x)
        if not ok:
            failed.append(sid)
        # v0.4.0: a ida e volta confere o som CRU (o contrato com o storyboard); o que vai para o jogo e para o
        # mixdown é o som DIRIGIDO (spec/dramaturgy.json), conferido depois no mix pelo psycho.py
        x = director.apply(x, sid, s["tick"])
        stems[sid] = x
        lufs = METER.integrated_loudness(x)
        report.append((sid, rows, ok, gains, lufs, float(20 * np.log10(np.abs(x).max() + 1e-12))))
        write_wav(x, BUILD / "stems" / f"{sid}.wav")
        to_ogg(x, OUT / f"{sid}.ogg")
        to_ogg(dsp.mono(x), OUT / f"{sid}_m.ogg")
        library[f"{sid}.ogg"] = library_entry(x, f"{sid}.ogg")
        if not QUICK:
            spectrogram(x, sid, BUILD / "spectrograms" / f"{sid}.png")
        mode = "both" if s["heard_in_cutscene"] and s["heard_outside_cutscene"] else ("cutscene" if s["heard_in_cutscene"] else "outside")
        events.append({
            "id": i, "sound": sid, "file": f"{sid}.ogg", "tick": s["tick"], "end_tick": s["end_tick"], "volume": s["volume"],
            "pitch": s.get("pitch", 1.0), "mode": mode, "heard_in_cutscene": s["heard_in_cutscene"],
            "heard_outside_cutscene": s["heard_outside_cutscene"], "analysis_ref": f"{sid}.ogg",
            "onsets_abs": [{"tick": round(s["tick"] + o["t_local_s"] * 20, 2), "time_s": round(s["tick"] / 20 + o["t_local_s"], 4),
                            "strength": o["strength"], "rms_norm": o["rms_norm"]} for o in library[f"{sid}.ogg"]["onsets"]],
        })
        print(f"  {'✓' if ok else '✗'} {sid:20s} {lufs:6.1f} LUFS  " + " ".join(f"{r['tick']}:{r['rms']:.2f}/{r['want']:.2f}{'' if r['ok'] else '✗'}" for r in rows))

    # mixdown: a cutscene inteira (2D, com os volumes do jogo)
    end = AU["meta"]["audio_end_tick"]
    mix = np.zeros((end * TICK, 2))
    for s in AU["sounds"]:
        if not s["heard_in_cutscene"]:
            continue
        a = s["tick"] * TICK
        x = stems[s["id"]] * s["volume"]
        mix[a:a + len(x)] += x[: len(mix) - a]
    peak = np.abs(mix).max()
    mix *= 10 ** (-1 / 20) / peak
    silence = mix[600 * TICK:620 * TICK]
    sil_db = 20 * np.log10(np.abs(silence).max() + 1e-20)
    if sil_db > -90:
        failed.append(f"silêncio 600–619 ({sil_db:.1f} dBFS)")
    ok_ps, ps = psycho.check(mix)
    if not ok_ps:
        failed += [f"{mid}: {r['name']}" for mid, rows in ps for r in rows if not r["ok"]]
    write_wav(mix, BUILD / "singularity_mix.wav")
    to_ogg(mix, BUILD / "singularity_mix.ogg")
    # MP3 para ouvir no celular antes do jogo (qualquer player toca)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(BUILD / "singularity_mix.wav"), "-c:a", "libmp3lame",
                    "-b:a", "192k", "-fflags", "+bitexact", str(BUILD / "singularity_mix.mp3")], check=True)

    # S-05: tom com pulsos, pan L → R em 4 s, duas vezes
    t = dsp.time(int(SR * 8.5))
    sig = 0.5 * np.sin(2 * np.pi * 440 * t) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 4 * t)))
    to_ogg(dsp.pan(sig, np.clip((t % 4.25) / 4.0, 0, 1) * 2 - 1), OUT / "sgx_spike_pan.ogg")

    sd = json.loads(SD.read_text(encoding="utf-8"))
    sd["sound_definitions"][f"{NS}:sgx2d_spike_pan"] = {"category": "ui", "sounds": [
        {"name": "sounds/singularity/sgx_spike_pan", "is3D": False, "stream": False, "load_on_low_memory": True, "volume": 1.0}]}
    SD.write_text(json.dumps(sd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    timeline = {"meta": {"name": "singularity_timeline", "tick_rate": 20, "audio_end_tick": end,
                         "sources": {"spec": "spec/audio_cues.json", "synth": "tools/synth/render.py"}},
                "events": events, "audio_library": library}
    (BUILD / "timeline.json").write_text(json.dumps(timeline, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Relatório do áudio (gerado por tools/synth/render.py)", "",
             f"Silêncio 600–619 no mixdown: **{sil_db:.1f} dBFS** (meta < −90).", "",
             "| Som | LUFS | Pico dBFS | Onsets (tick: medido/pedido, Δtick) | OK |", "|---|---|---|---|---|"]
    for sid, rows, ok, gains, lufs, pk in report:
        on = " · ".join(f"{r['tick']}: {r['rms']:.2f}/{r['want']:.2f}, Δ{r['dt']}" for r in rows)
        lines.append(f"| `{sid}` | {lufs:.1f} | {pk:.1f} | {on} | {'✅' if ok else '❌'} |")
    lines += ["", "Dramaturgia (impacto, vácuo, relógio do mundo): `build/psycho_report.md` e `build/psycho.png`.", "", "Espectrogramas: `build/spectrograms/<som>.png`. Mixdown: `build/singularity_mix.wav` / `.ogg`."]
    (BUILD / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failed:
        print("✗ áudio reprovado na ida e volta: " + ", ".join(failed))
        sys.exit(1)
    print(f"✓ áudio: {len(AU['sounds'])} sons, todos os onsets batem · silêncio 600–619 {sil_db:.0f} dBFS · build/singularity_mix.wav")


if __name__ == "__main__":
    main()
