#!/usr/bin/env python3
"""build/timeline.json (saída do tools/synth/render.py) → BP/scripts/singularity/blackhole/timeline_data.js
com SOUND_CUES (o que tocar e quando), ONSETS (os onsets DETECTADOS no áudio real, em tick do filme) e
ENVELOPE (rms_norm por tick do mix da cutscene, para flashes e brilhos seguirem o som na F4+).
Idempotente. Nunca edite o .js à mão (docs/AUDIO_DESIGN.md §2)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TL = json.loads((ROOT / "build/timeline.json").read_text(encoding="utf-8"))
OUT = ROOT / "BP/scripts/singularity/blackhole/timeline_data.js"

cues = [{"sound": e["sound"], "tick": e["tick"], "end": e["end_tick"], "volume": e["volume"], "mode": e["mode"]} for e in TL["events"]]
onsets = sorted(({"tick": o["tick"], "sound": e["sound"], "rms": o["rms_norm"]} for e in TL["events"] if e["heard_in_cutscene"]
                 for o in e["onsets_abs"]), key=lambda o: (o["tick"], o["sound"]))
end = TL["meta"]["audio_end_tick"]
env = [0.0] * end
for e in TL["events"]:
    if not e["heard_in_cutscene"]:
        continue
    lib = TL["audio_library"][e["file"]]["envelope_rms_norm_20fps"]
    for i, v in enumerate(lib):
        t = e["tick"] + i
        if t < end:
            env[t] = max(env[t], round(v * e["volume"], 3))

js = ("// GERADO por tools/build_timeline.py a partir de build/timeline.json (tools/synth/render.py). NÃO EDITE À MÃO.\n"
      f"export const SOUND_CUES = {json.dumps(cues, ensure_ascii=False)};\n"
      f"export const ONSETS = {json.dumps(onsets)};\n"
      f"export const ENVELOPE = {json.dumps(env)};\n")
if not OUT.exists() or OUT.read_text(encoding="utf-8") != js:
    OUT.write_text(js, encoding="utf-8")
print(f"✓ {OUT.relative_to(ROOT)}: {len(cues)} sons, {len(onsets)} onsets detectados, envelope de {end} ticks")
