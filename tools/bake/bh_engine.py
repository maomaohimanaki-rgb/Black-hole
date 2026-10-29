#!/usr/bin/env python3
"""Motor de imagem do buraco negro (F3, docs/VISUAL_TECH.md §2). Traçado de raios de Schwarzschild, offline, numpy.

- Geodésica nula no plano da órbita: u'' = −u + (3/2)·u²  (u = r_s/r, φ = ângulo na órbita), RK4, uma tabela
  u(b, φ) para todos os parâmetros de impacto b de uma vez (b em unidades de r_s).
- Cada pixel do impostor: b = |(X, Y)| na tela, o plano da órbita é o da linha de visada com a direção do pixel.
  O fóton cruza o plano do disco em φ_k = φ₀ + kπ (k = 0, 1, 2: imagem direta, secundária e o anel de fótons);
  o primeiro cruzamento dentro do disco (3 r_s ≤ r ≤ r_out) vence. Capturado antes (u ≥ 1) → a sombra.
- Disco fino de Novikov–Thorne simplificado: T(r) ∝ r^(−3/4)·(1 − √(r_in/r))^(1/4), pico 9 000 K. Fator g
  (gravitacional + Doppler da órbita kepleriana, β = √(M/(r − 2M)) × beta_scale): brilho × g⁴, cor da
  temperatura × g, pela rampa de corpo negro de spec/palette.json. O lado que se aproxima fica mais claro e mais azul.
  Brilho ∝ T^lum_exponent (o T⁴ real apaga a borda externa; o expoente visual fica no spec).
- Turbulência fBm estática em (log r, ψ) e um bloom fino no anel de fótons.
- Tonemap 1 − e^(−1,15x) pela luminância (preserva o tom), gama 1,12 (VISUAL_TECH §2.2).
v0.3.0: assava o atlas do impostor (partícula). v0.3.1 (T-25): virou biblioteca (tabela de geodésicas, cor, ruído) do
bh_lens.py / bh_model.py, e o main() só desenha a referência por pixel em build/bake/reference.png."""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "spec/bake.json").read_text(encoding="utf-8"))
BUILD = ROOT / "build/bake"


# ------------------------------------------------------------------ geodésicas


def geodesic_table(b, phi_max, dphi):
    """u(φ) e u'(φ) para cada b, a partir do observador no infinito (u = 0, u' = 1/b).
    Devolve (u, du, phi_cap, phi_esc): ângulo de captura (u ≥ 1) e de fuga (u volta a 0)."""
    n = int(phi_max / dphi) + 1
    U = np.zeros((len(b), n), np.float32)
    W = np.zeros((len(b), n), np.float32)
    u = np.zeros(len(b))
    w = 1.0 / b
    cap = np.full(len(b), np.inf)
    esc = np.full(len(b), np.inf)
    alive = np.ones(len(b), bool)
    f = lambda u, w: (w, -u + 1.5 * u * u)  # noqa: E731
    for i in range(1, n):
        k1u, k1w = f(u, w)
        k2u, k2w = f(u + 0.5 * dphi * k1u, w + 0.5 * dphi * k1w)
        k3u, k3w = f(u + 0.5 * dphi * k2u, w + 0.5 * dphi * k2w)
        k4u, k4w = f(u + dphi * k3u, w + dphi * k3w)
        u = np.where(alive, u + dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u), u)
        w = np.where(alive, w + dphi / 6 * (k1w + 2 * k2w + 2 * k3w + k4w), w)
        phi = i * dphi
        newcap = alive & (u >= 1.0)
        cap[newcap] = phi
        newesc = alive & (u <= 0.0) & (phi > 0.1)
        esc[newesc] = phi
        alive &= ~(newcap | newesc)
        U[:, i] = np.clip(u, 0, 1)
        W[:, i] = w
    return U, W, cap, esc


def lookup(table, bgrid, b, phi, dphi):
    """Interpolação bilinear em (b, φ)."""
    j = np.clip(np.searchsorted(bgrid, b) - 1, 0, len(bgrid) - 2)
    tb = np.clip((b - bgrid[j]) / (bgrid[j + 1] - bgrid[j]), 0, 1)
    x = np.clip(phi / dphi, 0, table.shape[1] - 1.001)
    i = x.astype(int)
    tp = x - i
    v00, v01 = table[j, i], table[j, i + 1]
    v10, v11 = table[j + 1, i], table[j + 1, i + 1]
    return (v00 * (1 - tp) + v01 * tp) * (1 - tb) + (v10 * (1 - tp) + v11 * tp) * tb


# ------------------------------------------------------------------ cor


PALETTE = json.loads((ROOT / "spec/palette.json").read_text(encoding="utf-8"))


def _hex_lin(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]) ** 2.2


# v0.3.0: a cor do disco é a rampa de spec/palette.json (a mesma do STORYBOARD "Cor"), interpolada em linear.
# A rampa de Helland pura com o pico a 9 000 K deixava o disco quase todo bege-acinzentado.
_DT = PALETTE["disk_temperature"]
_STOPS = sorted([(float(k[:-1]), _hex_lin(v)) for k, v in _DT.items() if k.endswith("K")])
_STOPS = [(1000.0, _hex_lin("#5A1404"))] + _STOPS + [(16000.0, _hex_lin(_DT["approach_tint"]))]


def temp_rgb(T):
    """Temperatura (K) → RGB linear pela rampa da paleta (abaixo de 1 000 K e acima de 16 000 K, satura)."""
    ts = np.array([t for t, _ in _STOPS])
    cols = np.stack([c for _, c in _STOPS])
    t = np.clip(T, ts[0], ts[-1])
    return np.stack([np.interp(t, ts, cols[:, ch]) for ch in range(3)], axis=-1)


def fbm(x, y, octaves=5, seed=0):
    """Ruído de valor fractal suave (determinístico), para a turbulência do disco."""
    rng = np.random.default_rng(seed)
    out = np.zeros_like(x)
    amp, freq, tot = 1.0, 1.0, 0.0
    for _ in range(octaves):
        g = rng.standard_normal((64, 64))
        xi = (x * freq) % 64
        yi = (y * freq) % 64
        x0, y0 = xi.astype(int) % 64, yi.astype(int) % 64
        fx, fy = xi - x0, yi - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x1, y1 = (x0 + 1) % 64, (y0 + 1) % 64
        v = (g[y0, x0] * (1 - sx) + g[y0, x1] * sx) * (1 - sy) + (g[y1, x0] * (1 - sx) + g[y1, x1] * sx) * sy
        out += amp * v
        tot += amp
        amp *= 0.55
        freq *= 2.0
    return out / tot


# ------------------------------------------------------------------ render de um quadro


def half_width(cfg, kind):
    """Meia-largura do quadro em r_s (o jogo usa a mesma conta, via storyboard_data.js)."""
    return cfg["small_half_width_rs"] if kind in ("small", "bare") else cfg["half_width_rs"]


class Tracer:
    def __init__(self, cfg):
        self.cfg = cfg
        bc = 1.5 * math.sqrt(3)  # parâmetro de impacto crítico (2,598 r_s)
        self.b = np.unique(np.concatenate([np.linspace(0.04, bc - 0.3, 500), np.linspace(bc - 0.3, bc + 0.4, 1400),
                                           np.linspace(bc + 0.4, cfg["half_width_rs"] * 1.5, 900)]))
        self.dphi = 0.0025
        self.U, self.W, self.cap, self.esc = geodesic_table(self.b, 3 * math.pi + 0.6, self.dphi)

    def render(self, incl_deg, size, r_in, r_out, exposure, flip=False, small=False, bare=False):
        c = self.cfg
        hw = half_width(c, "small" if small or bare else "")
        ss = 2  # superamostragem
        N = size * ss
        X, Y = np.meshgrid(np.linspace(-hw, hw, N), np.linspace(hw, -hw, N))
        # v0.3.0: exatamente no plano do disco a imagem direta tem espessura zero (some e sobra só o anel do lado
        # de trás); o "90°" é assado a 88°, com a linha fina do disco de lado.
        i = math.radians(min(incl_deg, 88.0))
        n_hat = np.array([0.0, 0.0, 1.0])
        o_hat = np.array([math.sin(i), 0.0, math.cos(i)])        # do buraco ao observador
        xs = np.array([0.0, 1.0, 0.0])                            # tela: direita
        ys = np.array([-math.cos(i), 0.0, math.sin(i)])           # tela: cima
        b = np.hypot(X, Y) + 1e-9
        e = (X[..., None] * xs + Y[..., None] * ys) / b[..., None]
        on = o_hat @ n_hat
        en = e @ n_hat
        phi0 = np.arctan2(-on, en) % math.pi
        bcap = np.interp(b, self.b, self.cap, right=np.inf)
        besc = np.interp(b, self.b, self.esc, right=np.inf)
        rgb = np.zeros((N, N, 3))
        alpha = np.zeros((N, N))
        done = np.zeros((N, N), bool)
        direct = np.zeros((N, N), bool)
        for k in range(0 if bare else 3):  # 'bare': sem disco, só a sombra e o anel
            phik = phi0 + k * math.pi
            valid = ~done & (phik < bcap) & (phik < besc)
            u = lookup(self.U, self.b, b, phik, self.dphi)
            r = 1.0 / np.maximum(u, 1e-6)
            hit = valid & (r >= r_in) & (r <= r_out)
            if not hit.any():
                continue
            du = lookup(self.W, self.b, b, phik, self.dphi)
            cphi, sphi = np.cos(phik)[..., None], np.sin(phik)[..., None]
            p_hat = cphi * o_hat + sphi * e
            dr = -du / np.maximum(u, 1e-6) ** 2
            tang = dr[..., None] * p_hat + r[..., None] * (-sphi * o_hat + cphi * e)
            k_hat = -tang / np.linalg.norm(tang, axis=-1, keepdims=True)
            v_hat = np.cross(n_hat, p_hat)
            v_hat /= np.linalg.norm(v_hat, axis=-1, keepdims=True) + 1e-12
            # v0.3.0: β visual (beta_scale) para o Doppler ler no disco largo (o β real a 11 r_s é só 0,22)
            beta = np.minimum(np.sqrt(0.5 / np.maximum(r - 1.0, 1e-3)) * c.get("beta_scale", 1.0), 0.75)
            cos_t = np.sum(v_hat * k_hat, axis=-1)
            g = np.sqrt(np.clip(1 - 1.5 / r, 1e-4, 1)) / (1 - beta * cos_t)
            # temperatura de Novikov–Thorne simplificada, pico normalizado
            prof = r ** -0.75 * np.clip(1 - np.sqrt(r_in / r), 0, 1) ** 0.25
            rr = np.linspace(r_in, r_out, 2000)
            pmax = (rr ** -0.75 * np.clip(1 - np.sqrt(r_in / rr), 0, 1) ** 0.25).max()
            pout = r_out ** -0.75 * (1 - math.sqrt(r_in / r_out)) ** 0.25
            # v0.3.0: pico → t_peak, borda externa → t_edge (VISUAL_TECH §2.2), linear no perfil
            T = c["t_edge_k"] + (c["t_peak_k"] - c["t_edge_k"]) * np.clip((prof - pout) / (pmax - pout), 0, 1)
            psi = np.arctan2(p_hat[..., 1], p_hat[..., 0])
            turb = fbm(np.log(r) * 6.0, (psi / (2 * math.pi)) * 64.0 + np.log(r) * 9.0, 5, seed=11)
            turb = np.clip(0.78 + 0.42 * turb, 0.25, None)
            # v0.3.0: T⁴ de verdade apaga a borda (2 000 K = 0,2 % do pico); o expoente visual fica no spec
            lum = (T / c["t_peak_k"]) ** c.get("lum_exponent", 4.0) * g ** 4 * turb
            lum *= np.clip((r_out - r) / (0.15 * r_out), 0, 1)  # borda externa suave
            if small:
                lum *= 0.6
            col = temp_rgb(T * g) * lum[..., None] * exposure
            rgb[hit] = col[hit]
            alpha[hit] = 1.0
            done |= hit
            if k == 0:
                direct = hit.copy()
        shadow = ~done & np.isfinite(bcap)  # capturado sem bater no disco antes: a sombra
        rgb[shadow] = 0.0
        alpha[shadow] = 1.0
        # bloom fino em volta da sombra (o anel de fótons que o tonemap esmaga)
        # (só onde a frente do disco, a imagem direta, não passa por cima)
        ring = np.exp(-((b - 2.6) / 0.08) ** 2) * c["ring_glow"] * (~shadow) * (~direct)
        rgb += ring[..., None] * _hex_lin(PALETTE["photon_ring"]) * exposure
        alpha = np.maximum(alpha, np.clip(ring * 3, 0, 1))
        # tonemap + gama
        # v0.3.0: tonemap pela LUMINÂNCIA, preservando o tom (por canal, os três saturavam e o disco ficava branco)
        L = np.maximum(rgb.max(axis=-1), 1e-9)
        tm = 1 - np.exp(-1.15 * L)
        disp = (rgb * (tm / L)[..., None]) ** (1 / 2.2)  # linear → tela
        disp = np.clip(disp, 0, 1) ** (1 / 1.12)
        # alfa do disco pelo brilho (o fundo do céu aparece através do disco fraco)
        lum_disp = disp.max(axis=-1)
        a = np.where(shadow, 1.0, np.clip(np.maximum(alpha * np.clip(lum_disp * 2.2, 0, 1), ring * 3), 0, 1))
        img = np.concatenate([disp, a[..., None]], axis=-1)
        # reduz a superamostragem
        img = img.reshape(size, ss, size, ss, 4).mean(axis=(1, 3))
        if flip:
            img = img[::-1]
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def main():
    """Referência: o traçado por pixel em algumas elevações (build/bake/reference.png), para comparar com a prévia
    da geometria (bh_model.py). Desde a v0.3.1 nada daqui vai para o pacote (T-25: o buraco negro é malha)."""
    cfg = SPEC["physics"]
    BUILD.mkdir(parents=True, exist_ok=True)
    tr = Tracer(cfg)
    els = [3, 9.5, 19, 32]
    size = 384
    sheet = Image.new("RGBA", (size * len(els), size), (5, 7, 15, 255))
    for i, e in enumerate(els):
        img = tr.render(90 - e, size, cfg["r_in_rs"], cfg["r_out_rs"], cfg["exposure"])
        sheet.alpha_composite(Image.fromarray(img, "RGBA"), (i * size, 0))
    sheet.convert("RGB").save(BUILD / "reference.png")
    print("✓ build/bake/reference.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
