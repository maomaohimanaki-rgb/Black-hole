#!/usr/bin/env python3
"""Monta BP/ e RP/ (tudo, MENOS BP/scripts/) a partir de templates/ + os assets da F0/F1:
partículas de teste e de gizmo, entidades dos spikes, texturas de teste com números grandes, ícones
provisórios e os textos EN/PT (menu, spikes, HUD do storyboard).
Idempotente: apaga e recria. Os sons saem de tools/synth/placeholder.py e a UI de tools/gen_ui.py (rode
tools/build_all.py, que chama tudo na ordem).
v0.1.0: texturas de teste são PROVISÓRIAS (F0/F1). As finais saem do motor de imagem na F3."""
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
SB = json.loads((ROOT / "spec/storyboard.json").read_text(encoding="utf-8"))
LY = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
TPL = ROOT / "templates"
BP, RP = ROOT / "BP", ROOT / "RP"
NS = P["namespace"]
FV = P["bedrock"]["format_versions"]
FONT = ROOT / "assets/fonts/IBMPlexSans-SemiBold.ttf"
MONO = ROOT / "assets/fonts/IBMPlexMono-SemiBold-full.ttf"

# ------------------------------------------------------------------ limpa e copia o esqueleto
for child in list(BP.iterdir()) if BP.exists() else []:
    if child.name == "scripts":
        continue
    shutil.rmtree(child) if child.is_dir() else child.unlink()
if RP.exists():
    shutil.rmtree(RP)
for src in TPL.rglob("*"):
    rel = src.relative_to(TPL)
    if src.is_dir() or rel.parts[0] not in ("BP", "RP") or rel.parts[:2] == ("BP", "scripts"):
        continue
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def font(size, mono=False):
    return ImageFont.truetype(str(MONO if mono else FONT), size)


def save_png(img, rel):
    p = RP / "textures" / f"{rel}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def label(draw, box, text, size, fill=(255, 255, 255, 255), mono=False, stroke=(0, 0, 0, 255)):
    x0, y0, x1, y1 = box
    f = font(size, mono)
    w = draw.textlength(text, font=f)
    draw.text(((x0 + x1 - w) / 2, (y0 + y1) / 2 - size * 0.62), text, font=f, fill=fill,
              stroke_width=max(1, size // 14), stroke_fill=stroke)


# ------------------------------------------------------------------ texturas de teste (números grandes, para ler no print)
RING_COLORS = [(220, 228, 255), (255, 244, 234), (255, 180, 107), (255, 138, 61), (255, 106, 30)]  # 9000 K → 2000 K


def disk_atlas(lit):
    img = Image.new("RGBA", (2048, 512), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for k in range(5):
        y0 = k * 64
        base = RING_COLORS[k] if lit else tuple(int(c * 0.28) for c in RING_COLORS[k])
        for j in range(32):
            x0 = j * 64
            shade = 0.82 + 0.18 * ((j % 2) == 0)
            col = tuple(int(c * shade) for c in base) + (255,)
            d.rectangle([x0, y0, x0 + 63, y0 + 63], fill=col)
            if j % 4 == 0:
                label(d, (x0, y0, x0 + 64, y0 + 64), str(k + 1), 44, fill=(0, 0, 0, 255), stroke=(255, 255, 255, 255))
    return img


save_png(disk_atlas(False), "sgx/disk/disk_cold")
save_png(disk_atlas(True), "sgx/disk/disk_lit")

# detritos: 16 tipos, cada um com o número em todas as faces (UV de caixa 64×32 → imagem 256×128)
KIND_COLORS = ["#5E9B3A", "#7A5A3A", "#808080", "#DBCB8E", "#6B5133", "#3F7F2A", "#F2F6F8", "#8C8484",
               "#A0A6B4", "#B5653F", "#3D3D46", "#A47D4C", "#9CC2FF", "#3B6BD8", "#FF7A1E", "#B04CFF"]
for i, c in enumerate(KIND_COLORS):
    img = Image.new("RGBA", (256, 128), c)
    d = ImageDraw.Draw(img)
    for fx, fy in [(64, 0), (128, 0), (0, 64), (64, 64), (128, 64), (192, 64)]:
        d.rectangle([fx, fy, fx + 63, fy + 63], outline=(0, 0, 0, 255), width=3)
        label(d, (fx, fy, fx + 64, fy + 64), f"{i:02d}", 34)
    save_png(img, f"sgx/debris/k{i:02d}")

# impostor de teste: 8 quadros 512² num atlas 2048×1024, sombra + anel + número do quadro
imp = Image.new("RGBA", (2048, 1024), (0, 0, 0, 0))
d = ImageDraw.Draw(imp)
for fr in range(8):
    x0, y0 = (fr % 4) * 512, (fr // 4) * 512
    cx, cy = x0 + 256, y0 + 256
    ang = fr * 45
    d.ellipse([cx - 230, cy - 60, cx + 230, cy + 60], outline=(255, 180, 107, 255), width=26)  # disco de lado
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=(0, 0, 0, 255), outline=(255, 231, 176, 255), width=8)
    a = math.radians(ang)
    d.line([cx, cy, cx + 100 * math.cos(a), cy + 100 * math.sin(a)], fill=(255, 255, 255, 255), width=10)
    label(d, (x0, y0 + 360, x0 + 512, y0 + 500), f"F{fr}", 96)
save_png(imp, "sgx/impostor/inc_00")

# S-06: atlas 2048×2048 com 4 linhas (inclinação 0–3) × 4 colunas (quadro 0–3)
at = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
d = ImageDraw.Draw(at)
ROW = [(255, 80, 80, 255), (80, 220, 80, 255), (80, 140, 255, 255), (255, 220, 60, 255)]
for row in range(4):
    for col in range(4):
        x0, y0 = col * 512, row * 512
        d.rounded_rectangle([x0 + 16, y0 + 16, x0 + 495, y0 + 495], radius=48, fill=(10, 10, 14, 230), outline=ROW[row], width=18)
        label(d, (x0, y0 + 40, x0 + 512, y0 + 260), f"I{row}", 170, fill=ROW[row])
        label(d, (x0, y0 + 260, x0 + 512, y0 + 470), f"F{col}", 150)
save_png(at, "sgx/spike/atlas")


def radial(size, fn):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - c, y - c) / c
            px[x, y] = fn(r)
    return img


save_png(radial(128, lambda r: (0, 0, 0, 255) if r <= 0.96 else (0, 0, 0, int(255 * max(0, (1 - r) / 0.04)))), "sgx/fx/shadow_disc")
save_png(radial(64, lambda r: (255, 255, 255, int(255 * max(0.0, 1 - r) ** 0.7))), "sgx/fx/dot")
save_png(radial(256, lambda r: (216, 226, 240, int(255 * max(0.0, 1 - abs(r - 0.9) / 0.08)))), "sgx/fx/ripple")
jet = Image.new("RGBA", (32, 256), (0, 0, 0, 0))
px = jet.load()
for y in range(256):
    for x in range(32):
        cx = abs(x - 15.5) / 15.5
        px[x, y] = (240, 238, 255, int(255 * max(0.0, 1 - cx) ** 1.5))
save_png(jet, "sgx/fx/jet_core")

# S-02: placa com seta e o nome do query testado
for name, text in (("bb_cam", "camera_rotation"), ("bb_rot", "rotation_to_camera")):
    img = Image.new("RGBA", (256, 256), (25, 25, 35, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 255, 255], outline=(255, 220, 60, 255), width=10)
    d.polygon([(128, 30), (200, 120), (150, 120), (150, 170), (106, 170), (106, 120), (56, 120)], fill=(255, 220, 60, 255))
    label(d, (0, 180, 256, 240), text, 22)
    save_png(img, f"sgx/spike/{name}")

# S-07: disco poly_mesh (textura normalizada)
pm = Image.new("RGBA", (256, 256), (255, 106, 30, 255))
d = ImageDraw.Draw(pm)
for i in range(8):
    d.rectangle([i * 32, 0, i * 32 + 15, 255], fill=(255, 180, 107, 255))
label(d, (0, 64, 256, 192), "MESH", 70, fill=(0, 0, 0, 255), stroke=(255, 255, 255, 255))
save_png(pm, "sgx/spike/polymesh")

# UI: branco para overlays coloridos, impacto negativo provisório, ícones
save_png(Image.new("RGBA", (16, 16), (255, 255, 255, 255)), "sgx/ui/white")
neg = Image.new("RGBA", (1024, 576), (0, 0, 0, 255))
d = ImageDraw.Draw(neg)
d.ellipse([512 - 70, 288 - 70, 512 + 70, 288 + 70], fill=(255, 255, 255, 255))
for k in range(24):
    a = math.radians(k * 15)
    d.line([512 + 120 * math.cos(a), 288 + 120 * math.sin(a), 512 + 520 * math.cos(a), 288 + 520 * math.sin(a)], fill=(255, 255, 255, 90), width=3)
save_png(neg, "sgx/ui/impact_negative")


def icon(size):
    img = Image.new("RGBA", (size, size), (5, 7, 15, 255))
    d = ImageDraw.Draw(img)
    c = size / 2
    d.ellipse([c - size * 0.45, c - size * 0.13, c + size * 0.45, c + size * 0.13], outline=(255, 140, 50, 255), width=max(2, size // 14))
    d.ellipse([c - size * 0.2, c - size * 0.2, c + size * 0.2, c + size * 0.2], fill=(0, 0, 0, 255), outline=(255, 231, 176, 255), width=max(1, size // 40))
    return img


item = icon(32)
p = RP / "textures/items/singularity_core.png"
p.parent.mkdir(parents=True, exist_ok=True)
item.save(p)
for pack in (BP, RP):
    icon(256).save(pack / "pack_icon.png")

# ------------------------------------------------------------------ partículas da F0/F1


def particle(ident, material, texture, billboard, extra=None):
    comps = {
        "minecraft:emitter_rate_instant": {"num_particles": 1},
        "minecraft:emitter_lifetime_once": {"active_time": 0.05},
        "minecraft:emitter_shape_point": {},
        "minecraft:particle_lifetime_expression": {"max_lifetime": "v.lf.x"},
        "minecraft:particle_initial_speed": 0.0,
        "minecraft:particle_motion_dynamic": {},
        "minecraft:particle_appearance_billboard": billboard,
        "minecraft:particle_appearance_tinting": {"color": ["v.c0.x", "v.c0.y", "v.c0.z",
            "math.clamp(v.a.x, 0, 1) * math.clamp(math.min(v.particle_age / math.max(v.lf.y, 0.01), (v.particle_lifetime - v.particle_age) / math.max(v.lf.z, 0.01)), 0, 1)"]},
    }
    comps.update(extra or {})
    return {"format_version": FV["particles"], "particle_effect": {
        "description": {"identifier": ident, "basic_render_parameters": {"material": material, "texture": texture}},
        "components": comps}}


FULL = {"texture_width": 1, "texture_height": 1, "uv": [0, 0], "uv_size": [1, 1]}
dump(RP / "particles/sgx_gizmo.json", particle(f"{NS}:sgx_gizmo", "particles_blend", "textures/sgx/fx/dot",
     {"size": ["v.s.x", "v.s.x"], "facing_camera_mode": "lookat_xyz", "uv": FULL}))
dump(RP / "particles/sgx_gizmo_add.json", particle(f"{NS}:sgx_gizmo_add", "particles_add", "textures/sgx/fx/dot",
     {"size": ["v.s.x", "v.s.x"], "facing_camera_mode": "lookat_xyz", "uv": FULL}))
# S-06: o quadro de tempo vem da idade; a linha do atlas vem da variável v.incl (enviada no spawn).
dump(RP / "particles/sgx_spike_atlas.json", particle(f"{NS}:sgx_spike_atlas", "particles_blend", "textures/sgx/spike/atlas",
     {"size": ["v.s.x", "v.s.x"], "facing_camera_mode": "lookat_xyz",
      "uv": {"texture_width": 2048, "texture_height": 2048,
             "uv": ["math.mod(math.floor(v.particle_age * 2), 4) * 512", "math.floor(v.incl.x) * 512"], "uv_size": [512, 512]}}))

# ------------------------------------------------------------------ entidades dos spikes
INERT = load(BP / "entities/sgx_disk.json")["minecraft:entity"]["components"]


def fx_entity(ident, props=None, extra=None):
    comps = dict(INERT)
    comps.update(extra or {})
    desc = {"identifier": ident, "is_spawnable": False, "is_summonable": True, "is_experimental": False}
    if props:
        desc["properties"] = props
    return {"format_version": FV["entity_bp"], "minecraft:entity": {"description": desc, "components": comps}}


def client_entity(ident, tex, geo, scripts=None, anim=None, material="entity_alphatest"):
    desc = {"identifier": ident, "materials": {"default": material}, "textures": {"default": tex},
            "geometry": {"default": geo}, "render_controllers": [f"controller.render.{NS}.sgx_simple"]}
    if scripts:
        desc["scripts"] = scripts
    if anim:
        desc["animations"] = anim
    return {"format_version": FV["client_entity"], "minecraft:client_entity": {"description": desc}}


dump(RP / "render_controllers/sgx_simple.render_controllers.json", {"format_version": FV["render_controllers"], "render_controllers": {
    f"controller.render.{NS}.sgx_simple": {"geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
                                           "textures": ["Texture.default"], "ignore_lighting": True}}})

# S-02: duas placas. A de cima usa q.camera_rotation, a de baixo q.rotation_to_camera.
for name, q in (("bb_cam", "q.camera_rotation"), ("bb_rot", "q.rotation_to_camera")):
    ident = f"{NS}:sgx_spike_{name}"
    dump(BP / f"entities/sgx_spike_{name}.json", fx_entity(ident))
    dump(RP / f"models/entity/sgx_spike_{name}.geo.json", {"format_version": FV["geometry"], "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{NS}.sgx_spike_{name}", "texture_width": 16, "texture_height": 16,
                        "visible_bounds_width": 6, "visible_bounds_height": 6, "visible_bounds_offset": [0, 1.5, 0]},
        "bones": [{"name": "root", "pivot": [0, 24, 0]},
                  {"name": "panel", "parent": "root", "pivot": [0, 24, 0],
                   "cubes": [{"origin": [-16, 8, -0.8], "size": [32, 32, 1.6],
                              "uv": {f: {"uv": [0, 0], "uv_size": [16, 16]} for f in ("north", "south", "east", "west", "up", "down")}}]}]}]})
    if q == "q.camera_rotation":
        rot = ["-q.camera_rotation(0)", "-q.camera_rotation(1) + 180", 0]
    else:
        rot = ["q.rotation_to_camera(0)", "q.rotation_to_camera(1) - q.body_y_rotation", 0]
    dump(RP / f"animations/sgx_spike_{name}.animation.json", {"format_version": FV["animations"], "animations": {
        f"animation.{NS}.sgx_spike_{name}.face": {"loop": True, "bones": {"panel": {"rotation": rot}}}}})
    dump(RP / f"entity/sgx_spike_{name}.entity.json", client_entity(ident, f"textures/sgx/spike/{name}", f"geometry.{NS}.sgx_spike_{name}",
         scripts={"animate": ["face"]}, anim={"face": f"animation.{NS}.sgx_spike_{name}.face"}))

# S-07: disco liso em poly_mesh (anel de 32 segmentos, as duas faces)
SEG, R0, R1 = 32, 3 * 16, 8 * 16
pos, uvs, polys = [], [], []
for j in range(SEG + 1):
    a = 2 * math.pi * j / SEG
    for r in (R0, R1):
        pos.append([round(r * math.cos(a), 4), 0.0, round(r * math.sin(a), 4)])
        uvs.append([j / SEG, 0.0 if r == R0 else 1.0])
for j in range(SEG):
    i0, i1, i2, i3 = 2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2
    polys.append([[i0, 0, i0], [i1, 0, i1], [i2, 0, i2], [i3, 0, i3]])
    polys.append([[i3, 1, i3], [i2, 1, i2], [i1, 1, i1], [i0, 1, i0]])
ident = f"{NS}:sgx_spike_mesh"
dump(BP / "entities/sgx_spike_mesh.json", fx_entity(ident))
dump(RP / "models/entity/sgx_spike_mesh.geo.json", {"format_version": FV["geometry"], "minecraft:geometry": [{
    "description": {"identifier": f"geometry.{NS}.sgx_spike_mesh", "texture_width": 16, "texture_height": 16,
                    "visible_bounds_width": 20, "visible_bounds_height": 4, "visible_bounds_offset": [0, 0, 0]},
    "bones": [{"name": "root", "pivot": [0, 0, 0],
               "poly_mesh": {"normalized_uvs": True, "positions": pos, "normals": [[0, 1, 0], [0, -1, 0]], "uvs": uvs, "polys": polys}}]}]})
dump(RP / "animations/sgx_spike_mesh.animation.json", {"format_version": FV["animations"], "animations": {
    f"animation.{NS}.sgx_spike_mesh.spin": {"loop": True, "bones": {"root": {"rotation": [0, "q.life_time * 40", 0]}}}}})
dump(RP / "entity/sgx_spike_mesh.entity.json", client_entity(ident, "textures/sgx/spike/polymesh", f"geometry.{NS}.sgx_spike_mesh",
     scripts={"animate": ["spin"]}, anim={"spin": f"animation.{NS}.sgx_spike_mesh.spin"}))

# ------------------------------------------------------------------ textos (EN/PT): templates + spikes + menu + HUD do storyboard
EXTRA = {
    "en_US": {
        "sgx.menu.soon": "§8Coming in a later version.",
        "sgx.menu.options.body": "§7Options arrive with the full film. For now: /scriptevent sgx:spike 1…10, sgx:play blackhole, sgx:stop.",
        "sgx.msg.no_target": "§cAim at the ground (40–128 blocks away).",
        "sgx.msg.too_far": "§cToo far. Aim at the ground at most %1 blocks away.",
        "sgx.msg.stopped": "§8[Dooms Day] Stopped.",
        "sgx.msg.restored": "§8[Dooms Day] Restored the world settings after an interrupted cinematic.",
        "sgx.msg.film_done": "§8[Dooms Day] Animatic finished (%1 ticks, %2 skipped, script %3 ms avg / %4 ms peak).",
        "sgx.spike.unknown": "§cUnknown test. Use /scriptevent sgx:spike 1…10",
        "sgx.spike.end": "§8[S-%1] Test finished. Camera back to normal.",
        "sgx.spike.1": "§e[S-01] Depth: §f3D disk (numbered rings) + black particle in the center. Camera orbits for 12 s. §7Look: is the black disk IN FRONT of the back part of the rings and BEHIND the front part?",
        "sgx.spike.2": "§e[S-02] Billboards: §ftop = q.camera_rotation, bottom = q.rotation_to_camera. Cutscene camera orbits. §7Look: does each panel turn WITH the camera (even if facing the wrong side)?",
        "sgx.spike.3": "§e[S-03] Thin cubes: §fonly the outer disk ring (0.1-unit thick cubes, entity_emissive). §7Look: is the ring visible, solid and bright (tablet AND phone)?",
        "sgx.spike.4": "§e[S-04] Debris: §f20 numbered blocks spiral in and stretch (bones moved up to 30 blocks by Molang). §7Look: do any blocks vanish when you turn away from the center? Do they stretch toward the center?",
        "sgx.spike.5": "§e[S-05] Stereo: §fa 2D sound pans LEFT → RIGHT in 4 s (twice). §7Listen on the phone speaker AND headphones: does it move from left to right?",
        "sgx.spike.6": "§e[S-06] Atlas: §f4 particles with v.incl 0…3 (rows I0–I3) animating frames F0→F3, plus 1 impostor (F0…F7). §7Look: each one shows its own row and the frame numbers change?",
        "sgx.spike.7": "§e[S-07] poly_mesh: §fa smooth orange ring (\"MESH\") spinning. §7Look: does it appear at all, on tablet AND phone?",
        "sgx.spike.8": "§e[S-08] Letterbox: §fbars sweep 16:9 → 2.39 → 3.2 → closed → open, then flashes (white, ice, warm, violet, black). §7Look: are the bars clean on 20:9? Does anything stick out at the edges?",
        "sgx.spike.9": "§e[S-09] FOV breathing: §ffixed camera, FOV ±5° every 3 ticks (6 s), then every 6 ticks (6 s). §7Look: smooth or jerky?",
        "sgx.spike.10": "§e[S-10] Pull: §f10 cows are pulled to the gold marker every 4 ticks for 8 s. §7Look: smooth, or do they \"teleport\"?",
        "sgx.spike.10.after": "§8[S-10] Cows removed.",
        "sgx.spike.busy": "§8A test or cinematic is already running. /scriptevent sgx:stop",
    },
    "pt_BR": {
        "sgx.menu.soon": "§8Chega numa versão futura.",
        "sgx.menu.options.body": "§7As opções chegam com o filme completo. Por enquanto: /scriptevent sgx:spike 1…10, sgx:play blackhole, sgx:stop.",
        "sgx.msg.no_target": "§cMire no chão (a 40–128 blocos).",
        "sgx.msg.too_far": "§cLonge demais. Mire no chão a no máximo %1 blocos.",
        "sgx.msg.stopped": "§8[Dooms Day] Parado.",
        "sgx.msg.restored": "§8[Dooms Day] Restaurei as configurações do mundo depois de uma cinemática interrompida.",
        "sgx.msg.film_done": "§8[Dooms Day] Animatic terminou (%1 ticks, %2 pulados, script %3 ms média / %4 ms pico).",
        "sgx.spike.unknown": "§cTeste desconhecido. Use /scriptevent sgx:spike 1…10",
        "sgx.spike.end": "§8[S-%1] Teste terminou. Câmera de volta ao normal.",
        "sgx.spike.1": "§e[S-01] Profundidade: §fdisco 3D (anéis numerados) + partícula preta no centro. A câmera orbita por 12 s. §7Olhe: o disco preto fica NA FRENTE da parte de trás dos anéis e ATRÁS da parte da frente?",
        "sgx.spike.2": "§e[S-02] Billboards: §fem cima = q.camera_rotation, embaixo = q.rotation_to_camera. A câmera da cutscene orbita. §7Olhe: cada placa gira JUNTO com a câmera (mesmo que virada do lado errado)?",
        "sgx.spike.3": "§e[S-03] Cubos finos: §fsó o anel de fora do disco (cubos de 0,1 unidade, entity_emissive). §7Olhe: o anel aparece inteiro e aceso (no tablet E no celular)?",
        "sgx.spike.4": "§e[S-04] Detritos: §f20 blocos numerados caem em espiral e esticam (ossos deslocados até 30 blocos pelo Molang). §7Olhe: algum some quando você vira para longe do centro? Eles esticam apontando para o centro?",
        "sgx.spike.5": "§e[S-05] Estéreo: §fum som 2D vai da ESQUERDA → DIREITA em 4 s (duas vezes). §7Escute no alto-falante do celular E no fone: ele anda da esquerda para a direita?",
        "sgx.spike.6": "§e[S-06] Atlas: §f4 partículas com v.incl 0…3 (linhas I0–I3) animando os quadros F0→F3, mais 1 impostor (F0…F7). §7Olhe: cada uma mostra a própria linha e os números dos quadros mudam?",
        "sgx.spike.7": "§e[S-07] poly_mesh: §fum anel laranja liso (\"MESH\") girando. §7Olhe: ele aparece, no tablet E no celular?",
        "sgx.spike.8": "§e[S-08] Letterbox: §fas barras varrem 16:9 → 2,39 → 3,2 → fechado → abre, depois os flashes (branco, gelo, quente, violeta, preto). §7Olhe: as barras ficam limpas no 20:9? Algo vaza nas bordas?",
        "sgx.spike.9": "§e[S-09] FOV respirando: §fcâmera parada, FOV ±5° a cada 3 ticks (6 s), depois a cada 6 ticks (6 s). §7Olhe: liso ou aos trancos?",
        "sgx.spike.10": "§e[S-10] Puxão: §f10 vacas são puxadas para o marcador dourado a cada 4 ticks por 8 s. §7Olhe: liso, ou elas \"teleportam\"?",
        "sgx.spike.10.after": "§8[S-10] Vacas removidas.",
        "sgx.spike.busy": "§8Já tem um teste ou cinemática rodando. /scriptevent sgx:stop",
    },
}
# Legendas (SB) traduzidas; o HUD técnico (HD) fica igual nos dois idiomas, como num painel de instrumentos.
SB_PT = {"ANOMALY DETECTED": "ANOMALIA DETECTADA", "BINARY LOCKED": "SISTEMA BINÁRIO", "THEY BECAME ONE": "VIRARAM UM SÓ",
         "ACCRETION": "ACREÇÃO", "RELATIVISTIC JETS": "JATOS RELATIVÍSTICOS", "TIDAL FORCES": "FORÇAS DE MARÉ",
         "SIGNAL LOST": "SINAL PERDIDO", "SINGULARITY · A": "SINGULARIDADE · A"}
hud = {"en_US": {}, "pt_BR": {}}
for b in SB["blocks"]:
    for i, h in enumerate(b.get("hud", [])):
        if h["ch"] in ("SB", "HD", "TT", "TT2"):
            key = f"sgx.hud.{b['id'].lower()}.{i}"
            hud["en_US"][key] = h["text"]
            hud["pt_BR"][key] = SB_PT.get(h["text"], h["text"])
for lang in P["languages"]:
    p = RP / f"texts/{lang}.lang"
    lines = p.read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines.append("## F0/F1")
    lines += [f"{k}={v}" for k, v in EXTRA[lang].items()]
    lines.append("## GERADO do spec/storyboard.json (HUD)")
    lines += [f"{k}={v}" for k, v in hud[lang].items()]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

n = sum(1 for d in (BP, RP) for f in d.rglob("*") if f.is_file() and "scripts" not in f.parts)
print(f"✓ BP/ e RP/ montados: {n} arquivos (sem scripts)")
