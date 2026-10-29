#!/usr/bin/env python3
"""O buraco negro como GEOMETRIA (v0.3.1, T-25): malha que a lente dobra, animada pelo Molang no cliente.

O usuário vetou sprite (v0.3.0 usava partícula com atlas): "tem que ser objeto, entidade, JSON e Molang". E mostrou
os vídeos da NASA (disco xadrez dobrado pela lente). Este script gera tudo o que a entidade precisa:

1. **Malhas por bin de elevação da câmera** (spec/bake.json → lens.bins_e_deg). Cada vértice do disco (r, ψ) vai
   para a posição da sua imagem (bh_lens.image): a imagem direta (k = 0) fica no ponto real do disco deslocado pela
   lente (perto do buraco ela vira a "corcova" por cima da sombra; longe, é o disco 3D de verdade, com paralaxe), e a
   secundária (k = 1, o arco por baixo) fica no plano do céu. A sombra, o anel de fótons e o halo também.
   A malha fica num osso que o cliente vira para a câmera a cada quadro (q.rotation_to_camera) e espelha na
   vertical quando a câmera está abaixo do disco.
2. **O giro**: a textura do disco é polar (U = ψ, V = r) e anda por uv_anim, um render controller por anel com
   o ω de Kepler, com o tempo em q.frame_alpha (liso em qualquer FPS, igual ao creeper carregado do vanilla).
   Material `charged_creeper` (aditivo, sem culling, com USE_UV_ANIM); a sombra é `entity_alphatest`.
3. **Doppler**: o lado que vem para a câmera está fixo no referencial da câmera, então ele é uma segunda camada
   aditiva com textura parada (por grupo de elevação e por imagem k).
4. **Molang**: a curva de escala, o ringdown, a ignição dos anéis e o fim saem do spec como expressões.

As texturas usam o truque do espelho vertical (cada região é simétrica em V em torno do meio da textura): a
malha funciona igual se o jogo contar V de cima ou de baixo.

Saída: RP/models/entity/sgx_bh*.geo.json, RP/textures/sgx/bh/*.png, RP/entity, RP/render_controllers,
RP/animations, BP/entities (gerados, P-31/P-29) e a prévia em build/bake/lens_sheet.png (um rasterizador numpy
que soma as camadas como o jogo soma). Cache em build/bake/ (--force refaz)."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bh_engine as E  # noqa: E402
import bh_lens as LZ  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "spec/bake.json").read_text(encoding="utf-8"))
LAYOUT = json.loads((ROOT / "spec/layout.json").read_text(encoding="utf-8"))
PROJECT = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
PHYS, LENS = SPEC["physics"], SPEC["lens"]
BUILD = ROOT / "build/bake"
CACHE = BUILD / "model"
NS = "singularity"
BC = 1.5 * math.sqrt(3)  # raio da sombra em r_s


# ------------------------------------------------------------------ física do disco (repouso)


def temperature(r, r_in, r_out):
    """Novikov–Thorne simplificado, pico → t_peak, borda externa → t_edge (VISUAL_TECH §2.2, T-24)."""
    prof = r ** -0.75 * np.clip(1 - np.sqrt(r_in / r), 0, 1) ** 0.25
    rr = np.linspace(r_in, 15.0, 4000)
    pmax = (rr ** -0.75 * np.clip(1 - np.sqrt(r_in / rr), 0, 1) ** 0.25).max()
    pout = 15.0 ** -0.75 * (1 - math.sqrt(r_in / 15.0)) ** 0.25
    tp, te = PHYS["t_peak_k"], PHYS["t_edge_k"]
    return te + (tp - te) * np.clip((prof - pout) / (pmax - pout), 0, 1)


def tonemap(x):
    return 1 - np.exp(-1.15 * x)


def display(rgb_lin):
    """Linear → tela pela luminância (o mesmo do bh_engine): preserva o tom."""
    L = np.maximum(rgb_lin.max(axis=-1), 1e-9)
    out = rgb_lin * (tonemap(L) / L)[..., None]
    return np.clip(out, 0, 1) ** (1 / 2.2)


def disk_light(r, g, r_in=3.0, r_out=15.0):
    """Cor (tela, 0–1) do disco no raio r com fator g (Doppler + gravitacional)."""
    T = temperature(r, r_in, r_out)
    lum = (T / PHYS["t_peak_k"]) ** PHYS["lum_exponent"] * g ** 4
    lum = lum * np.clip((r_out - r) / (0.12 * r_out), 0, 1)  # borda externa suave
    lin = E.temp_rgb(T * g) * (lum * PHYS["exposure"])[..., None]
    return display(lin)


def g_rest(r):
    return np.sqrt(np.clip(1 - 1.5 / r, 1e-4, 1))


# ------------------------------------------------------------------ ruído periódico


def pnoise(x, y, px, seed):
    """Ruído de valor suave, periódico em x com período px (inteiro); y livre."""
    rng = np.random.default_rng(seed)
    py = 256
    g = rng.standard_normal((py, px))
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    xa, xb = x0 % px, (x0 + 1) % px
    ya, yb = y0 % py, (y0 + 1) % py
    return (g[ya, xa] * (1 - sx) + g[ya, xb] * sx) * (1 - sy) + (g[yb, xa] * (1 - sx) + g[yb, xb] * sx) * sy


def pfbm(u, s, cx, cy, octaves, seed, gain=0.55):
    """fBm periódico em u ∈ [0, 1) com cx células na 1ª oitava; s ∈ [0, 1] com cy células."""
    out = np.zeros_like(u)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        f = 2 ** o
        out += amp * pnoise(u * cx * f, s * cy * f, cx * f, seed + 17 * o)
        tot += amp
        amp *= gain
    return out / tot


# ------------------------------------------------------------------ texturas


def mirror_v(region):
    """Região (h, w, c) → (2h, w, c) com a metade de baixo espelhada (V de cima ou de baixo dá no mesmo)."""
    return np.concatenate([region, region[::-1]], axis=0)


def flow_texture():
    """Textura do disco que anda (U = ψ, V = r): estrias concêntricas finas × aglomerados alongados no giro,
    na luz de repouso (g gravitacional só). É a camada de base, no nível flow_level (o Doppler soma por cima)."""
    W, H = LENS["flow_tex"]
    h = H // 2
    look = LENS["look"]
    u = (np.arange(W) + 0.5) / W
    s = (np.arange(h) + 0.5) / h
    U, S = np.meshgrid(u, s)
    r_in, r_out = PHYS["r_in_rs"], PHYS["r_out_rs"]
    r = r_in + S * (r_out - r_in)
    rng = np.random.default_rng(look["seed"])
    # estrias: anéis gaussianos finos em raios aleatórios (como a NASA mostra), contraste ~±45 %
    stri = np.zeros(h)
    rs = r[:, 0]
    for _ in range(look["striations"]):
        c = rng.uniform(r_in, r_out)
        w = rng.uniform(0.02, 0.16) * (c / 6) ** 0.5
        stri += rng.uniform(0.3, 1.0) * np.exp(-((rs - c) / w) ** 2)
    stri = 0.55 + 0.9 * stri / stri.max()
    # vãos escuros finos nas bordas dos anéis do storyboard (cada anel gira no seu ω: o vão esconde o corte)
    for edge in LENS["band_edges_rs"][1:-1]:
        stri *= 1 - 0.75 * np.exp(-((rs - edge) / 0.07) ** 2)
    # aglomerados: fBm esticado no giro (poucas células em ψ, muitas em r), mais forte no meio do disco
    turb = pfbm(U, S, 6, 48, 5, look["seed"] + 1)
    fil = pfbm(U, S, 3, 160, 3, look["seed"] + 2)  # filamentos bem finos
    t = np.clip(0.72 + 0.55 * turb + 0.25 * fil, 0.15, 1.6)
    light = disk_light(r, g_rest(r))  # (h, W, 3), tela
    img = light * (stri[:, None] * t)[..., None] * look["flow_level"]
    img = np.clip(img, 0, 1)
    return mirror_v(img)


def doppler_region(tr, e_deg, k, w, h):
    """Camada parada no referencial da câmera: o quanto o Doppler soma em cima da base (só soma: o lado que se
    afasta fica na base, mais escuro e mais vermelho)."""
    look = LENS["look"]
    r_in, r_out = PHYS["r_in_rs"], PHYS["r_out_rs"]
    # as colunas seguem o mesmo parâmetro da malha (psi_grid): densas atrás do buraco, onde a corcova estica um
    # pedacinho de ψ por um arco enorme (v0.3.1: com ψ uniforme o Doppler da corcova saía em blocos)
    psi = psi_of_x(-1 + 2 * (np.arange(w) + 0.5) / w)
    hc = 128  # o Doppler é liso: calcula em 128 linhas e interpola
    sc = (np.arange(hc) + 0.5) / hc
    P, S = np.meshgrid(psi, sc)
    r = r_in + S * (r_out - r_in)
    im = LZ.image(tr, r.ravel(), P.ravel(), e_deg, k, PHYS["beta_scale"])
    g = np.where(im["ok"], im["g"], 1.0).reshape(r.shape)
    s = (np.arange(h) + 0.5) / h
    gi = np.stack([np.interp(s, sc, g[:, c]) for c in range(w)], axis=1)
    rr = r_in + s[:, None] * (r_out - r_in) + 0 * gi
    full = disk_light(rr, gi)
    base = disk_light(rr, g_rest(rr)) * look["flow_level"]
    return np.clip(full - base, 0, 1) * look["doppler_level"]


def static_texture(tr):
    """Regiões lado a lado (cada uma com a altura toda, espelhada em V):
    0–7 = Doppler (grupo de elevação × k), 8 = anel de fótons + halo (V = b), 9 = preto (sombra)."""
    W, H = LENS["static_tex"]
    h = H // 2
    groups = LENS["doppler_groups_e"]
    n = len(groups) * 2 + 2
    rw = W // n
    img = np.zeros((H, W, 3))
    regions = {}
    for gi, e in enumerate(groups):
        for k in (0, 1):
            idx = gi * 2 + k
            x0 = idx * rw
            reg = doppler_region(tr, e, k, rw - 4, h)
            img[:, x0 + 2:x0 + rw - 2] = mirror_v(reg)
            regions[("dop", gi, k)] = (x0 + 2, rw - 4)
    # anel + halo: V = (b − b_c)/(halo_out − b_c)
    x0 = len(groups) * 2 * rw
    look = LENS["look"]
    s = (np.arange(h) + 0.5) / h
    b = BC + s * (LENS["halo_out_rs"] - BC)
    ring_col = np.array(E._hex_lin(E.PALETTE["photon_ring"])) ** (1 / 2.2)
    ring = look["ring"] * np.exp(-((b - BC - 0.035) / 0.035) ** 2) + 0.35 * look["ring"] * np.exp(-((b - BC) / 0.25) ** 2)
    halo_col = np.array(E._hex_lin("#FFB46B")) ** (1 / 2.2)
    halo = look["halo"] * np.exp(-(b - BC) / 1.6)
    strip = np.clip(ring[:, None] * ring_col + halo[:, None] * halo_col, 0, 1)
    img[:, x0 + 2:x0 + rw - 2] = mirror_v(np.repeat(strip[:, None, :], rw - 4, axis=1))
    regions["ring"] = (x0 + 2, rw - 4)
    regions["black"] = ((n - 1) * rw + 2, rw - 4)  # já é preto
    return img, regions


def save_png(arr, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    rgba = np.concatenate([a, np.full(a.shape[:2] + (1,), 255, np.uint8)], axis=-1)  # alfa 1: o ALPHA_TEST não corta
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)


# ------------------------------------------------------------------ malhas


def model(p):
    """(R, U, B) em r_s → unidades de modelo (16 por bloco; assado com r_s = 1 bloco, o osso escala).
    A frente do modelo (−Z, a "cara" de um mob) é o lado da câmera: B → −Z."""
    return np.stack([16 * p[..., 0], 16 * p[..., 1], -16 * p[..., 2]], axis=-1)


def psi_grid(M):
    """ψ de −π/2 (o ponto mais perto da câmera) a 3π/2, denso em π/2 (o ponto atrás do buraco), onde a lente
    dobra mais: lá a corcova e o arco de baixo mudam rápido com ψ (v0.3.1: com ψ uniforme a corcova saía poligonal)."""
    return psi_of_x(np.linspace(-1, 1, M + 1))


def psi_of_x(x):
    return math.pi / 2 + math.pi * np.sign(x) * np.abs(x) ** 1.7


def rows_for(edges, per):
    rows, band_of_row = [edges[0]], []
    for k in range(len(edges) - 1):
        for j in range(1, per[k] + 1):
            rows.append(edges[k] + (edges[k + 1] - edges[k]) * j / per[k])
            band_of_row.append(k)
    return np.array(rows), band_of_row  # band_of_row[i] = anel da faixa de quads entre rows[i] e rows[i+1]


def direct_mask(tr, e, hw, N, r_in, r_out):
    """Onde a imagem direta (k = 0) cobre a tela: a secundária não é desenhada ali (o disco é opaco)."""
    xs = np.linspace(-hw, hw, N)
    X, Y = np.meshgrid(xs, xs[::-1])
    o, R, Up = LZ.frame(e)
    b = np.hypot(X, Y) + 1e-9
    ev = (X[..., None] * R + Y[..., None] * Up) / b[..., None]
    n = np.array([0.0, 1.0, 0.0])
    phi0 = np.arctan2(-(o @ n), ev @ n) % math.pi
    bcap = np.interp(b, tr.b, tr.cap, right=np.inf)
    besc = np.interp(b, tr.b, tr.esc, right=np.inf)
    u = E.lookup(tr.U, tr.b, b, phi0, tr.dphi)
    r = 1 / np.maximum(u, 1e-6)
    return (phi0 < bcap) & (phi0 < besc) & (r >= r_in) & (r <= r_out)


def lens_bin(tr, e, cfg, small=False):
    """Todas as malhas de um bin: {'flow': [peça por anel], 'dop': [peça por anel], 'shadow', 'ring'}.
    Cada peça = (posições de modelo (n, 3), uvs normalizadas (n, 2), quads (m, 4) de índices)."""
    edges = cfg["band_edges_rs"]
    r_in, r_out = edges[0], edges[-1]
    rows, band_of_row = rows_for(edges, cfg["rows_per_band"])
    M = cfg["psi_segments"]
    psi = psi_grid(M)
    Rg, Pg = np.meshgrid(rows, psi, indexing="ij")         # (nr, M+1)
    o, Rv, Up = LZ.frame(e)
    d0 = LENS["d0_rs"]
    W_flow = 1.0
    u_flow = Pg / (2 * math.pi)                             # U = ψ (o uv_anim gira; −0,25…0,75, a textura repete)
    v_flow = 0.5 * (Rg - PHYS["r_in_rs"]) / (PHYS["r_out_rs"] - PHYS["r_in_rs"])  # metade de cima (espelho)

    def direct_pos():
        im = LZ.image(tr, Rg.ravel(), Pg.ravel(), e, 0, PHYS["beta_scale"])
        X, Y, z = im["X"].reshape(Rg.shape), im["Y"].reshape(Rg.shape), im["z"].reshape(Rg.shape)
        P = LZ.disk_point(Rg, Pg)
        X0, Y0 = Rg * np.cos(Pg), Rg * np.sin(Pg) * math.sin(math.radians(e))
        f = np.clip((d0 + z) / d0, 0.3, 2.0)
        dX, dY = (X - X0) * f, (Y - Y0) * f
        Pp = P + dX[..., None] * Rv + dY[..., None] * Up
        return Pp, im["ok"].reshape(Rg.shape), np.stack([X, Y], -1)

    def secondary_pos():
        im = LZ.image(tr, Rg.ravel(), Pg.ravel(), e, 1, PHYS["beta_scale"])
        X, Y = im["X"].reshape(Rg.shape), im["Y"].reshape(Rg.shape)
        Pp = X[..., None] * Rv + Y[..., None] * Up - cfg.get("secondary_push_rs", LENS["secondary_push_rs"]) * o
        return Pp, im["ok"].reshape(Rg.shape), np.stack([X, Y], -1)

    Pd, okd, _ = direct_pos()
    Ps, oks, XYs = secondary_pos()
    hw = r_out + 2
    Nm = 600
    mask = direct_mask(tr, e, hw, Nm, r_in, r_out)

    def covered(xy):
        i = np.clip(((hw - xy[..., 1]) / (2 * hw) * (Nm - 1)).round().astype(int), 0, Nm - 1)
        j = np.clip(((xy[..., 0] + hw) / (2 * hw) * (Nm - 1)).round().astype(int), 0, Nm - 1)
        return mask[i, j]

    nb = len(edges) - 1
    flow = [[] for _ in range(nb)]
    for P, ok, which in ((Pd, okd, 0), (Ps, oks, 1)):
        for i in range(len(rows) - 1):
            k = band_of_row[i]
            for m in range(M):
                quad = [(i, m), (i, m + 1), (i + 1, m + 1), (i + 1, m)]
                if not all(ok[a, b] for a, b in quad):
                    continue
                if which == 1:
                    c = XYs[i:i + 2, m:m + 2].reshape(-1, 2).mean(0)
                    if covered(c[None])[0]:
                        continue
                    # quad degenerado/esticado demais (fótons que quase dão a volta): fora
                    pts = np.array([XYs[a, b] for a, b in quad])
                    if np.ptp(pts, axis=0).max() > 3.0:
                        continue
                flow[k].append(([P[a, b] for a, b in quad], [(u_flow[a, b], v_flow[a, b]) for a, b in quad]))
    # Doppler: malha mais grossa (o Doppler é liso), UV parada no referencial da câmera
    Md = LENS["overlay_psi_segments"] if not small else max(16, cfg["psi_segments"] // 2)
    gi = int(np.argmin([abs(e - x) for x in LENS["doppler_groups_e"]]))
    dop = [[] for _ in range(nb)]
    step = max(1, M // Md)
    for which, P, ok in ((0, Pd, okd), (1, Ps, oks)):
        x0, w = REGIONS[("dop", gi, which)]
        Wt = LENS["static_tex"][0]
        for i in range(len(rows) - 1):
            k = band_of_row[i]
            for m in range(0, M, step):
                m2 = min(m + step, M)
                quad = [(i, m), (i, m2), (i + 1, m2), (i + 1, m)]
                if not all(ok[a, b] for a, b in quad):
                    continue
                if which == 1:
                    c = XYs[i:i + 2, m:m2 + 1:max(1, m2 - m)].reshape(-1, 2).mean(0)
                    if covered(c[None])[0]:
                        continue
                    pts = np.array([XYs[a, b] for a, b in quad])
                    if np.ptp(pts, axis=0).max() > 3.0 * step:
                        continue
                uv = [((x0 + b / M * w) / Wt, v_flow[a, b]) for a, b in quad]  # coluna m ↔ x = −1 + 2m/M
                dop[k].append(([P[a, b] for a, b in quad], uv))
    # sombra (disco no plano do céu) e anel + halo
    Wt = LENS["static_tex"][0]
    xb, wb = REGIONS["black"]
    ub = (xb + wb / 2) / Wt
    na = 48
    ang = np.linspace(0, 2 * math.pi, na + 1)
    circ = lambda rad: [rad * math.cos(a) * Rv + rad * math.sin(a) * Up for a in ang]  # noqa: E731
    shadow = []
    edge = circ(BC)
    for a in range(na):
        tri = [np.zeros(3), edge[a + 1], edge[a]]
        shadow.append((tri + [tri[-1]], [(ub, 0.25)] * 4))
        shadow.append(([tri[0], tri[2], tri[1], tri[1]], [(ub, 0.25)] * 4))  # as duas faces (alphatest tem culling)
    xr, wr = REGIONS["ring"]
    ring = []
    ring_b = [BC, BC + 0.07, BC + 0.3, BC + 1.2, LENS["halo_out_rs"]]
    if small:
        ring_b = ring_b[:4]
    for j in range(len(ring_b) - 1):
        c0, c1 = circ(ring_b[j]), circ(ring_b[j + 1])
        v0 = 0.5 * (ring_b[j] - BC) / (LENS["halo_out_rs"] - BC)
        v1 = 0.5 * (ring_b[j + 1] - BC) / (LENS["halo_out_rs"] - BC)
        for a in range(na):
            pos = [c0[a], c0[a + 1], c1[a + 1], c1[a]]
            uu = [(xr + (a / na) * wr) / Wt, (xr + ((a + 1) / na) * wr) / Wt]
            ring.append(([p - 0.01 * o for p in pos], [(uu[0], v0), (uu[1], v0), (uu[1], v1), (uu[0], v1)]))
    return {"flow": flow, "dop": dop, "shadow": shadow, "ring": ring}


REGIONS = {}


# ------------------------------------------------------------------ JSON de geometria


def mesh_json(quads):
    """Lista de (4 posições (R,U,B), 4 uvs) → poly_mesh compacto (vértices compartilhados por chave)."""
    pos, uvs, polys = [], [], []
    pidx, uidx = {}, {}
    for P4, UV4 in quads:
        poly = []
        for p, uv in zip(P4, UV4):
            m = model(np.asarray(p, float))
            kp = tuple(round(float(x), 2) for x in m)
            ku = (round(float(uv[0]), 5), round(float(uv[1]), 5))
            if kp not in pidx:
                pidx[kp] = len(pos)
                pos.append(list(kp))
            if ku not in uidx:
                uidx[ku] = len(uvs)
                uvs.append(list(ku))
            poly.append([pidx[kp], 0, uidx[ku]])
        polys.append(poly)
    return {"normalized_uvs": True, "positions": pos, "normals": [[0, 0, -1]], "uvs": uvs, "polys": polys}


def geometry(ident, bins, part, bands=None, bounds=130):
    """Um arquivo de geometria: osso 'face' (vira para a câmera) com um osso por bin (e por anel)."""
    bones = [{"name": "root", "pivot": [0, 0, 0]}, {"name": "face", "parent": "root", "pivot": [0, 0, 0]}]
    for j, b in enumerate(bins):
        if bands is None:
            q = b[part]
            if q:
                bones.append({"name": f"{part[0]}{j}", "parent": "face", "pivot": [0, 0, 0], "poly_mesh": mesh_json(q)})
        else:
            for k in bands:
                q = b[part][k]
                if q:
                    bones.append({"name": f"{part[0]}{j}_{k}", "parent": "face", "pivot": [0, 0, 0], "poly_mesh": mesh_json(q)})
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": ident, "texture_width": 16, "texture_height": 16,
                        "visible_bounds_width": bounds, "visible_bounds_height": bounds, "visible_bounds_offset": [0, 0, 0]},
        "bones": bones}]}


def core_geometry(ident, bins, nb, bounds=130):
    """Sombra (s), anel+halo (p) e Doppler (o, por anel) num arquivo só (um render controller, textura parada)."""
    bones = [{"name": "root", "pivot": [0, 0, 0]}, {"name": "face", "parent": "root", "pivot": [0, 0, 0]}]
    for j, b in enumerate(bins):
        bones.append({"name": f"s{j}", "parent": "face", "pivot": [0, 0, 0], "poly_mesh": mesh_json(b["shadow"])})
    for j, b in enumerate(bins):
        bones.append({"name": f"p{j}", "parent": "face", "pivot": [0, 0, 0], "poly_mesh": mesh_json(b["ring"])})
        for k in range(nb):
            if b["dop"][k]:
                bones.append({"name": f"o{j}_{k}", "parent": "face", "pivot": [0, 0, 0], "poly_mesh": mesh_json(b["dop"][k])})
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": ident, "texture_width": 16, "texture_height": 16,
                        "visible_bounds_width": bounds, "visible_bounds_height": bounds, "visible_bounds_offset": [0, 0, 0]},
        "bones": bones}]}


# ------------------------------------------------------------------ prévia (rasterizador numpy)


def _tri_raster(img, zbuf, P2, Z, UV, tex, mode, offset=0.0):
    """Um triângulo: P2 (3, 2) pixels, Z (3,) profundidade, UV (3, 2). mode 'add' soma (se na frente da sombra),
    'depth' escreve a profundidade da sombra."""
    H, W = zbuf.shape
    x0, y0 = np.floor(P2.min(0)).astype(int)
    x1, y1 = np.ceil(P2.max(0)).astype(int)
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W - 1), min(y1, H - 1)
    if x1 < x0 or y1 < y0:
        return
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    (ax, ay), (bx, by), (cx, cy) = P2
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-9:
        return
    w0 = ((by - cy) * (xs + 0.5 - cx) + (cx - bx) * (ys + 0.5 - cy)) / den
    w1 = ((cy - ay) * (xs + 0.5 - cx) + (ax - cx) * (ys + 0.5 - cy)) / den
    w2 = 1 - w0 - w1
    inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    if not inside.any():
        return
    z = w0 * Z[0] + w1 * Z[1] + w2 * Z[2]
    yy, xx = ys[inside], xs[inside]
    zz = z[inside]
    if mode == "depth":
        zbuf[yy, xx] = np.minimum(zbuf[yy, xx], zz)
        return
    vis = zz < zbuf[yy, xx] - 1e-3
    if not vis.any():
        return
    u = (w0 * UV[0, 0] + w1 * UV[1, 0] + w2 * UV[2, 0])[inside][vis]
    v = (w0 * UV[0, 1] + w1 * UV[1, 1] + w2 * UV[2, 1])[inside][vis]
    th, tw = tex.shape[:2]
    ti = np.clip((v * th).astype(int), 0, th - 1)
    tj = ((u + offset) % 1.0 * tw).astype(int) % tw
    img[yy[vis], xx[vis]] += tex[ti, tj]


def preview(geoms, flow_tex, static_tex, e, j, D_blocks=84.0, rs_blocks=2.8, size=(640, 360), fov=60.0, t=20.0,
            band_on=None, below=False, edges=None):
    """O que a câmera vê: camadas somadas, a sombra cobrindo o que está atrás dela (como no jogo)."""
    W, H = size
    img = np.zeros((H, W, 3))
    zbuf = np.full((H, W), np.inf)
    o, Rv, Up = LZ.frame(e)
    D = D_blocks / rs_blocks
    C = D * o
    fpx = (H / 2) / math.tan(math.radians(fov) / 2)

    def proj(pm):
        p = np.stack([pm[:, 0] / 16, pm[:, 1] / 16, -pm[:, 2] / 16], -1)
        if below:
            p[:, 1] *= -1
        oo = o.copy()
        if below:
            oo = np.array([o[0], -o[1], o[2]])
            up = np.array([Up[0], -Up[1], Up[2]])
            Cc = D * oo
        else:
            up, Cc = Up, C
        d = p - Cc
        depth = d @ (-oo)
        sx = (d @ Rv) / depth
        sy = (d @ (up if not below else -up)) / depth
        return np.stack([W / 2 + sx * fpx, H / 2 - sy * fpx], -1), depth

    def draw(mesh, tex, mode, offset=0.0):
        if not mesh["polys"]:
            return
        pos = np.array(mesh["positions"], float)
        uv = np.array(mesh["uvs"], float)
        P2, Z = proj(pos)
        for poly in mesh["polys"]:
            pi = [q[0] for q in poly]
            ui = [q[2] for q in poly]
            for tri in ((0, 1, 2), (0, 2, 3)):
                a = [pi[x] for x in tri]
                if len(set(a)) < 3:
                    continue
                _tri_raster(img, zbuf, P2[a], Z[a], uv[[ui[x] for x in tri]], tex, mode, offset)

    core = {bn["name"]: bn for bn in geoms["core"]["minecraft:geometry"][0]["bones"] if "poly_mesh" in bn}
    draw(core[f"s{j}"]["poly_mesh"], static_tex, "depth")
    edges = edges or LENS["band_edges_rs"]
    nb = len(edges) - 1
    omega = omegas(edges)
    for k in range(nb):
        if band_on is not None and not band_on[k]:
            continue
        bones = {bn["name"]: bn for bn in geoms[f"flow{k}"]["minecraft:geometry"][0]["bones"] if "poly_mesh" in bn}
        if f"f{j}_{k}" in bones:
            draw(bones[f"f{j}_{k}"]["poly_mesh"], flow_tex, "add", offset=-omega[k] * t / 360.0)
        if f"o{j}_{k}" in core:
            draw(core[f"o{j}_{k}"]["poly_mesh"], static_tex, "add")
    draw(core[f"p{j}"]["poly_mesh"], static_tex, "add")
    return np.clip(img, 0, 1)


def omegas(edges):
    """ω de Kepler (°/s) no meio de cada anel: ω_in · (r/r_in)^(−3/2) (spec/layout.json → disk)."""
    w_in = LAYOUT["disk"].get("omega_in_deg_s", 90)
    r_in = edges[0]
    return [w_in * (((edges[k] + edges[k + 1]) / 2) / r_in) ** -1.5 for k in range(len(edges) - 1)]


# ------------------------------------------------------------------ Molang


EASE_MOLANG = {
    "linear": "({u})",
    "inQuad": "({u}) * ({u})",
    "outQuad": "(1 - (1 - ({u})) * (1 - ({u})))",
    "inCubic": "math.pow({u}, 3)",
    "outCubic": "(1 - math.pow(1 - ({u}), 3))",
    "inExpo": "(({u}) <= 0 ? 0 : math.pow(2, 10 * ({u}) - 10))",
    "outExpo": "(({u}) >= 1 ? 1 : 1 - math.pow(2, -10 * ({u})))",
}


def curve_molang(keys, field, x="v.tk"):
    """Curva por keyframes (a mesma convenção do easing.js: o ease do keyframe diz como se CHEGA nele) → uma
    expressão Molang de ternários aninhados em x (ticks)."""
    expr = f"{keys[-1][field]}"
    for i in range(len(keys) - 1, 0, -1):
        p, k = keys[i - 1], keys[i]
        span = k["t"] - p["t"]
        u = f"(({x}) - {p['t']}) / {span}" if span > 0 else "1"
        e = EASE_MOLANG[k.get("ease", "linear")].format(u=u)
        seg = f"{p[field]} + ({k[field] - p[field]}) * {e}"
        expr = f"(({x}) <= {k['t']}) ? ({seg}) : ({expr})"
    return f"(({x}) <= {keys[0]['t']}) ? ({keys[0][field]}) : ({expr})"


def scale_molang():
    """escala(t) do buraco final × ringdown (layout.json → black_hole), em v.tk; 0 antes do 240."""
    keys = LAYOUT["black_hole"]["scale_curve"]
    ring = "((v.tk >= 241 && v.tk <= 279) ? 1 + 0.15 * math.exp(-(v.tk - 241) / 10) * math.sin(360 * (v.tk - 241) / 12) : 1)"
    return f"(v.tk < 240 ? 0 : ({curve_molang(keys, 's')}) * {ring})"


def orbit_molang():
    """A (side 1) e B (side 2) na órbita do binary_math.js, no plano (R, F) do layout. Linhas de pré-animação que
    deixam o deslocamento no mundo em v.wx, v.wz (blocos). F vem da propriedade singularity:fyaw (graus, a mesma
    convenção do yaw do MC: 0 = +Z, 90 = −X)."""
    mA, mB = 36, 29
    d0 = LAYOUT["binary"]["d0"]
    return [
        "v.tau = math.max((240 - v.tk) / 20, 0.000001);",
        f"v.d = {d0} * math.pow(v.tau / 9, 0.25);",
        "v.ph = 360 * (35 / 48) * math.pow(9, 0.375) * 1.6 * (math.pow(9, 0.625) - math.pow(v.tau, 0.625));",
        f"v.a = v.side == 1 ? -{mB / (mA + mB):.8f} * v.d : {mA / (mA + mB):.8f} * v.d;",
        "v.fy = q.property('singularity:fyaw');",
        # offset = a·(cos φ·R + sin φ·F); F = (−sin fy, 0, cos fy), R = F × U = (−cos fy, 0, −sin fy)
        "v.wx = v.a * (-math.cos(v.ph) * math.cos(v.fy) - math.sin(v.ph) * math.sin(v.fy));",
        "v.wz = v.a * (-math.cos(v.ph) * math.sin(v.fy) + math.sin(v.ph) * math.cos(v.fy));",
    ]


# ------------------------------------------------------------------ pacote


def ignite_s(k, nb, small=False):
    """Segundos de filme em que o anel k (0 = interno) acende: de fora para dentro (layout.json → ignite_ticks)."""
    if small:
        return 0.0
    ig = LAYOUT["disk"]["ignite_ticks"]
    return ig[f"ring{k + 1}"] / 20


def entity_files(kind, nbins, nb, omegas_k, rs_blocks):
    """BP + client entity + render controllers + animação de uma das duas entidades ('bh' ou 'bhs')."""
    small = kind == "bhs"
    ident = f"{NS}:sgx_bh_small" if small else f"{NS}:sgx_bh"
    fv = PROJECT["bedrock"]["format_versions"]
    props = {
        f"{NS}:t0": {"type": "float", "range": [0.0, 60.0], "default": 0.0, "client_sync": True},
        f"{NS}:bin": {"type": "int", "range": [-31, 31], "default": 0, "client_sync": True},
        f"{NS}:cal": {"type": "int", "range": [0, 3], "default": 0, "client_sync": True},
    }
    if small:
        props[f"{NS}:side"] = {"type": "int", "range": [1, 2], "default": 1, "client_sync": True}
        props[f"{NS}:fyaw"] = {"type": "float", "range": [-360.0, 360.0], "default": 0.0, "client_sync": True}
    inert = json.loads((ROOT / "BP/entities/sgx_disk.json").read_text(encoding="utf-8"))["minecraft:entity"]["components"]
    bp = {"format_version": fv["entity_bp"], "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": False, "is_summonable": True, "is_experimental": False,
                        "properties": props},
        "components": inert}}
    # pré-animação: o tempo do filme liso por quadro (o creeper carregado usa o mesmo frame_alpha)
    default_bin = int(np.argmin([abs(e - 7.5) for e in (LENS["small"] if small else LENS)["bins_e_deg"]]))
    pre = [
        "v.t = q.property('singularity:t0') + (math.floor(q.life_time * 20) + q.frame_alpha) / 20;",
        "v.tk = v.t * 20;",
        f"v.bi = q.property('singularity:bin') == 0 ? {default_bin} : math.abs(q.property('singularity:bin')) - 1;",
        "v.below = q.property('singularity:bin') < 0;",
        "v.cal = q.property('singularity:cal');",
        "v.yaw = q.rotation_to_camera(1) - q.body_y_rotation + (math.mod(v.cal, 2) >= 1 ? 180 : 0);",
        "v.ys = math.mod(math.floor(v.cal / 2), 2) >= 1 ? -1 : 1;",
    ]
    if small:
        pre += [
            "v.side = q.property('singularity:side');",
            "v.born = v.side == 1 ? 20 : 40;",
            "v.g = math.clamp((v.tk - v.born - 6) / 12, 0, 1);",
            "v.grow = v.tk < v.born ? 0 : (v.g >= 1 ? 1 : 0.08 + 0.92 * (1 - math.pow(2, -10 * v.g)));",
            f"v.rs = v.side == 1 ? {LAYOUT['black_hole']['shadow_A'] / BC:.5f} : {LAYOUT['black_hole']['shadow_B'] / BC:.5f};",
            "v.sc = v.tk >= 240 ? 0 : v.rs * v.grow;",
            "v.on = v.tk >= v.born && v.tk < 240;",
        ] + orbit_molang()
    else:
        pre += [
            f"v.sc = {rs_blocks} * {scale_molang()};",
            "v.on = v.tk >= 240 && v.tk < 700;",
        ]
    pre.append("v.disk_off = " + ("!v.on;" if small else "v.tk >= 620;"))
    anim_name = f"animation.{NS}.sgx_{kind}.face"
    bones = {"face": {"rotation": [0, "v.yaw", 0], "scale": ["v.sc", "v.sc * (v.below ? -1 : 1)", "v.sc"]}}
    if small:
        # mundo → modelo com o corpo em 0: x igual, z espelhado (o −Z do modelo, a "cara", olha para +Z)
        bones["root"] = {"position": ["16 * v.wx", 0, "-16 * v.wz"]}
    anim = {"format_version": fv["animations"], "animations": {anim_name: {"loop": True, "bones": bones}}}
    geos = {f"flow{k}": f"geometry.{NS}.sgx_{kind}_flow{k}" for k in range(nb)}
    geos["core"] = f"geometry.{NS}.sgx_{kind}_core"
    rcs = {}
    core_rc = f"controller.render.{NS}.sgx_{kind}_core"
    vis = []
    for j in range(nbins):
        vis.append({f"s{j}": f"v.on && v.bi == {j}"})
        vis.append({f"p{j}": f"v.on && v.bi == {j}"})
        for k in range(nb):
            vis.append({f"o{j}_{k}": f"v.on && !v.disk_off && v.bi == {j} && v.t >= {ignite_s(k, nb, small)}"})
    rcs[core_rc] = {"geometry": "Geometry.core", "materials": [{"*": "Material.add"}, {"s*": "Material.shadow"}],
                    "textures": ["Texture.static"], "ignore_lighting": True, "part_visibility": vis}
    order = [core_rc]
    for k in range(nb):
        name = f"controller.render.{NS}.sgx_{kind}_flow{k}"
        # U anda para trás no tempo (o material em ψ chega de ψ − ωt) e compensa o giro da malha (v.yaw)
        rcs[name] = {"geometry": f"Geometry.flow{k}", "materials": [{"*": "Material.flow"}], "textures": ["Texture.flow"],
                     "ignore_lighting": True,
                     "uv_anim": {"offset": [f"v.ys * v.yaw / 360 - {omegas_k[k] / 360:.6f} * v.t", 0.0], "scale": [1.0, 1.0]},
                     "part_visibility": [{f"f{j}_{k}": f"v.on && !v.disk_off && v.bi == {j} && v.t >= {ignite_s(k, nb, small)}"}
                                         for j in range(nbins)]}
        order.append(name)
    client = {"format_version": fv["client_entity"], "minecraft:client_entity": {"description": {
        "identifier": ident,
        "materials": {"add": "charged_creeper", "flow": "charged_creeper", "shadow": "entity_alphatest"},
        "textures": {"flow": "textures/sgx/bh/flow", "static": "textures/sgx/bh/static"},
        "geometry": geos,
        "animations": {"face": anim_name},
        "scripts": {"pre_animation": pre, "animate": ["face"]},
        "render_controllers": order}}}
    rc = {"format_version": fv["render_controllers"], "render_controllers": rcs}
    return bp, client, rc, anim


def stamp():
    h = hashlib.sha256()
    for f in ("spec/bake.json", "spec/layout.json", "spec/palette.json", "spec/project.json", "tools/bake/bh_engine.py",
              "tools/bake/bh_lens.py", "tools/bake/bh_model.py"):
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()


OUTPUTS = []  # caminhos relativos gerados (o cache espelha)


def put(rel, data):
    p = CACHE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, (dict, list)):
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    else:
        save_png(data, p)
    OUTPUTS.append(rel)


def build():
    t0 = __import__("time").time()
    tr = E.Tracer(PHYS)
    flow = flow_texture()
    static, regions = static_texture(tr)
    REGIONS.clear()
    REGIONS.update(regions)
    put("RP/textures/sgx/bh/flow.png", flow)
    put("RP/textures/sgx/bh/static.png", static)
    sheets = []
    for kind, cfg in (("bh", LENS), ("bhs", {**LENS["small"], "secondary_push_rs": LENS["secondary_push_rs"]})):
        small = kind == "bhs"
        bins = [lens_bin(tr, e, cfg, small) for e in cfg["bins_e_deg"]]
        nb = len(cfg["band_edges_rs"]) - 1
        geoms = {f"flow{k}": geometry(f"geometry.{NS}.sgx_{kind}_flow{k}", bins, "flow", bands=[k],
                                       bounds=60 if small else 130) for k in range(nb)}
        geoms["core"] = core_geometry(f"geometry.{NS}.sgx_{kind}_core", bins, nb, bounds=60 if small else 130)
        for name, g in geoms.items():
            put(f"RP/models/entity/sgx_{kind}_{name}.geo.json", g)
        om = omegas(cfg["band_edges_rs"])
        rs = LAYOUT["black_hole"]["r_s_final"]
        bp, client, rc, anim = entity_files(kind, len(bins), nb, om, rs)
        ent = "sgx_bh_small" if small else "sgx_bh"
        put(f"BP/entities/{ent}.json", bp)
        put(f"RP/entity/{ent}.entity.json", client)
        put(f"RP/render_controllers/{ent}.render_controllers.json", rc)
        put(f"RP/animations/{ent}.animation.json", anim)
        if not small:
            for j, e in enumerate(cfg["bins_e_deg"]):
                if e in (3, 7.5, 14, 25, 36, 46):
                    sheets.append((f"e = {e}°", preview(geoms, flow, static, e, j, size=(640, 360), t=7.0)))
            # a ignição (de fora para dentro) e o disco girando, num bin só
            j = cfg["bins_e_deg"].index(9.5)
            for tk, lab in ((240, "240 sem disco"), (283, "283 anel 5"), (295, "295 anéis 3–5"), (320, "320 + 1 s")):
                on = [tk / 20 >= ignite_s(k, nb) for k in range(nb)]
                sheets.append((lab, preview(geoms, flow, static, 9.5, j, size=(640, 360), t=tk / 20, band_on=on)))
        else:
            for j, e in enumerate(cfg["bins_e_deg"][:2]):
                sheets.append((f"A/B e = {e}°", preview(geoms, flow, static, e, j, D_blocks=40, rs_blocks=1.63,
                                                         size=(640, 360), t=3.0, edges=cfg["band_edges_rs"])))
    # folha de contato da prévia
    cols = 3
    rows = (len(sheets) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols, 360 * rows), (5, 7, 15))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(str(ROOT / "assets/fonts/IBMPlexMono-SemiBold-full.ttf"), 20)
    except OSError:
        f = None
    for i, (lab, img) in enumerate(sheets):
        bg = np.array([5, 7, 15]) / 255
        im = np.clip(bg + img, 0, 1)
        sheet.paste(Image.fromarray((im * 255).astype(np.uint8)), ((i % cols) * 640, (i // cols) * 360))
        d.text(((i % cols) * 640 + 10, (i // cols) * 360 + 8), lab, fill=(180, 200, 255), font=f)
    BUILD.mkdir(parents=True, exist_ok=True)
    sheet.save(BUILD / "lens_sheet.png")
    (CACHE / "outputs.json").write_text(json.dumps(OUTPUTS), encoding="utf-8")
    return __import__("time").time() - t0


def main():
    st = stamp()
    stamp_f = CACHE / "stamp"
    fresh = "--force" not in sys.argv and stamp_f.exists() and stamp_f.read_text() == st and (CACHE / "outputs.json").exists()
    if not fresh:
        if CACHE.exists():
            shutil.rmtree(CACHE)
        dt = build()
        stamp_f.write_text(st)
        how = f"gerado em {dt:.0f} s"
    else:
        how = "cache de build/bake/model"
    outs = json.loads((CACHE / "outputs.json").read_text(encoding="utf-8"))
    total = 0
    for rel in outs:
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CACHE / rel, dst)
        total += dst.stat().st_size
    print(f"✓ buraco negro em geometria: {len(outs)} arquivos ({total / 1e6:.1f} MB), {how} · prévia em build/bake/lens_sheet.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
