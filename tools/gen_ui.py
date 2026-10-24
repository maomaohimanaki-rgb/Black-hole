#!/usr/bin/env python3
"""Gera RP/ui/hud_screen.json: o barramento por título (ARCHITECTURE §4.6, VISUAL_TECH §8).
- Esconde todo título com "SGX" (P-13: a condição vai em title_frame/title e title_frame/title_background).
- Controles próprios entram por modifications/insert_back no root_panel (P-14), 1 painel por canal (P-16).
- Canal LB: letterbox com a altura visível em %x (pela largura, P-17), barras "fill" em cima e embaixo.
  LB=c (1–98) → altura visível = (99 − c)/98 · 56,25 %x ; LB=99 = fechado (preto).
- Canal FL: flash. Dezena = cor (FLASH_COLORS), unidade = alfa (1–9 → /9).
- Canal RS: desvio para o vermelho, 1–20.  Canal IN: impacto negativo (01).
Nada aqui é texto: legendas e HUD técnico vão pela actionbar na F1 (provisório; PNG assado na F3, P-25)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "RP/ui/hud_screen.json"
FLASH_COLORS = ["#FFFFFF", "#F2F6FF", "#FFE2C4", "#C9C2FF", "#000000", "#DDE6FF", "#E9E4FF", "#FFD2A8"]  # = build_storyboard_data.py
WHITE = "textures/sgx/ui/white"
MARK = "SGX"


def rgb(h):
    h = h.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def has(token):
    return {"binding_type": "view", "source_property_name": f"(not ((#text - '{token}') = #text))", "target_property_name": "#visible"}


GLOBAL = {"binding_name": "#hud_title_text_string", "binding_name_override": "#text", "binding_type": "global"}


def gated(token, body):
    body = dict(body)
    body["bindings"] = [GLOBAL, has(token)]
    return body


ui = {"namespace": "hud"}

# P-13: esconder o título do barramento (nos filhos, não na raiz criada por fábrica)
hide = {"binding_type": "view", "source_property_name": f"((#text - '{MARK}') = #text)", "target_property_name": "#visible"}
ui["hud_title_text/title_frame/title"] = {"bindings": [GLOBAL, hide]}
ui["hud_title_text/title_frame/title_background"] = {"bindings": [GLOBAL, hide]}

ui["root_panel"] = {"modifications": [{"array_name": "controls", "operation": "insert_back",
                                       "value": [{"sgx_root@hud.sgx_root": {}}]}]}

ui["sgx_full_image"] = {"type": "image", "texture": WHITE, "size": ["100%", "100%"], "keep_ratio": False, "layer": 1}  # P-15
ui["sgx_bar"] = {"type": "image", "texture": WHITE, "color": [0, 0, 0], "size": ["100%", "fill"], "keep_ratio": False}

# Ordem de desenho (layer): vermelho < impacto < letterbox < flash.
lb = []
for c in range(1, 100):
    v = 0.0 if c == 99 else (99 - c) / 98 * 56.25
    lb.append({f"sgx_lb_{c:02d}": gated(f";LB={c:02d};", {
        "type": "stack_panel", "orientation": "vertical", "size": ["100%", "100%"],
        "controls": [{"top@hud.sgx_bar": {}}, {"mid": {"type": "panel", "size": ["100%", f"{v:.3f}%x"]}}, {"bot@hud.sgx_bar": {}}]})})
fl = []
for ci, col in enumerate(FLASH_COLORS):
    for a in range(1, 10):
        code = ci * 10 + a
        if code == 0:
            continue
        fl.append({f"sgx_fl_{code:02d}@hud.sgx_full_image": gated(f";FL={code:02d};", {"color": rgb(col), "alpha": round(a / 9, 4)})})
rs = []
c0, c1 = rgb("#FF7A3D"), rgb("#2A0000")
for k in range(1, 21):
    r = k / 20
    col = [round(c0[i] + (c1[i] - c0[i]) * r, 4) for i in range(3)]
    rs.append({f"sgx_rs_{k:02d}@hud.sgx_full_image": gated(f";RS={k:02d};", {"color": col, "alpha": round(0.15 + 0.6 * r, 4)})})
imp = [{"sgx_in_01@hud.sgx_full_image": gated(";IN=01;", {"texture": "textures/sgx/ui/impact_negative"})}]


def group(name, token, controls, layer):
    return {name: gated(token, {"type": "panel", "size": ["100%", "100%"], "layer": layer, "controls": controls})}


ui["sgx_root"] = {
    "type": "panel", "size": ["100%", "100%"], "layer": 60,
    "controls": [group("sgx_rs", ";RS=", rs, 1), group("sgx_in", ";IN=", imp, 2), group("sgx_lb", ";LB=", lb, 3), group("sgx_fl", ";FL=", fl, 4)],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ui, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"✓ {OUT.relative_to(ROOT)}: LB {len(lb)} · FL {len(fl)} · RS {len(rs)} · IN {len(imp)} controles")
