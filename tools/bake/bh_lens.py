#!/usr/bin/env python3
"""A lente como MAPA de malha (v0.3.1, T-25): para cada ponto do disco (r, ψ), onde ele aparece na tela.

O bh_engine.py traça do pixel para o disco (bom para imagem). Aqui é o caminho inverso, que é o que a geometria
precisa: o vértice (r, ψ) do disco vai para a posição (X, Y) da sua imagem no plano do céu (o "plano b", que passa
por O de frente para a câmera), para a imagem direta (k = 0) e a secundária (k = 1, a luz que dá a volta por baixo).
É o mesmo que os vídeos da NASA mostram com o disco xadrez: a malha do disco dobrada pela lente.

Geometria (unidades de r_s):
- ô = de O para a câmera, elevação e acima do plano do disco. Na tela: R = direita (horizontal), U' = cima.
- Ponto do disco p̂ = cos ψ·R + sin ψ·F_h (F_h = horizontal para longe da câmera; ψ cresce no sentido anti-horário
  visto de cima, que é o sentido do giro do disco). ψ = −90° é o ponto mais perto da câmera.
- O fóton varre o ângulo φ no plano (ô, p̂) desde o observador: φ = γ (k = 0) ou 2π − γ (k = 1), cos γ = p̂·ô.
- b sai da tabela de geodésicas (u(b, φ) = 1/r); a imagem fica em b·ê, ê = direção de p̂ ⊥ ô na tela (−ê no k = 1).
- g = √(1 − 1/r)·… /(1 − β·cos θ): o mesmo fator do bh_engine (β visual × beta_scale, teto 0,75)."""
import math

import numpy as np


def frame(e_deg):
    """Vetores da tela em coordenadas (R, U, B) da câmera (B = horizontal para a câmera)."""
    e = math.radians(e_deg)
    o = np.array([0.0, math.sin(e), math.cos(e)])           # O → câmera
    R = np.array([1.0, 0.0, 0.0])
    Up = np.array([0.0, math.cos(e), -math.sin(e)])          # cima na tela
    return o, R, Up


def disk_point(r, psi):
    """(R, U, B) do ponto do disco: F_h = −B."""
    return np.stack([r * np.cos(psi), np.zeros_like(r), -r * np.sin(psi)], axis=-1)


def solve_b(tr, phi, u_target, chunk=1500):
    """b tal que u(b, φ) = u_target na tabela do Tracer (u decresce com b: capturado → 1, fugiu → 0)."""
    bg = tr.b
    out = np.full(phi.shape, np.nan)
    flat_phi, flat_u = phi.ravel(), u_target.ravel()
    res = out.ravel()
    x = np.clip(flat_phi / tr.dphi, 0, tr.U.shape[1] - 1.001)
    i0 = x.astype(int)
    tp = (x - i0).astype(np.float32)
    for s in range(0, len(flat_phi), chunk):
        sl = slice(s, s + chunk)
        rows = tr.U[:, i0[sl]] * (1 - tp[sl]) + tr.U[:, i0[sl] + 1] * tp[sl]   # (Nb, n)
        below = rows < flat_u[sl][None, :]
        j = np.argmax(below, axis=0)                                          # primeiro b com u < alvo
        ok = below[j, np.arange(len(j))] & (j > 0)
        jj = np.maximum(j, 1)
        ua, ub = rows[jj - 1, np.arange(len(j))], rows[jj, np.arange(len(j))]
        t = np.clip((ua - flat_u[sl]) / np.maximum(ua - ub, 1e-9), 0, 1)
        res[sl] = np.where(ok, bg[jj - 1] + t * (bg[jj] - bg[jj - 1]), np.nan)
    return res.reshape(phi.shape)


def image(tr, r, psi, e_deg, k, beta_scale=1.0):
    """Imagem k (0 ou 1) dos pontos (r, ψ) vista com elevação e. Devolve dict com X, Y (plano b, r_s), z (profundidade
    do ponto real atrás de O, + = longe da câmera), g (fator de Doppler + gravitacional) e ok."""
    r = np.asarray(r, float)
    psi = np.asarray(psi, float)
    o, R, Up = frame(e_deg)
    p_hat = disk_point(np.ones_like(r), psi)
    cg = np.clip(p_hat @ o, -1, 1)
    gam = np.arccos(cg)
    perp = p_hat - cg[..., None] * o
    sg = np.maximum(np.linalg.norm(perp, axis=-1), 1e-9)
    e_hat = perp / sg[..., None]
    if k == 1:
        phi = 2 * math.pi - gam
        e_hat = -e_hat
    else:
        phi = gam
    b = solve_b(tr, phi, 1.0 / r)
    ok = np.isfinite(b)
    bb = np.where(ok, b, 0.0)
    X = bb * (e_hat @ R)
    Y = bb * (e_hat @ Up)
    # Doppler: direção do fóton na emissão (mesma conta do bh_engine.render)
    from bh_engine import lookup  # noqa: E402 (módulo irmão)
    u = 1.0 / r
    du = lookup(tr.W, tr.b, bb, phi, tr.dphi)
    cphi, sphi = np.cos(phi)[..., None], np.sin(phi)[..., None]
    ph = cphi * o + sphi * e_hat
    dr = -du / u ** 2
    tang = dr[..., None] * ph + r[..., None] * (-sphi * o + cphi * e_hat)
    k_hat = -tang / np.maximum(np.linalg.norm(tang, axis=-1, keepdims=True), 1e-12)
    n_hat = np.array([0.0, 1.0, 0.0])
    v_hat = np.cross(n_hat, p_hat)
    v_hat /= np.maximum(np.linalg.norm(v_hat, axis=-1, keepdims=True), 1e-12)
    beta = np.minimum(np.sqrt(0.5 / np.maximum(r - 1.0, 1e-3)) * beta_scale, 0.75)
    cos_t = np.sum(v_hat * k_hat, axis=-1)
    g = np.sqrt(np.clip(1 - 1.5 / r, 1e-4, 1)) / (1 - beta * cos_t)
    z = r * math.cos(math.radians(e_deg)) * np.sin(psi)
    return {"X": X, "Y": Y, "z": z, "g": g, "ok": ok, "b": bb}
