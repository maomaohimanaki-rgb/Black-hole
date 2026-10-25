#!/usr/bin/env python3
"""Gera spec/storyboard.json — a versão de máquina do docs/STORYBOARD.md (fonte única de TEMPO e DIREÇÃO por tick).
Rode: python3 tools/build_storyboard_json.py && python3 tools/check_spec.py"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

# v0.2.4 (T-18, escala B): toda distância ×K, com a câmera limitada a CAM_MAX blocos (render 12 = 192). Altura de
# câmera rente ao chão (≤ 1 bloco) NÃO escala: o olho humano olhando para cima é o que dá escala.
_L = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))["scene_scale"]
K, CAM_MAX = _L["k"], _L["camera_max_distance"]
def _k(x): return round(x * K, 2)
def _ku(u): return u if abs(u) <= 1 else _k(u)
def orb(r, az, el, around="O"): return {"around": around, "r": min(_k(r), CAM_MAX), "az": az, "el": el}
def loc(f, r, u): return {"rel": "G", "f": _k(f), "r": _k(r), "u": _ku(u)}
def kf(t, pos, look="O", fov=None, ease="inOutSine", **kw):
    k = {"t": t, "pos": pos, "look": look, "ease": ease}
    if fov is not None: k["fov"] = fov
    k.update(kw); return k
def hud(t, ch, text, clear=None):
    h = {"t": t, "ch": ch, "text": text}
    if clear: h["clear"] = clear
    return h

ACTS = [
 {"id": "I",   "name": "ANOMALIA",   "ticks": [0, 79]},
 {"id": "II",  "name": "INSPIRAL",   "ticks": [80, 239]},
 {"id": "III", "name": "FUSÃO",      "ticks": [240, 279]},
 {"id": "IV",  "name": "DISCO",      "ticks": [280, 419]},
 {"id": "V",   "name": "O PUXÃO",    "ticks": [420, 539]},
 {"id": "VI",  "name": "HORIZONTE",  "ticks": [540, 619]},
 {"id": "VII", "name": "EVAPORAÇÃO", "ticks": [620, 719]},
]

B = []
B.append({"id": "B01", "act": "I", "name": "O SILÊNCIO ERRADO", "ticks": [0, 19],
  "audio": ["sgx_void_in"],
  "camera": [kf(0, loc(-10, 0, 0.6), loc(0, 0, 3), 50, "linear"),
             kf(19, loc(-8, 0, 0.6), loc(0, 0, 6), 48)],
  "vfx": [{"t": 0, "fx": "dust_inflow", "to": "O", "rate": "baixa", "note": "poeira e pólen derivam devagar para um ponto vazio 14 blocos acima do chão"},
          {"t": 12, "fx": "grass_lean", "note": "partículas de folha/grama inclinam para O junto com o sub-grave"}],
  "hud": [hud(4, "SB", "ANOMALY DETECTED", 30), hud(8, "HD", "GRAV. GRADIENT +0.003 g", 19)],
  "flash": [], "shake": [{"t": 12, "level": 1}],
  "intent": "Algo está errado e ainda não se vê. Noite, chão, poeira indo para o lugar errado."})
B.append({"id": "B02", "act": "I", "name": "O PONTO", "ticks": [20, 39],
  "audio": ["sgx_point"],
  "camera": [kf(20, loc(-8, 0, 0.6), "O", 48, "linear"),
             kf(39, loc(-14, 3, 6), "O", 42, "outCubic")],
  "vfx": [{"t": 20, "fx": "bh_spawn", "body": "A", "scale": 0.12, "note": "um ponto de PRETO absoluto com um fio de anel de fótons"},
          {"t": 24, "fx": "lens_glint", "body": "A"}, {"t": 28, "fx": "lens_glint", "body": "A"}, {"t": 32, "fx": "lens_glint", "body": "A"},
          {"t": 20, "fx": "dust_inflow", "rate": "média"},
          {"t": 26, "fx": "bh_grow", "body": "A", "to": 1.0, "dur": 12, "ease": "outExpo"}],
  "hud": [hud(20, "SB", "SINGULARITY · A", 39), hud(22, "HD", "MASS 36 M☉", 39)],
  "flash": [{"t": 20, "level": "N2", "kind": "negative_micro", "color": "#000000"}],
  "shake": [{"t": 20, "level": 2}, {"t": 24, "level": 1}],
  "intent": "O ponto nasce. Primeiro é menor que um pixel; os brilhos de lente mostram que ele dobra a luz."})
B.append({"id": "B03", "act": "I", "name": "O GÊMEO", "ticks": [40, 59],
  "audio": ["sgx_twin"],
  "camera": [kf(40, loc(-14, 3, 6), "O", 42, "linear"),
             kf(42, loc(-14, 3, 6), "B", 50, "outExpo", note="whip-pan de 2 ticks para revelar B"),
             kf(59, orb(16, 20, 15), "O", 55, "inOutSine")],
  "vfx": [{"t": 40, "fx": "bh_spawn", "body": "B", "scale": 0.12},
          {"t": 46, "fx": "bh_grow", "body": "B", "to": 1.0, "dur": 10, "ease": "outExpo"},
          {"t": 48, "fx": "binary_orbit_start", "note": "A e B começam a girar (fórmula de layout.binary, avaliada no cliente)"},
          {"t": 50, "fx": "dust_spiral", "arms": 2}],
  "hud": [hud(40, "HD", "SECOND BODY · 29 M☉", 59), hud(50, "SB", "BINARY LOCKED", 79)],
  "flash": [{"t": 40, "level": "N2", "kind": "negative_micro", "color": "#000000"}],
  "shake": [{"t": 40, "level": 2}],
  "letterbox": "fecha 16:9 → 2,39:1 entre 48 e 79",
  "intent": "Não é um. São dois. O enquadramento começa a ser puxado (as barras fecham)."})
B.append({"id": "B04", "act": "I", "name": "A DANÇA COMEÇA", "ticks": [60, 79],
  "audio": ["sgx_chirp"],
  "camera": [kf(60, orb(16, 20, 15), "O", 55, "linear"),
             kf(79, orb(22, 40, 50), "O", 60, "inOutCubic")],
  "vfx": [{"t": 74, "fx": "ground_ripple", "note": "1ª ondulação no chão (meia-órbita)"}],
  "hud": [hud(60, "HD", "INSPIRAL · f 35 Hz · d 8.0", 79)],
  "flash": [], "shake": [{"t": 60, "level": 1}],
  "intent": "Grua sobe e mostra a dança de cima. O chirp começa grave, quase sentido no peito."})

ripples = [74, 87, 99, 112, 124, 135, 146, 156, 166, 176, 185, 194, 202, 209, 216, 222, 227, 232, 236]
B.append({"id": "B05", "act": "II", "name": "ESPIRAL", "ticks": [80, 139],
  "audio": ["sgx_chirp"],
  "camera": [kf(80, orb(22, 40, 50), "O", 60, "linear"),
             kf(139, orb(16, -60, 25), "O", 58, "inOutSine", note="órbita no sentido CONTRÁRIO ao par: o par parece mais rápido")],
  "vfx": [{"t": t, "fx": "ground_ripple"} for t in ripples if 80 <= t <= 139] +
         [{"t": 80, "fx": "mini_disks", "note": "cada corpo com um disquinho de poeira (impostor pequeno)"},
          {"t": 90, "fx": "leaf_vortex", "note": "folhas e pétalas sobem em funil embaixo do par"}],
  "hud": [hud(80, "HD", "f 37 Hz · d 7.8", 99), hud(100, "HD", "f 39 Hz · d 7.5", 119), hud(120, "HD", "f 41 Hz · d 7.2", 139)],
  "flash": [], "shake": [{"t": 80, "level": 1}, {"t": 120, "level": 2}],
  "intent": "Hipnótico. A imagem gira, o som quase não muda: a tensão vem do ritmo das ondulações."})
B.append({"id": "B06", "act": "II", "name": "ACELERAÇÃO", "ticks": [140, 199],
  "audio": ["sgx_chirp"],
  "camera": [kf(140, orb(16, -60, 25), "O", 58, "linear"),
             kf(199, orb(12, -170, 6), "O", 66, "inOutSine", handheld=0.15, note="desce para o plano da órbita")],
  "vfx": [{"t": t, "fx": "ground_ripple"} for t in ripples if 140 <= t <= 199] +
         [{"t": 150, "fx": "eclipse_glints", "note": "quando um corpo passa na frente do outro (calculado pela fase e pela câmera): brilho de lente N1"},
          {"t": 160, "fx": "dust_spiral", "arms": 2, "tight": True}],
  "hud": [hud(140, "HD", "f 44 Hz · d 6.9", 169), hud(170, "HD", "f 50 Hz · d 6.3", 199)],
  "flash": [], "shake": [{"t": 140, "level": 2}, {"t": 180, "level": 3}],
  "intent": "A câmera entra no plano: os corpos passam rente à lente. O mundo começa a se mexer junto."})
snaps = [202, 209, 216, 222, 227, 232, 236, 239]
B.append({"id": "B07", "act": "II", "name": "O GRITO", "ticks": [200, 239],
  "audio": ["sgx_chirp", "sgx_merge"],
  "camera": [kf(200, orb(12, -170, 6), "O", 66, "linear")] +
            [kf(t, orb(round(12 - 6 * i / 7, 1), -170 - 4 * i, 6), "O", 66 - 3 * (i + 1), "step", cut=True, note="snap-zoom")
             for i, t in enumerate(snaps)],
  "vfx": [{"t": t, "fx": "ground_ripple"} for t in ripples if 200 <= t <= 239] +
         [{"t": 220, "fx": "photon_rings_merge", "note": "os dois anéis de fótons se deformam num 8"},
          {"t": 230, "fx": "dust_sheet", "note": "a espiral de poeira vira uma lâmina"}],
  "hud": [hud(200, "HD", "f 62 Hz · d 5.5", 229), hud(230, "HD", "f 103 Hz · d 3.9", 235), hud(236, "HD", "f 146 Hz · d 3.1", 238), hud(239, "HD", "f 245 Hz", 240)],
  "flash": [{"t": t, "level": "N1", "kind": "white", "color": "#F2F6FF"} for t in snaps],
  "shake": [{"t": 200, "level": 3}, {"t": 222, "level": 4}, {"t": 232, "level": 5}, {"t": 236, "level": 6}],
  "intent": "O chirp sobe de verdade. Snap-zooms nos acentos. Termina colado nos dois corpos."})
B.append({"id": "B08", "act": "III", "name": "FUSÃO / RINGDOWN", "ticks": [240, 259],
  "audio": ["sgx_merge", "sgx_ringdown"],
  "camera": [kf(240, orb(6, -198, 6), "O", 40, "step", impact_frame=2),
             kf(242, orb(40, -200, 12), "O", 70, "step", cut=True, note="corte seco para o plano aberto"),
             kf(247, orb(40, -200, 12), "O", 76, "outSine", note="a onda gravitacional passa pela câmera: FOV respira (+ e ×)"),
             kf(250, orb(40, -200, 12), "O", 66, "inOutSine"), kf(253, orb(40, -200, 12), "O", 73, "inOutSine"),
             kf(256, orb(40, -200, 12), "O", 68, "inOutSine"), kf(259, orb(39, -200, 12), "O", 70, "inOutSine")],
  "vfx": [{"t": 240, "fx": "merge", "note": "A+B → um só; sombra final (raio 2,08)"},
          {"t": 241, "fx": "ringdown_wobble", "formula": "layout.black_hole.ringdown"},
          {"t": 241, "fx": "gw_shell", "note": "casca esférica de ar 'tremido' + anel no chão a 6 blocos/tick"},
          {"t": 241, "fx": "leaf_burst"}],
  "hud": [hud(241, "SB", "THEY BECAME ONE", 262), hud(241, "HD", "MERGER · 62 M☉", 245), hud(246, "HD", "ΔM = 3.0 M☉ → GRAVITATIONAL WAVES", 262)],
  "flash": [{"t": 240, "level": "N4", "kind": "impact_negative", "dur": 2, "note": "negativo: o buraco negro BRANCO num mundo preto"},
            {"t": 242, "level": "N3", "kind": "white", "color": "#FFFFFF"}],
  "shake": [{"t": 241, "level": 10}, {"t": 247, "level": 6}, {"t": 250, "level": 3}],
  "letterbox": "rebote 2,39 → 2,7 → 2,39 entre 240 e 246",
  "intent": "O clímax da primeira metade. O impacto é ao contrário (negativo) e depois o espaço inteiro respira."})
B.append({"id": "B09", "act": "III", "name": "O VAZIO RESPIRA", "ticks": [260, 279],
  "audio": ["sgx_ringdown"],
  "camera": [kf(260, orb(39, -200, 12), "O", 70, "linear"), kf(279, orb(26, -205, 8), "O", 64, "inOutSine")],
  "vfx": [{"t": 260, "fx": "dust_settle", "note": "a poeira cai de volta"}, {"t": 272, "fx": "first_sparks", "note": "primeiras faíscas de matéria começam a orbitar"}],
  "hud": [], "flash": [], "shake": [],
  "silence": [268, 279],
  "intent": "Silêncio quase total. Um buraco negro sozinho, com o anel fino. A calma antes da fome."})
B.append({"id": "B10", "act": "IV", "name": "IGNIÇÃO DO DISCO", "ticks": [280, 309],
  "audio": ["sgx_disk_ignite"],
  "camera": [kf(280, orb(26, -205, 8), "O", 64, "linear"), kf(309, orb(20, -145, 12), "O", 60, "inOutSine")],
  "vfx": [{"t": 280, "fx": "matter_streams", "count": 5, "note": "5 fluxos de poeira e detritos sobem do chão em espiral para o plano do disco"},
          {"t": 280, "fx": "disk_ring_ignite", "ring": 5}, {"t": 286, "fx": "disk_ring_ignite", "ring": 4}, {"t": 292, "fx": "disk_ring_ignite", "ring": 3},
          {"t": 298, "fx": "disk_ring_ignite", "ring": 2}, {"t": 304, "fx": "disk_ring_ignite", "ring": 1}],
  "hud": [hud(280, "SB", "ACCRETION", 309), hud(300, "HD", "T 10⁷ K", 330)],
  "flash": [{"t": 304, "level": "N3", "kind": "white", "color": "#DDE6FF"}],
  "shake": [{"t": 280, "level": 2}, {"t": 292, "level": 3}, {"t": 304, "level": 4}],
  "intent": "O disco acende de FORA para DENTRO: vermelho-escuro → laranja → branco-azulado no anel interno."})
B.append({"id": "B11", "act": "IV", "name": "O ANEL", "ticks": [310, 349],
  "audio": ["sgx_disk_loop"],
  "camera": [kf(310, orb(20, -145, 12), "O", 60, "linear"), kf(349, orb(14, -135, 9), "O", 52, "inOutSine", note="plano-herói: disco quase de lado")],
  "vfx": [{"t": 310, "fx": "impostor_hero", "note": "arco do disco por cima e por baixo da sombra (lente), anel de fótons nítido, Doppler: lado esquerdo azul-branco e forte, direito laranja e fraco"},
          {"t": 310, "fx": "lensed_starfield", "note": "anel de Einstein com as estrelas da NASA em volta da sombra"},
          {"t": 310, "fx": "disk_turbulence", "note": "flipbook de turbulência girando (Kepler)"}],
  "hud": [hud(315, "HD", "SPIN a* = 0.67", 329), hud(330, "HD", "ISCO 3 r_s", 349)],
  "flash": [], "shake": [],
  "intent": "O plano que todo mundo vai printar. Contemplativo: shake 0, empurrão lento."})
B.append({"id": "B12", "act": "IV", "name": "JATOS", "ticks": [350, 389],
  "audio": ["sgx_jet"],
  "camera": [kf(350, orb(14, -135, 9), "O", 52, "linear"),
             kf(360, orb(30, -120, -10), {"pitch": -35, "yaw_rel": 0}, 70, "step", cut=True, note="contra-plongée a partir do chão"),
             kf(380, orb(30, -120, -10), {"pitch": -80, "yaw_rel": 0}, 74, "inOutCubic", note="segue o jato até as nuvens"),
             kf(389, orb(26, -110, 4), "G", 70, "inOutSine", note="desce e mostra o jato de baixo furando o chão")],
  "vfx": [{"t": 358, "fx": "jet_precharge", "note": "polos brilham 2 ticks antes"},
          {"t": 360, "fx": "jets_on", "note": "dois jatos (lookat_y), violeta-azul; nós de plasma sobem a 8 blocos/tick"},
          {"t": 360, "fx": "ground_hit_glow", "at": "G"}],
  "destruction": [{"t": 360, "op": "shaft", "radius": 3, "depth": 28, "hidden_by": "flash N4"}],
  "hud": [hud(362, "SB", "RELATIVISTIC JETS", 389), hud(365, "HD", "v = 0.99 c", 389)],
  "flash": [{"t": 360, "level": "N4", "kind": "white", "color": "#E9E4FF"}, {"t": 361, "level": "N3", "kind": "white", "color": "#C9C2FF"}],
  "shake": [{"t": 360, "level": 10}, {"t": 362, "level": 6}, {"t": 366, "level": 3}],
  "intent": "A primeira violência contra o mundo: o jato de baixo fura o chão."})
B.append({"id": "B13", "act": "IV", "name": "O OLHO DO MUNDO", "ticks": [390, 419],
  "audio": ["sgx_jet", "sgx_disk_loop", "sgx_pad"],
  "camera": [kf(390, orb(26, -110, 4), "O", 70, "linear"), kf(419, orb(60, -100, 20), "O", 60, "inOutSine", note="plano geral, grua subindo")],
  "vfx": [{"t": 390, "fx": "ground_glow", "note": "decalques no chão com a cor do disco (a paisagem 'iluminada' por ele)"},
          {"t": 400, "fx": "jets_fade", "until": 419}],
  "hud": [], "flash": [], "shake": [{"t": 390, "level": 1}],
  "intent": "Respiro. O buraco negro como um olho sobre a paisagem. Coral grave entra."})
B.append({"id": "B14", "act": "V", "name": "MARÉ", "ticks": [420, 459],
  "audio": ["sgx_tidal"],
  "camera": [kf(420, orb(34, -100, -8), "O", 66, "step", cut=True, note="rente ao chão, olhando para cima através do terreno"),
             kf(459, orb(28, -95, -6), "O", 66, "inOutSine")],
  "vfx": [{"t": 420, "fx": "debris_rise", "max_alive": 48, "note": "blocos do próprio terreno (texturas do bioma) sobem em espiral e esticam"},
          {"t": 420, "fx": "ground_ripple_up"}],
  "destruction": [{"t": 422, "op": "crater_slice", "slice": 1, "hidden_by": "poeira + debris"},
                  {"t": 432, "op": "crater_slice", "slice": 2}, {"t": 440, "op": "crater_slice", "slice": 3}, {"t": 448, "op": "crater_slice", "slice": 4}],
  "hud": [hud(420, "SB", "TIDAL FORCES", 459), hud(430, "HD", "STRAIN 10⁹ g", 459)],
  "flash": [{"t": 446, "level": "N1", "kind": "white", "color": "#FFE2C4"}, {"t": 452, "level": "N1", "kind": "white", "color": "#FFE2C4"}, {"t": 457, "level": "N2", "kind": "white", "color": "#FFD2A8"}],
  "shake": [{"t": 420, "level": 3}, {"t": 430, "level": 4}, {"t": 438, "level": 5}, {"t": 446, "level": 6}, {"t": 452, "level": 7}, {"t": 457, "level": 8}],
  "intent": "O mundo é que cai para cima. Cada estalo de madeira/pedra é um pedaço de chão se soltando."})
B.append({"id": "B15", "act": "V", "name": "ESPAGUETE", "ticks": [460, 499],
  "audio": ["sgx_fall"],
  "camera": [kf(460, {"follow": "hero_chunk", "back": 3, "up": 1}, "hero_chunk", 66, "step", cut=True, note="smash-cut para o ponto de vista do pedaço de chão"),
             kf(499, {"follow": "hero_chunk", "back": 3, "up": 0.5}, "O", 90, "inQuad")],
  "vfx": [{"t": 460, "fx": "hero_chunk", "note": "um bloco de grama em espiral; estica (y ×6, xz ×0,3) conforme se aproxima"},
          {"t": 460, "fx": "speed_lines"}, {"t": 470, "fx": "debris_streaks"}],
  "hud": [hud(470, "HD", "r = 6 r_s", 484), hud(485, "HD", "r = 3 r_s", 494), hud(495, "HD", "r = 1.5 r_s · PHOTON SPHERE", 504)],
  "flash": [], "shake": [{"t": 460, "level": 4}, {"t": 480, "level": 6}, {"t": 495, "level": 7}],
  "letterbox": "aperta 2,39 → 2,8 entre 460 e 499",
  "intent": "A gente vira o pedaço de chão. Esticado, rápido, sem volta."})
B.append({"id": "B16", "act": "V", "name": "A QUEDA", "ticks": [500, 539],
  "audio": ["sgx_fall"],
  "camera": [kf(500, {"follow": "hero_chunk", "back": 3, "up": 0.5}, "O", 90, "linear", note="cruza o plano do disco (clarão)"),
             kf(539, {"along": "O", "dist_to_shadow": _k(6)}, "O", 120, "inCubic", note="FOV abre: o anel de fótons vira um círculo gigante")],
  "vfx": [{"t": 500, "fx": "disk_plane_cross"}, {"t": 505, "fx": "aberration_ring", "note": "o universo de fora comprime num anel (overlay assado)"},
          {"t": 510, "fx": "redshift_grade", "from": 0.0, "to": 0.5, "until": 539}, {"t": 520, "fx": "chunk_to_thread"}],
  "hud": [hud(505, "HD", "r → r_s", 524), hud(525, "HD", "z = 9.0", 539)],
  "flash": [{"t": 500, "level": "N3", "kind": "white", "color": "#FFF2DD"}],
  "shake": [{"t": 500, "level": 7}, {"t": 515, "level": 5}, {"t": 530, "level": 3}],
  "letterbox": "aperta 2,8 → 3,2 entre 500 e 539",
  "intent": "Mergulho. O tempo começa a ficar mole (o som afunda)."})
B.append({"id": "B17", "act": "VI", "name": "O ÚLTIMO OLHAR", "ticks": [540, 579],
  "audio": ["sgx_horizon"],
  "camera": [kf(540, {"along": "O", "dist_to_shadow": _k(6)}, "O", 120, "linear"),
             kf(579, {"along": "O", "dist_to_shadow": _k(2.5)}, "O", 100, "outSine", stutter=[1, 1, 2, 2, 3, 4, 6, 8], note="dilatação: a pose segura por cada vez mais ticks")],
  "vfx": [{"t": 540, "fx": "redshift_grade", "from": 0.5, "to": 0.95, "until": 579}, {"t": 540, "fx": "aberration_ring_shrink"}],
  "hud": [hud(545, "HD", "t → ∞", 559), hud(560, "HD", "SIGNAL LOST", 579, ), hud(560, "HT", "3")],
  "flash": [], "shake": [{"t": 540, "level": 2}, {"t": 560, "level": 1}],
  "intent": "Congelamento. Tudo fica vermelho, lento, distante."})
B.append({"id": "B18", "act": "VI", "name": "CRUZAMENTO", "ticks": [580, 599],
  "audio": ["sgx_horizon"],
  "camera": [kf(580, {"along": "O", "dist_to_shadow": _k(2.5)}, "O", 100, "linear", stutter=[8]), kf(599, {"along": "O", "dist_to_shadow": _k(0.5)}, "O", 96, "inSine")],
  "vfx": [{"t": 580, "fx": "iris_close", "until": 590}, {"t": 590, "fx": "last_photon", "until": 599, "note": "um ponto de luz no centro que encolhe"}],
  "hud": [], "flash": [], "shake": [],
  "letterbox": "3,2 → fechado (preto) entre 580 e 590",
  "intent": "As barras se encontram. Sobra um fóton."})
B.append({"id": "B19", "act": "VI", "name": "SILÊNCIO ABSOLUTO", "ticks": [600, 619],
  "audio": [],
  "camera": [kf(600, orb(70, -100, 35), "O", 55, "step", cut=True, note="teleporte escondido no preto")],
  "vfx": [{"t": 600, "fx": "screen_black", "until": 619}, {"t": 601, "fx": "despawn_debris"}, {"t": 602, "fx": "spawn_remnant", "scale": 0.6}, {"t": 604, "fx": "crater_rim_glow"}],
  "destruction": [{"t": 600, "op": "crater_bulk", "budget_ms": 25, "hidden_by": "tela preta (20 ticks)"}],
  "hud": [], "flash": [], "shake": [],
  "silence": [600, 619],
  "intent": "Um segundo de NADA: preto e mudo. O melhor momento do filme."})
B.append({"id": "B20", "act": "VII", "name": "DE FORA", "ticks": [620, 659],
  "audio": ["sgx_hawking"],
  "camera": [kf(620, orb(70, -100, 35), "O", 55, "linear"), kf(659, orb(55, -95, 30), "O", 55, "inOutSine")],
  "vfx": [{"t": 620, "fx": "fade_in_from_black", "dur": 12}, {"t": 620, "fx": "hawking_sparkles", "rate": "baixa"}],
  "hud": [], "flash": [], "shake": [],
  "letterbox": "abre para 16:9 entre 620 e 630 (a respiração)",
  "intent": "Do lado de fora, o tempo é normal: uma cratera perfeita e um buraco negro pequeno pairando."})
hk = [660, 672, 682, 690, 696, 699]
B.append({"id": "B21", "act": "VII", "name": "HAWKING", "ticks": [660, 699],
  "audio": ["sgx_hawking"],
  "camera": [kf(660, orb(55, -95, 30), "O", 55, "linear"), kf(699, orb(30, -90, 18), "O", 50, "inOutSine")],
  "vfx": [{"t": 660, "fx": "bh_shrink", "to": 0.05, "until": 699, "ease": "inExpo"}, {"t": 660, "fx": "hawking_sparkles", "rate": "crescente"}] +
         [{"t": t, "fx": "hawking_flicker"} for t in hk],
  "hud": [], "flash": [{"t": t, "level": ("N1" if i < 3 else "N2"), "kind": "white", "color": "#E8FBFF"} for i, t in enumerate(hk)],
  "shake": [],
  "intent": "Evapora. Quanto menor, mais quente e mais rápido pisca (é física: a temperatura de Hawking sobe quando a massa cai)."})
B.append({"id": "B22", "act": "VII", "name": "O ÚLTIMO CLARÃO", "ticks": [700, 719],
  "audio": ["sgx_burst"],
  "camera": [kf(700, orb(30, -90, 18), "O", 50, "linear"), kf(719, orb(40, -90, 22), "O", 52, "outSine")],
  "vfx": [{"t": 700, "fx": "final_burst", "note": "casca de luz limpa que se expande devagar e lava a cratera"}, {"t": 704, "fx": "stars_twinkle"}],
  "hud": [hud(704, "TT", "SINGULARITY", 719), hud(706, "TT2", "黑洞", 719)],
  "flash": [{"t": 700, "level": "N4", "kind": "white_soft", "color": "#FFFFFF", "note": "o único branco de paz do filme — SEM shake"}],
  "shake": [],
  "intent": "Perdão. Luz, sem violência. O mundo fica: a cratera sob as estrelas."})

LETTERBOX = [  # razão de aspecto alvo (16:9 = 1,78 = aberto). "closed" = preto total.
 {"t": 0, "ratio": 1.78}, {"t": 47, "ratio": 1.78}, {"t": 79, "ratio": 2.39, "ease": "inOutSine"},
 {"t": 240, "ratio": 2.39}, {"t": 242, "ratio": 2.7, "ease": "outQuad"}, {"t": 246, "ratio": 2.39, "ease": "outBack"},
 {"t": 459, "ratio": 2.39}, {"t": 499, "ratio": 2.8, "ease": "inOutSine"}, {"t": 539, "ratio": 3.2, "ease": "inOutSine"},
 {"t": 580, "ratio": 3.2}, {"t": 590, "ratio": "closed", "ease": "inCubic"}, {"t": 619, "ratio": "closed"},
 {"t": 620, "ratio": "closed"}, {"t": 630, "ratio": 1.78, "ease": "outSine"}, {"t": 719, "ratio": 1.78}]
GRADE = [{"t": 0, "redshift": 0.0}, {"t": 509, "redshift": 0.0}, {"t": 539, "redshift": 0.5, "ease": "inQuad"},
         {"t": 579, "redshift": 0.95, "ease": "inOutSine"}, {"t": 599, "redshift": 1.0}, {"t": 600, "redshift": 0.0, "note": "zera no preto"}]
CONTINUITY = [
 {"item": "Letterbox", "rule": "16:9 (0–47) → 2,39 (79–459) → aperta até 3,2 (539) → fecha (590) → preto (600–619) → 16:9 (630–fim)"},
 {"item": "HUD", "rule": "Plex Mono branco-gelo. Existe de 4 a 579. Nunca depois do 580. Título só no 704."},
 {"item": "Shake 10", "rule": "Só no 241 (fusão) e no 360 (jatos)."},
 {"item": "Shake 0 obrigatório", "rule": "B11 (plano-herói), B19 (silêncio), B20–B22 (lado de fora / evaporação)."},
 {"item": "Silêncios", "rule": "268–279 (quase) e 600–619 (absoluto: nenhum som, nenhuma imagem)."},
 {"item": "Paleta", "rule": "noite fria → prata (ondas) → corpo negro do disco (laranja → branco-azul) → violeta (jatos) → âmbar → vermelho (desvio para o vermelho) → preto → branco-gelo (Hawking)"},
 {"item": "Flash branco de paz", "rule": "Só o do 700. Todos os outros flashes são de energia (com shake ou de lente)."},
 {"item": "Impacto negativo", "rule": "Só no 240: o buraco negro vira branco e o mundo preto por 2 ticks."},
 {"item": "Escala do buraco negro", "rule": "layout.black_hole.scale_curve — nunca encolhe antes do 600 (no preto)."},
 {"item": "Destruição", "rule": "Todo corte de bloco fica embaixo de algo que já cobre a tela: flash 360, poeira 420–459, preto 600–619."},
]
doc = {"meta": {"title": "SINGULARITY (buraco negro)", "tick_rate": 20, "film_ticks": 720, "outro_ticks": 20,
                "source_of_truth": "Este JSON manda no TEMPO; o docs/STORYBOARD.md manda na DIREÇÃO.",
                "camera_conventions": "spec/layout.json → frame.camera_orbit; ease = nomes do camera_engine.js; cut = chegada seca; stutter = segura a pose N ticks"},
       "acts": ACTS, "blocks": B, "letterbox_curve": LETTERBOX, "grade_curve": GRADE, "continuity": CONTINUITY,
       "flash_levels": {"N0": "sem flash", "N1": "brilho suave +0,5 EV, shake ≤1", "N2": "pulso/halo +1 EV, shake ≤3", "N3": "flash cheio 2–3 ticks, +2 EV, shake ≤6", "N4": "white-out/impacto 1–2 ticks, +4 EV"},
       "hud_channels": {"SB": "legenda (canto inferior esquerdo, dentro da barra)", "HD": "linha de HUD técnica", "HT": "tremor do HUD (1–3)", "TT": "título", "TT2": "subtítulo CJK"}}
(ROOT / "spec" / "storyboard.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
print("ok", len(B), "blocos")
