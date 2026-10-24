#!/usr/bin/env python3
"""Gera templates/BP e templates/RP: o esqueleto do addon com os ids de spec/project.json.
São MODELOS para a Fase 0/1 (formatos que já funcionaram em aparelho real, out/2026), não arquivos testados no jogo.
Rode: python3 tools/gen_templates.py   (idempotente; apaga e recria templates/)"""
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
LY = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
AU = json.loads((ROOT / "spec/audio_cues.json").read_text(encoding="utf-8"))
OUT = ROOT / "templates"
NS = P["namespace"]
FV = P["bedrock"]["format_versions"]
U = P["uuids"]

if OUT.exists():
    shutil.rmtree(OUT)

def dump(rel, obj):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, str):
        p.write_text(obj, encoding="utf-8")
    else:
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def prop_float(lo, hi, default):     # PITFALLS P-29: faixa float SEMPRE com literais float
    return {"type": "float", "range": [float(lo), float(hi)], "default": float(default), "client_sync": True}

def prop_int(lo, hi, default):
    return {"type": "int", "range": [int(lo), int(hi)], "default": int(default), "client_sync": True}

INERT = {  # componentes de "entidade de efeito" (colisão zero, sem física, imune a dano)
    "minecraft:collision_box": {"width": 0.001, "height": 0.001},
    "minecraft:physics": {"has_collision": False, "has_gravity": False},
    "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
    "minecraft:movement": {"value": 0.0},
    "minecraft:health": {"value": 1, "max": 1},
    "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": False}]},
    "minecraft:fire_immune": True,
    "minecraft:knockback_resistance": {"value": 1.0},
    "minecraft:body_rotation_blocked": {},
}

# ------------------------------------------------------------------ manifests
v = [0, 0, 1]
dump("BP/manifest.json", {
    "format_version": 2,
    "header": {"name": "pack.name", "description": "pack.description", "uuid": U["bp_header"], "version": v,
               "min_engine_version": P["bedrock"]["min_engine_version"]},
    "modules": [{"type": "data", "uuid": U["bp_data_module"], "version": v},
                {"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": U["bp_script_module"], "version": v}],
    "dependencies": [{"module_name": k, "version": ver} for k, ver in P["bedrock"]["script_modules"].items()] +
                    [{"uuid": U["rp_header"], "version": v}],
})
dump("RP/manifest.json", {
    "format_version": 2,
    "header": {"name": "pack.name", "description": "pack.description", "uuid": U["rp_header"], "version": v,
               "min_engine_version": P["bedrock"]["min_engine_version"]},
    "modules": [{"type": "resources", "uuid": U["rp_resources_module"], "version": v}],
})

# ------------------------------------------------------------------ textos (i18n desde o dia 1, P-50)
LANG = {
    "en_US": {
        "bp": ("Dooms Day (BP)", "Two cinematic events about the strangest objects in the universe: a black hole (binary merger, accretion disk, jets, the fall) and a magnetar (SGR 1806-20). Real destruction. Use the Singularity Core."),
        "rp": ("Dooms Day (RP)", "Dooms Day resources: black hole impostors (Schwarzschild ray tracer), accretion disk, jets, magnetar field lines, synthesized audio, NASA starfield."),
        "item": "§5Singularity Core",
        "keys": {"sgx.menu.title": "§l§4DOOMS DAY§r", "sgx.menu.subtitle": "§8SINGULARITY CORE", "sgx.menu.body": "§7Aim at the ground 40–128 blocks away.",
                 "sgx.menu.play": "§5BLACK HOLE", "sgx.menu.play.sub": "§7Binary, merger, disk, jets, the fall", "sgx.menu.magnetar": "§bMAGNETAR", "sgx.menu.magnetar.sub": "§7SGR 1806-20 · the flare of 2004", "sgx.menu.options": "§5OPTIONS",
                 "sgx.menu.options.sub": "§7Destruction, damage, protections, quality, camera", "sgx.menu.cancel": "§8Cancel",
                 "sgx.msg.too_close": "§cToo close. Aim at the ground at least %1 blocks away.", "sgx.msg.busy": "§8Another cinematic is already playing.",
                 "sgx.msg.loaded": "§8[Dooms Day] §7Loaded. /give @s singularity:core"}},
    "pt_BR": {
        "bp": ("Dooms Day (BP)", "Dois eventos cinematográficos sobre os objetos mais estranhos do universo: um buraco negro (fusão, disco, jatos, a queda) e um magnetar (SGR 1806-20). Destruição real. Use o Núcleo da Singularidade."),
        "rp": ("Dooms Day (RP)", "Recursos do Dooms Day: impostores do buraco negro (traçado de raios de Schwarzschild), disco de acreção, jatos, linhas de campo do magnetar, áudio sintetizado, céu da NASA."),
        "item": "§5Núcleo da Singularidade",
        "keys": {"sgx.menu.title": "§l§4DOOMS DAY§r", "sgx.menu.subtitle": "§8NÚCLEO DA SINGULARIDADE", "sgx.menu.body": "§7Mire no chão a 40–128 blocos.",
                 "sgx.menu.play": "§5BURACO NEGRO", "sgx.menu.play.sub": "§7Par, fusão, disco, jatos, a queda", "sgx.menu.magnetar": "§bMAGNETAR", "sgx.menu.magnetar.sub": "§7SGR 1806-20 · a erupção de 2004", "sgx.menu.options": "§5OPÇÕES",
                 "sgx.menu.options.sub": "§7Destruição, dano, proteções, qualidade, câmera", "sgx.menu.cancel": "§8Cancelar",
                 "sgx.msg.too_close": "§cPerto demais. Mire no chão a pelo menos %1 blocos.", "sgx.msg.busy": "§8Já tem uma cinemática tocando.",
                 "sgx.msg.loaded": "§8[Dooms Day] §7Carregado. /give @s singularity:core"}},
}
for pack in ("BP", "RP"):
    dump(f"{pack}/texts/languages.json", list(LANG))
    for lang, L in LANG.items():
        name, desc = L["bp" if pack == "BP" else "rp"]
        lines = [f"pack.name={name}", f"pack.description={desc}"]
        if pack == "RP":
            lines.append(f"item.{P['item']['id']}={L['item']}")
            lines += [f"{k}={val}" for k, val in L["keys"].items()]
        dump(f"{pack}/texts/{lang}.lang", "\n".join(lines) + "\n")

# ------------------------------------------------------------------ item (sem display_name literal: o nome vem do .lang)
dump("BP/items/sgx_core.json", {
    "format_version": FV["item"],
    "minecraft:item": {
        "description": {"identifier": P["item"]["id"], "menu_category": {"category": "equipment"}},
        "components": {
            "minecraft:icon": {"textures": {"default": P["item"]["texture"]}},
            "minecraft:max_stack_size": 1, "minecraft:glint": True, "minecraft:hand_equipped": True,
            "minecraft:use_modifiers": {"use_duration": 0.1, "movement_modifier": 1.0},
            "minecraft:cooldown": {"category": "singularity_core", "duration": 0.4},
        }}})
dump("RP/textures/item_texture.json", {"resource_pack_name": "DoomsDay", "texture_name": "atlas.items",
      "texture_data": {P["item"]["texture"]: {"textures": f"textures/items/{P['item']['texture']}"}}})

# ------------------------------------------------------------------ disco de acreção (VISUAL_TECH §3)
rings = LY["disk"]["rings"]
SEG = 32
ATLAS_W, ROW_H = 2048, 64        # cada anel = uma faixa de 2048×64 no atlas do disco (5 faixas → 2048×320, arredonde p/ 512)
bones = [{"name": "root", "pivot": [0, 0, 0]}, {"name": "spin_root", "parent": "root", "pivot": [0, 0, 0]}]
for k, (r0, r1) in enumerate(rings, start=1):
    cubes = []
    r0u, r1u = r0 * 16, r1 * 16                       # P-31: 16 unidades = 1 bloco
    rm = (r0u + r1u) / 2
    chord = 2 * rm * math.tan(math.pi / SEG) * 1.04   # 4 % de sobreposição contra frestas
    for j in range(SEG):
        u = j * (ATLAS_W // SEG)
        face = {"uv": [u, (k - 1) * ROW_H], "uv_size": [ATLAS_W // SEG, ROW_H]}
        cubes.append({"origin": [r0u, -0.05, -chord / 2], "size": [r1u - r0u, 0.1, chord],   # P-30: espessura 0,1 (nunca zero)
                      "pivot": [0, 0, 0], "rotation": [0, round(-360 * j / SEG, 4), 0],
                      "uv": {"up": face, "down": face, "north": face, "south": face, "east": face, "west": face}})
    bones.append({"name": f"ring_{k}", "parent": "spin_root", "pivot": [0, 0, 0], "cubes": cubes})
outer = rings[-1][1]
dump("RP/models/entity/sgx_disk.geo.json", {"format_version": FV["geometry"], "minecraft:geometry": [{
    "description": {"identifier": f"geometry.{NS}.sgx_disk", "texture_width": ATLAS_W, "texture_height": 512,
                    "visible_bounds_width": math.ceil(outer * 2 + 4), "visible_bounds_height": 8, "visible_bounds_offset": [0, 0, 0]},
    "bones": bones}]})
dump("BP/entities/sgx_disk.json", {"format_version": FV["entity_bp"], "minecraft:entity": {
    "description": {"identifier": f"{NS}:sgx_disk", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
                    "properties": {f"{NS}:lit": prop_int(0, 5, 0), f"{NS}:heat": prop_float(0, 1, 0), f"{NS}:scale": prop_float(0.01, 4, 1)}},
    "components": {"minecraft:type_family": {"family": ["singularity_fx", "inanimate"]}, **INERT}}})
dump("RP/entity/sgx_disk.entity.json", {"format_version": FV["client_entity"], "minecraft:client_entity": {"description": {
    "identifier": f"{NS}:sgx_disk",
    "materials": {"default": "entity_emissive", "glow": "entity_beam_additive"},
    "textures": {"cold": "textures/sgx/disk/disk_cold", "lit": "textures/sgx/disk/disk_lit"},
    "geometry": {"default": f"geometry.{NS}.sgx_disk"},
    "animations": {"kepler": f"animation.{NS}.sgx_disk.kepler"},
    "scripts": {"pre_animation": ["v.ang = (v.ang ?? 0) + q.delta_time * 180;"], "animate": ["kepler"]},
    "render_controllers": [f"controller.render.{NS}.sgx_disk"]}}})
dump("RP/animations/sgx_disk.animation.json", {"format_version": FV["animations"], "animations": {f"animation.{NS}.sgx_disk.kepler": {
    "loop": True,
    "bones": {"root": {"scale": f"q.property('{NS}:scale')"},
              **{f"ring_{k}": {"rotation": [0, f"v.ang * {round(((r0 + r1) / 2 / rings[0][0]) ** -1.5, 4)}", 0]} for k, (r0, r1) in enumerate(rings, start=1)}}}}})
dump("RP/render_controllers/sgx_disk.render_controllers.json", {"format_version": FV["render_controllers"], "render_controllers": {
    f"controller.render.{NS}.sgx_disk": {
        "arrays": {"textures": {"Array.tex": ["Texture.cold", "Texture.lit"]}},
        "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
        "textures": [f"Array.tex[q.property('{NS}:lit') > 0]"], "ignore_lighting": True,
        "part_visibility": [{"*": True}] + [{f"ring_{k}": f"q.property('{NS}:lit') >= {6 - k}"} for k in range(1, 6)]}}})

# ------------------------------------------------------------------ detritos com espiral no Molang (VISUAL_TECH §5)
dump("BP/entities/sgx_debris.json", {"format_version": FV["entity_bp"], "minecraft:entity": {
    "description": {"identifier": f"{NS}:sgx_debris", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
                    "properties": {f"{NS}:r0": prop_float(0, 64, 10), f"{NS}:phi0": prop_float(-360, 360, 0), f"{NS}:y0": prop_float(-32, 32, -14),
                                   f"{NS}:tc": prop_float(0.5, 6, 2), f"{NS}:spin": prop_float(-720, 720, 0), f"{NS}:kind": prop_int(0, 15, 0)}},
    "components": {"minecraft:type_family": {"family": ["singularity_fx", "inanimate"]}, **INERT,
                   "minecraft:timer": {"looping": False, "time": 6.0, "time_down_event": {"event": f"{NS}:despawn"}}},
    "component_groups": {f"{NS}:gone": {"minecraft:instant_despawn": {}}},
    "events": {f"{NS}:despawn": {"add": {"component_groups": [f"{NS}:gone"]}}}}})
dump("RP/models/entity/sgx_debris.geo.json", {"format_version": FV["geometry"], "minecraft:geometry": [{
    "description": {"identifier": f"geometry.{NS}.sgx_debris", "texture_width": 64, "texture_height": 32,   # v0.1.0: UV de caixa de um cubo 16³ ocupa 64×32
                    "visible_bounds_width": 64, "visible_bounds_height": 64, "visible_bounds_offset": [0, 0, 0]},   # P-31
    "bones": [{"name": "root", "pivot": [0, 0, 0]},
              {"name": "body", "parent": "root", "pivot": [0, 8, 0],
               "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16], "uv": [0, 0]}]}]}]})
MOL = (f"v.u = math.clamp(q.life_time / q.property('{NS}:tc'), 0, 1);"
       f"v.r = q.property('{NS}:r0') * math.pow(1 - v.u, 0.6667);"
       f"v.ang = q.property('{NS}:phi0') + 900 * v.u * v.u;"
       f"v.y = q.property('{NS}:y0') * (1 - v.u) + {LY['O_height']} * (v.u * v.u * (3 - 2 * v.u));"
       f"v.st = 1 + 5 * math.pow(v.u, 3);")
dump("RP/entity/sgx_debris.entity.json", {"format_version": FV["client_entity"], "minecraft:client_entity": {"description": {
    "identifier": f"{NS}:sgx_debris", "materials": {"default": "entity_alphatest"},
    "textures": {f"k{i:02d}": f"textures/sgx/debris/k{i:02d}" for i in range(16)},
    "geometry": {"default": f"geometry.{NS}.sgx_debris"},
    "animations": {"spiral": f"animation.{NS}.sgx_debris.spiral"},
    "scripts": {"pre_animation": [MOL], "animate": ["spiral"]},
    "render_controllers": [f"controller.render.{NS}.sgx_debris"]}}})
dump("RP/animations/sgx_debris.animation.json", {"format_version": FV["animations"], "animations": {f"animation.{NS}.sgx_debris.spiral": {
    "loop": True, "bones": {"body": {
        "position": ["v.r * math.cos(v.ang) * 16", "v.y * 16", "v.r * math.sin(v.ang) * 16"],
        "scale": ["1 / math.sqrt(v.st)", "v.st", "1 / math.sqrt(v.st)"],
        "rotation": [0, "-v.ang", f"q.property('{NS}:spin') * v.u"]}}}}})
dump("RP/render_controllers/sgx_debris.render_controllers.json", {"format_version": FV["render_controllers"], "render_controllers": {
    f"controller.render.{NS}.sgx_debris": {
        "arrays": {"textures": {"Array.kind": [f"Texture.k{i:02d}" for i in range(16)]}},
        "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
        "textures": [f"Array.kind[q.property('{NS}:kind')]"]}}})

# ------------------------------------------------------------------ partículas modelo
def particle(ident, material, texture, billboard, extra_vars_note):
    return {"format_version": FV["particles"], "particle_effect": {
        "description": {"identifier": ident, "basic_render_parameters": {"material": material, "texture": texture}},
        "components": {
            "minecraft:emitter_rate_instant": {"num_particles": 1},
            "minecraft:emitter_lifetime_once": {"active_time": 0.05},
            "minecraft:emitter_shape_point": {},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "v.lf.x"},
            "minecraft:particle_initial_speed": 0.0,
            "minecraft:particle_motion_dynamic": {},
            "minecraft:particle_appearance_billboard": billboard,
            "minecraft:particle_appearance_tinting": {"color": ["v.c0.x", "v.c0.y", "v.c0.z",
                "math.clamp(v.a.x, 0, 1) * math.clamp(math.min(v.particle_age / v.lf.y, (v.particle_lifetime - v.particle_age) / v.lf.z), 0, 1)"]}}}}
FR = "math.mod(math.floor(v.particle_age * 10), 8)"
dump(f"RP/particles/sgx_p_impostor.json", particle(f"{NS}:sgx_p_impostor", "particles_blend", "textures/sgx/impostor/inc_00",
    {"size": ["v.s.x", "v.s.x"], "facing_camera_mode": "lookat_xyz",
     "uv": {"texture_width": 2048, "texture_height": 1024, "uv": [f"math.mod({FR}, 4) * 512", f"math.floor({FR} / 4) * 512"], "uv_size": [512, 512]}},
    "Impostor (sombra + anel + disco dobrado). Uma partícula por inclinação (sgx_p_impostor_00…08) se a textura não puder variar (S-06). Variáveis Vector3: v.lf (vida, entrada, saída), v.s (tamanho), v.a (alfa), v.c0 (cor)."))
dump(f"RP/particles/sgx_p_ripple.json", particle(f"{NS}:sgx_p_ripple", "particles_add", "textures/sgx/fx/ripple",
    {"size": ["v.s.x + (v.s.y - v.s.x) * (v.particle_age / v.particle_lifetime)", "v.s.x + (v.s.y - v.s.x) * (v.particle_age / v.particle_lifetime)"],
     "facing_camera_mode": "direction_z", "direction": {"mode": "custom", "custom_direction": [0, 1, 0.02]},     # P-19 e P-21
     "uv": {"texture_width": 1, "texture_height": 1, "uv": [0, 0], "uv_size": [1, 1]}},
    "Ondulação no chão: cresce de v.s.x a v.s.y blocos (meia-largura, P-23) na vida toda."))
dump(f"RP/particles/sgx_p_jet_core.json", particle(f"{NS}:sgx_p_jet_core", "particles_add", "textures/sgx/fx/jet_core",
    {"size": ["v.s.x", "v.s.y"], "facing_camera_mode": "lookat_y",            # P-21: pilar vertical = lookat_y
     "uv": {"texture_width": 1, "texture_height": 1, "uv": [0, 0], "uv_size": [1, 1]}},
    "Núcleo do jato. O centro da partícula fica no MEIO do jato (O + U·comprimento/2)."))
dump(f"RP/particles/sgx_spike_shadow.json", particle(f"{NS}:sgx_spike_shadow", "particles_blend", "textures/sgx/fx/shadow_disc",
    {"size": ["v.s.x", "v.s.x"], "facing_camera_mode": "lookat_xyz", "uv": {"texture_width": 1, "texture_height": 1, "uv": [0, 0], "uv_size": [1, 1]}},
    "Teste S-01: disco preto opaco virado para a câmera, no centro do disco 3D."))

# ------------------------------------------------------------------ sons (2D na cutscene, posicional para quem está fora)
sd = {}
for s in AU["sounds"]:
    sid = s["id"]
    if s["heard_in_cutscene"]:
        sd[f"{NS}:sgx2d_{sid[4:]}"] = {"category": "ui", "sounds": [{"name": f"sounds/singularity/{sid}", "is3D": False, "stream": False, "load_on_low_memory": True, "volume": 1.0}]}
    if s["heard_outside_cutscene"]:
        sd[f"{NS}:{sid}"] = {"__use_legacy_max_distance": "true", "category": "neutral", "max_distance": 256, "min_distance": 1,
                             "sounds": [{"name": f"sounds/singularity/{sid}_m", "stream": False}]}
dump("RP/sounds/sound_definitions.json", {"format_version": FV["sound_definitions"], "sound_definitions": sd})

# ------------------------------------------------------------------ main.js mínimo (só para a F0 carregar)
dump("BP/scripts/main.js", """// F0 — esqueleto. Só registra o item e o /scriptevent sgx:spike <n>. O motor entra na F1 (docs/ROADMAP.md).
import { world, system } from "@minecraft/server";

const ITEM = "%s";
world.afterEvents.itemUse.subscribe((ev) => {
  if (ev.itemStack?.typeId !== ITEM) return;
  system.run(() => ev.source.sendMessage({ translate: "sgx.menu.title" }));
});
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "sgx:spike") return;
  const n = Number(String(ev.message ?? "").trim());
  ev.sourceEntity?.sendMessage(`§8[SGX] spike ${n}: ainda não implementado (F0)`);
});
""" % P["item"]["id"])
shutil.copyfile(ROOT / "tools/templates_README.md", OUT / "README.md")
n = sum(1 for _ in OUT.rglob("*") if _.is_file())
print(f"✓ templates/: {n} arquivos")
