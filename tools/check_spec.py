#!/usr/bin/env python3
"""Confere a coerência entre spec/storyboard.json, spec/audio_cues.json e spec/layout.json e gera docs/BEAT_TABLE.md.
Falha (exit 1) em qualquer divergência. Rode depois de mexer em qualquer arquivo de spec/."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sb = json.loads((ROOT / "spec/storyboard.json").read_text(encoding="utf-8"))
au = json.loads((ROOT / "spec/audio_cues.json").read_text(encoding="utf-8"))
ly = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
errs = []
def err(m): errs.append(m)

N = sb["meta"]["film_ticks"]
blocks = sb["blocks"]
sounds = {s["id"]: s for s in au["sounds"]}

# 1) blocos contíguos, dentro dos atos
pos = 0
acts = {a["id"]: a["ticks"] for a in sb["acts"]}
for b in blocks:
    a, z = b["ticks"]
    if a != pos: err(f"{b['id']}: começa em {a}, esperado {pos}")
    if z < a: err(f"{b['id']}: fim antes do começo")
    A = acts[b["act"]]
    if not (A[0] <= a and z <= A[1]): err(f"{b['id']}: fora do ato {b['act']} {A}")
    pos = z + 1
if pos != N: err(f"blocos terminam em {pos - 1}, filme tem {N} ticks")

# 2) eventos dentro do bloco; câmera ordenada e contínua
EASES = {"linear", "step", "inQuad", "outQuad", "inOutQuad", "inCubic", "outCubic", "inOutCubic", "inExpo", "outExpo", "inSine", "outSine", "inOutSine", "outBack", "outBounce"}
prev_last = None
for b in blocks:
    a, z = b["ticks"]
    for key in ("vfx", "hud", "flash", "shake", "destruction"):
        for e in b.get(key, []):
            if not (a <= e["t"] <= z): err(f"{b['id']}.{key}: t={e['t']} fora de [{a},{z}]")
    cam = b["camera"]
    ts = [k["t"] for k in cam]
    if ts != sorted(ts): err(f"{b['id']}: keyframes fora de ordem")
    if cam[0]["t"] != a: err(f"{b['id']}: 1º keyframe em {cam[0]['t']}, bloco começa em {a}")
    for k in cam:
        if not (a <= k["t"] <= z): err(f"{b['id']}: keyframe {k['t']} fora do bloco")
        if k["ease"] not in EASES: err(f"{b['id']}: ease desconhecido {k['ease']}")
    if prev_last is not None and not cam[0].get("cut") and cam[0]["pos"] != prev_last["pos"]:
        err(f"{b['id']}: câmera pula do bloco anterior sem 'cut' ({prev_last['pos']} → {cam[0]['pos']})")
    prev_last = cam[-1]
    for sid in b.get("audio", []):
        if sid not in sounds: err(f"{b['id']}: som {sid} não existe em audio_cues")
        else:
            s = sounds[sid]
            if s["end_tick"] < a or s["tick"] > z: err(f"{b['id']}: som {sid} [{s['tick']},{s['end_tick']}] não toca no bloco")
    for h in b.get("hud", []):
        if h["ch"] not in sb["hud_channels"]: err(f"{b['id']}: canal de HUD {h['ch']}")

# 3) áudio: onsets dentro do som; silêncios
for s in au["sounds"]:
    for o in s["onsets_intended"]:
        if not (s["tick"] <= o["tick"] <= s["end_tick"]): err(f"{s['id']}: onset {o['tick']} fora de [{s['tick']},{s['end_tick']}]")
        if not (0 <= o["rms_norm"] <= 1): err(f"{s['id']}: rms_norm {o['rms_norm']}")
for s in au["sounds"]:
    if s["heard_in_cutscene"] and s["tick"] < 620 and s["end_tick"] > 600:
        err(f"silêncio absoluto 600–619 violado por {s['id']} (cutscene)")

# 4) regras de continuidade que dá para checar
shake10 = sorted(e["t"] for b in blocks for e in b.get("shake", []) if e["level"] >= 10)
if shake10 != [241, 360]: err(f"shake 10 só em 241 e 360; achei {shake10}")
n4 = sorted(e["t"] for b in blocks for e in b.get("flash", []) if e["level"] == "N4")
if n4 != [240, 360, 700]: err(f"flash N4 só em 240, 360, 700; achei {n4}")
for bid in ("B11", "B19", "B20", "B21", "B22"):
    b = next(x for x in blocks if x["id"] == bid)
    if b.get("shake"): err(f"{bid} tem que ter shake 0")
hud_after = [(b["id"], h["t"]) for b in blocks for h in b.get("hud", []) if 580 <= h["t"] and h["ch"] not in ("TT", "TT2")]
if hud_after: err(f"HUD depois do 580: {hud_after}")

# 5) órbita: ondulações = meias-órbitas = acentos do chirp
half = ly["binary"]["half_orbit_ticks"]
rip = sorted(e["t"] for b in blocks for e in b.get("vfx", []) if e["fx"] == "ground_ripple")
if rip != half: err(f"ondulações {rip} ≠ meias-órbitas {half}")
chirp = [o["tick"] for o in sounds["sgx_chirp"]["onsets_intended"]]
if chirp[:-1] != half or chirp[-1] != 239: err(f"acentos do chirp {chirp} ≠ meias-órbitas + 239")

# 6) curvas
for name in ("letterbox_curve", "grade_curve"):
    ts = [p["t"] for p in sb[name]]
    if ts != sorted(ts) or ts[0] != 0 or ts[-1] > N: err(f"{name}: ticks fora de ordem/limite")

# 7) magnetar (esboço): blocos contíguos, pulsos a cada ~151 ticks, clarão de 4 ticks
mg = json.loads((ROOT / "spec/magnetar_outline.json").read_text(encoding="utf-8"))
pos = 0
for b in mg["blocks"]:
    if b["ticks"][0] != pos: err(f"magnetar {b['id']}: começa em {b['ticks'][0]}, esperado {pos}")
    pos = b["ticks"][1] + 1
if pos != mg["meta"]["film_ticks"]: err(f"magnetar termina em {pos - 1}")
pp = mg["rotation_pulses"]
if any(abs((b - a) - mg["meta"]["rotation_period_ticks"]) > 0.5 for a, b in zip(pp, pp[1:])): err(f"pulsos do magnetar fora do período: {pp}")
w = mg["flare"]["white_ticks"]
if (w[1] - w[0] + 1) / 20 != 0.2: err("o clarão do magnetar tem que durar 0,2 s (4 ticks)")
if not (mg["silence"][1] < w[0]): err("o silêncio do magnetar vem ANTES do clarão")

if errs:
    print("✗ spec com problemas:"); [print("  -", e) for e in errs]; sys.exit(1)

# ---------------------------------------------------------------- tabela de beats (Markdown)
def fmt_sh(b): return ", ".join(f"{e['level']}@{e['t']}" for e in b.get("shake", [])) or "—"
def fmt_fl(b): return ", ".join(f"{e['level']}@{e['t']}" for e in b.get("flash", [])) or "—"
def fmt_hud(b): return "; ".join(f"`{h['text']}`@{h['t']}" for h in b.get("hud", [])) or "—"
def fmt_au(b):
    out = []
    for sid in b.get("audio", []):
        s = sounds[sid]; ons = [o["tick"] for o in s["onsets_intended"] if b["ticks"][0] <= o["tick"] <= b["ticks"][1]]
        out.append(f"{sid}" + (f" ({', '.join(map(str, ons))})" if ons else ""))
    return "; ".join(out) or "**silêncio**"
lines = ["# BEAT TABLE — gerado de spec/storyboard.json + spec/audio_cues.json", "",
         "Gerado por `python3 tools/check_spec.py`. Não edite à mão: mude o JSON e rode de novo.", ""]
for act in sb["acts"]:
    lines += [f"## Ato {act['id']} — {act['name']} (ticks {act['ticks'][0]}–{act['ticks'][1]})", "",
              "| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |", "|---|---|---|---|---|---|"]
    for b in blocks:
        if b["act"] == act["id"]:
            lines.append(f"| **{b['id']}** {b['name']} | {b['ticks'][0]}–{b['ticks'][1]} | {fmt_au(b)} | {fmt_hud(b)} | {fmt_fl(b)} | {fmt_sh(b)} |")
    lines.append("")
lines += ["## Letterbox (razão de aspecto alvo)", "", " → ".join(f"{p['ratio']}@{p['t']}" for p in sb["letterbox_curve"]), "",
          "## Desvio para o vermelho (overlay)", "", " → ".join(f"{p['redshift']}@{p['t']}" for p in sb["grade_curve"]), ""]
(ROOT / "docs/BEAT_TABLE.md").write_text("\n".join(lines), encoding="utf-8")
print(f"✓ spec coerente: {len(blocks)} blocos, {len(au['sounds'])} sons, {len(half)} meias-órbitas · magnetar {len(mg['blocks'])} blocos · docs/BEAT_TABLE.md gerado")
