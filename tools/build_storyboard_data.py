#!/usr/bin/env python3
"""spec/storyboard.json + spec/layout.json + spec/audio_cues.json → BP/scripts/singularity/blackhole/storyboard_data.js
(ARCHITECTURE §2). Idempotente. Nunca edite o .js à mão: edite o spec (ou tools/build_storyboard_json.py) e rode de novo.
v0.1.0: letterbox convertido para "altura visível em fração da largura" (fechado = 0), que interpola liso até o preto."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SB = json.loads((ROOT / "spec/storyboard.json").read_text(encoding="utf-8"))
LY = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
AU = json.loads((ROOT / "spec/audio_cues.json").read_text(encoding="utf-8"))
PAL = json.loads((ROOT / "spec/palette.json").read_text(encoding="utf-8"))
OUT = ROOT / "BP/scripts/singularity/blackhole/storyboard_data.js"

# Cores de flash do catálogo da UI (tools/gen_ui.py usa a mesma lista: índice = dezena do canal FL).
FLASH_COLORS = ["#FFFFFF", "#F2F6FF", "#FFE2C4", "#C9C2FF", "#000000", "#DDE6FF", "#E9E4FF", "#FFD2A8"]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def nearest_flash(color):
    c = hex_rgb(color)
    return min(range(len(FLASH_COLORS)), key=lambda i: sum((a - b) ** 2 for a, b in zip(c, hex_rgb(FLASH_COLORS[i]))))


def vis(ratio):
    return 0.0 if ratio == "closed" else round(1.0 / float(ratio), 5)


def hud_key(block, i):
    return f"sgx.hud.{block.lower()}.{i}"


blocks = []
hud_lang = {}
for b in SB["blocks"]:
    hud = []
    for i, h in enumerate(b.get("hud", [])):
        e = {"t": h["t"], "ch": h["ch"]}
        if "clear" in h:
            e["clear"] = h["clear"]
        if h["ch"] in ("SB", "HD", "TT", "TT2"):
            e["key"] = hud_key(b["id"], i)
            hud_lang[e["key"]] = h["text"]
        else:
            e["value"] = int(h["text"])
        hud.append(e)
    flash = []
    for f in b.get("flash", []):
        flash.append({"t": f["t"], "level": f["level"], "kind": f.get("kind", "white"),
                      "color": nearest_flash(f.get("color", "#FFFFFF")), "dur": f.get("dur")})
    blocks.append({
        "id": b["id"], "act": b["act"], "name": b["name"], "ticks": b["ticks"],
        "camera": [{k: v for k, v in c.items() if k != "note"} for c in b["camera"]],
        "hud": hud, "flash": flash,
        "shake": [{"t": s["t"], "level": s["level"]} for s in b.get("shake", [])],
        "vfx": [{"t": v["t"], "fx": v["fx"]} for v in b.get("vfx", [])],
        "destruction": [{"t": d["t"], "op": d.get("op", "")} for d in b.get("destruction", [])],
    })

sounds = [{"id": s["id"], "tick": s["tick"], "end": s["end_tick"], "volume": s.get("volume", 1.0),
           "cutscene": s["heard_in_cutscene"], "outside": s["heard_outside_cutscene"]} for s in AU["sounds"]]

data = {
    "meta": {"filmTicks": SB["meta"]["film_ticks"], "outroTicks": SB["meta"]["outro_ticks"], "tickRate": SB["meta"]["tick_rate"]},
    "acts": SB["acts"],
    "blocks": blocks,
    "letterbox": [{"t": k["t"], "vis": vis(k["ratio"]), **({"ease": k["ease"]} if "ease" in k else {})} for k in SB["letterbox_curve"]],
    "grade": [{"t": k["t"], "redshift": k["redshift"], **({"ease": k["ease"]} if "ease" in k else {})} for k in SB["grade_curve"]],
    "scaleCurve": LY["black_hole"]["scale_curve"],
    "halfOrbits": LY["binary"]["half_orbit_ticks"],
    "disk": {"rings": LY["disk"]["rings"], "ignite": LY["disk"]["ignite_ticks"]},
    "jets": {"tOn": LY["jets"]["t_on"], "tFade": LY["jets"]["t_fade"], "up": LY["jets"]["up_length"]},
    "gwShell": LY["gw_shell"],
    "sounds": sounds,
    "flashColors": FLASH_COLORS,
}
for sc in data["scaleCurve"]:
    sc.pop("why", None)

js = ("// GERADO por tools/build_storyboard_data.py a partir de spec/. NÃO EDITE À MÃO.\n"
      "export const DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
      "export const HUD_TEXT = " + json.dumps(hud_lang, ensure_ascii=False, indent=1) + ";\n")
OUT.parent.mkdir(parents=True, exist_ok=True)
old = OUT.read_text(encoding="utf-8") if OUT.exists() else None
if old != js:
    OUT.write_text(js, encoding="utf-8")
print(f"✓ {OUT.relative_to(ROOT)}: {len(blocks)} blocos, {sum(len(b['camera']) for b in blocks)} keyframes, {len(hud_lang)} textos de HUD")
