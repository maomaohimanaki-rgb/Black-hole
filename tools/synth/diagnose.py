#!/usr/bin/env python3
"""Diagnóstico da ida e volta de um som: python3 tools/synth/diagnose.py sgx_chirp [sgx_tidal …]
Mostra, para cada onset pedido: rms medido × pedido, o onset detectado mais perto e a subida por banda."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import dsp  # noqa: E402
import render  # noqa: E402
from recipes import RECIPES  # noqa: E402

AU = json.loads((Path(__file__).resolve().parents[2] / "spec/audio_cues.json").read_text(encoding="utf-8"))
for sid in sys.argv[1:]:
    s = next(x for x in AU["sounds"] if x["id"] == sid)
    x, g = render.calibrate(s, RECIPES[sid](s))
    x = render.master(x)
    rows, ok = analyze.check(s, x)
    det = analyze.detect_onsets(x)[0] * 20 + s["tick"]
    db = 10 * np.log10(analyze._band_energy(dsp.mono(x)) + 1e-14)
    print(f"== {sid} {'OK' if ok else 'FALHA'}  ganhos: " + " ".join(f"{k}:{v:.3g}" for k, v in g.items()))
    for r in rows:
        if r["ok"]:
            continue
        near = det[np.argmin(np.abs(det - r["tick"]))] if len(det) else None
        j = int((r["tick"] - s["tick"]) * dsp.TICK / analyze.HOP)
        jump = db[:, j:j + 3].max(axis=1) - db[:, max(0, j - 4):j].max(axis=1)
        print(f"   {r['tick']}: rms {r['rms']:.2f}/{r['want']:.2f}  detectado mais perto {near:.2f}  subida por banda (dB) {np.round(jump, 1)}")
