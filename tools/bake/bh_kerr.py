#!/usr/bin/env python3
"""Lente de KERR (v0.3.2, T-26): o buraco negro final gira. O remanescente do GW150914 tem spin χ ≈ 0,67, e a
Gargântua do *Interstellar* também é de Kerr. O usuário pediu "os Boyer–Lindquist todos".

Traçado para trás de raios nulos em coordenadas de Boyer–Lindquist (M = 1), no tempo de Mino λ, na forma de
segunda ordem, que não tem troca de sinal nos pontos de retorno (u = cos θ):
    r'' = 2r(r² + a² − aL) − (r − M)((L − a)² + Q)
    u'' = u(a² − Q − L² − 2a²u²)
    φ'  = −[a(r² + a² − aL)/Δ − a + L/(1 − u²)]     (sinal trocado: o raio anda para o passado)
com L = −α·sen θ_o e Q = β² + cos² θ_o (α² − a²), (α, β) no plano do observador (Bardeen). Os cruzamentos do
equador (u muda de sinal) dão (r, φ) da imagem direta (k = 0) e da secundária (k = 1). O mapa se inverte por
interpolação (disco → tela), que é o que a malha precisa. O fator g do disco kepleriano prógrado é exato:
g = 1/(u^t (1 − Ω·L)), com o Doppler visual (beta_scale, T-24) multiplicando Ω·L.

A sombra é a curva crítica analítica (órbitas esféricas de fótons). Com a → 0 tudo cai no Schwarzschild do
bh_lens.py (o teste confere). Unidades de saída em r_s (= 2M), iguais às do bh_lens.image."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "build/bake/kerr"
M = 1.0


def horizon(a):
    return M + math.sqrt(max(M * M - a * a, 0.0))


def radial_grid(n_core=320, n_in=60, n_out=150, b_lo=3.4, b_hi=8.8, b_max=34.0):
    """b (em M) denso perto da curva crítica (≈ 4–7 M), onde moram o anel de fótons e a imagem secundária."""
    return np.unique(np.concatenate([
        np.linspace(0.02, b_lo, n_in, endpoint=False),
        np.linspace(b_lo, b_hi, n_core, endpoint=False),
        np.geomspace(b_hi, b_max, n_out)]))


def integrate(a, e_deg, alpha, beta, r_obs=1000.0, h=0.008, max_steps=4000, r_stop=60.0):
    """Traça os raios (α, β) (M) para trás. Devolve as duas primeiras travessias do equador (r, φ; NaN se não
    houver), L e se foi capturado. φ começa em 0 no observador."""
    th_o = max(math.radians(90.0 - e_deg), 1e-3)  # inclinação a partir do eixo de spin (vertical)
    alpha = np.asarray(alpha, float).ravel()
    beta = np.asarray(beta, float).ravel()
    so, co = math.sin(th_o), math.cos(th_o)
    L = -alpha * so
    Q = beta ** 2 + co * co * (alpha ** 2 - a * a)
    n = alpha.size
    r = np.full(n, r_obs)
    # o observador está no infinito: em r_obs o raio de parâmetro (α, β) já está deslocado de α/(r sen θ) em φ e
    # de −β/r em θ (sem isso a imagem saía ~0,04 r_s fora, erro que cresce com r)
    u = np.cos(th_o - beta / r_obs)
    Rr = (r * r + a * a - a * L) ** 2 - (r * r - 2 * M * r + a * a) * ((L - a) ** 2 + Q)
    pr = -np.sqrt(np.maximum(Rr, 0))
    Uu = (1 - u * u) * (Q + a * a * u * u) - L * L * u * u
    pu = np.where(beta >= 0, 1.0, -1.0) * np.sqrt(np.maximum(Uu, 0))
    phi = alpha / (r_obs * so)
    rh = horizon(a)
    alive = np.ones(n, bool)
    ncross = np.zeros(n, int)
    cr = np.full((2, n), np.nan)
    cphi = np.full((2, n), np.nan)
    captured = np.zeros(n, bool)
    K = (L - a) ** 2 + Q
    def deriv(r, u, pr, pu, L, Q, K):
        D = r * r - 2 * M * r + a * a
        ar = 2 * r * (r * r + a * a - a * L) - (r - M) * K
        au = u * (a * a - Q - L * L - 2 * a * a * u * u)
        dphi = -(a * (r * r + a * a - a * L) / np.maximum(D, 1e-9) - a + L / np.maximum(1 - u * u, 1e-9))
        return pr, pu, ar, au, dphi

    for _ in range(max_steps):
        if not alive.any():
            break
        idx = np.nonzero(alive)[0]
        r0, u0, pr0, pu0, ph0 = r[idx], u[idx], pr[idx], pu[idx], phi[idx]
        C = (L[idx], Q[idx], K[idx])
        dl = h / np.maximum(r0, 1.0)  # passo ~ uniforme em log r longe do buraco
        k1 = deriv(r0, u0, pr0, pu0, *C)
        k2 = deriv(r0 + 0.5 * dl * k1[0], u0 + 0.5 * dl * k1[1], pr0 + 0.5 * dl * k1[2], pu0 + 0.5 * dl * k1[3], *C)
        k3 = deriv(r0 + 0.5 * dl * k2[0], u0 + 0.5 * dl * k2[1], pr0 + 0.5 * dl * k2[2], pu0 + 0.5 * dl * k2[3], *C)
        k4 = deriv(r0 + dl * k3[0], u0 + dl * k3[1], pr0 + dl * k3[2], pu0 + dl * k3[3], *C)
        r1 = r0 + dl / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        u1 = u0 + dl / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        pr1 = pr0 + dl / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        pu1 = pu0 + dl / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        ph1 = ph0 + dl / 6 * (k1[4] + 2 * k2[4] + 2 * k3[4] + k4[4])
        # projeta no vínculo (pr² = R(r), pu² = U(u)): a forma de 2ª ordem sozinha deriva (um raio de b = 3M
        # "quicava" em r ≈ 8M); o sinal vem da evolução, que é quem sabe dos pontos de retorno
        Li, Qi, Ki = C
        R1 = (r1 * r1 + a * a - a * Li) ** 2 - (r1 * r1 - 2 * M * r1 + a * a) * Ki
        U1 = (1 - u1 * u1) * (Qi + a * a * u1 * u1) - Li * Li * u1 * u1
        pr1 = np.where(pr1 >= 0, 1.0, -1.0) * np.sqrt(np.maximum(R1, 0))
        pu1 = np.where(pu1 >= 0, 1.0, -1.0) * np.sqrt(np.maximum(U1, 0))
        # travessia do equador: interpolação linear em u
        cross = (u0 * u1 < 0)
        if cross.any():
            t = np.where(cross, u0 / np.where(cross, u0 - u1, 1.0), 0.0)
            nc = ncross[idx]
            for c in (0, 1):
                sel = cross & (nc == c)
                if sel.any():
                    g = idx[sel]
                    cr[c, g] = r0[sel] + t[sel] * (r1[sel] - r0[sel])
                    cphi[c, g] = ph0[sel] + t[sel] * (ph1[sel] - ph0[sel])
            ncross[idx[cross]] += 1
        r[idx], u[idx], pr[idx], pu[idx], phi[idx] = r1, np.clip(u1, -1, 1), pr1, pu1, ph1
        cap = r1 < rh * 1.01
        captured[idx[cap]] = True
        done = cap | ((pr1 > 0) & (r1 > r_stop)) | (ncross[idx] >= 2)
        alive[idx[done]] = False
    return {"L": L, "r": cr, "phi": cphi, "captured": captured}


def trace(a, e_deg, n_ang=720, bgrid=None, **kw):
    """Leque polar de raios (b denso perto da curva crítica). Devolve α, β, L e as travessias."""
    bgrid = radial_grid() if bgrid is None else bgrid
    ang = np.linspace(0, 2 * math.pi, n_ang, endpoint=False)
    B, A = np.meshgrid(bgrid, ang, indexing="ij")
    alpha, beta = (B * np.cos(A)).ravel(), (B * np.sin(A)).ravel()
    d = integrate(a, e_deg, alpha, beta, **kw)
    d.update({"alpha": alpha, "beta": beta, "nb": len(bgrid), "na": n_ang})
    return d


def critical_curve(a, e_deg, n=360):
    """Borda da sombra (curva crítica) no plano do observador, em M. Para a → 0, o círculo de raio 3√3."""
    th_o = math.radians(90.0 - e_deg)
    so, co = math.sin(th_o), math.cos(th_o)
    if a < 1e-4:
        t = np.linspace(0, 2 * math.pi, n, endpoint=False)
        return 3 * math.sqrt(3) * np.cos(t), 3 * math.sqrt(3) * np.sin(t)
    r1 = 2 * M * (1 + math.cos(2 / 3 * math.acos(-a / M)))
    r2 = 2 * M * (1 + math.cos(2 / 3 * math.acos(a / M)))
    rr = np.linspace(r1, r2, 20000)
    lam = -(rr ** 3 - 3 * M * rr ** 2 + a * a * rr + a * a * M) / (a * (rr - M))
    eta = rr ** 3 * (4 * a * a * M - rr * (rr - 3 * M) ** 2) / (a * a * (rr - M) ** 2)
    al = -lam / so
    b2 = eta + a * a * co * co - lam * lam * (co / so) ** 2
    ok = b2 >= 0
    al, b = al[ok], np.sqrt(b2[ok])
    X = np.concatenate([al, al[::-1]])
    Y = np.concatenate([b, -b[::-1]])
    # reamostra por ângulo em volta do centro (a curva é estrelada em relação ao centroide)
    cx = X.mean()
    th = np.arctan2(Y, X - cx)
    o = np.argsort(th)
    th, X, Y = th[o], X[o], Y[o]
    t = np.linspace(-math.pi, math.pi, n, endpoint=False)
    rad = np.hypot(X - cx, Y)
    rad_i = np.interp(t, th, rad, period=2 * math.pi)
    return cx + rad_i * np.cos(t), rad_i * np.sin(t)


def g_factor(r_M, L, a, beta_scale=1.0):
    """g = 1/(u^t (1 − Ω L)) do disco kepleriano prógrado; o Doppler visual multiplica Ω·L (teto 0,75)."""
    sq = np.sqrt(r_M)
    Om = math.sqrt(M) / (r_M ** 1.5 + a * math.sqrt(M))
    ut = (r_M ** 1.5 + a * math.sqrt(M)) / (r_M ** 0.75 * np.sqrt(np.maximum(r_M ** 1.5 - 3 * M * sq + 2 * a * math.sqrt(M), 1e-9)))
    d = np.clip(beta_scale * Om * L, -0.9, 0.75)
    return 1.0 / (ut * (1 - d))


class KerrLens:
    """Mesma interface do bh_lens.image: image(r, ψ, k) em unidades de r_s."""

    def __init__(self, a, e_deg, r_in_rs, r_out_rs, beta_scale=1.0, n_ang=720, cache=True):
        self.a, self.e = a, e_deg
        self.beta_scale = beta_scale
        key = hashlib.sha1(json.dumps([a, e_deg, n_ang, 6]).encode()).hexdigest()[:16]
        f = CACHE / f"{key}.npz"
        if cache and f.exists():
            d = dict(np.load(f))
        else:
            d = trace(a, e_deg, n_ang=n_ang)
            if cache:
                CACHE.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(f, **{k: v for k, v in d.items() if isinstance(v, np.ndarray)})
        self.d = d
        self.interp = {}
        lo, hi = 2 * (r_in_rs - 0.6), 2 * (r_out_rs + 2.5)  # em M
        for k in (0, 1):
            r = d["r"][k]
            ph = d["phi"][k]
            ok = np.isfinite(r) & (r >= lo) & (r <= hi)
            # ψ do disco: o ponto mais perto da câmera (φ = 0) é ψ = −π/2; mesmo sentido (anti-horário de cima)
            psi = ph[ok] - math.pi / 2
            xd, yd = r[ok] * np.cos(psi), r[ok] * np.sin(psi)
            vals = np.stack([d["alpha"][ok], d["beta"][ok], d["L"][ok]], -1)
            self.interp[k] = LinearNDInterpolator(np.stack([xd, yd], -1), vals)

    def _disk_xy(self, al, be, k):
        d = integrate(self.a, self.e, al, be)
        r, ph = d["r"][k], d["phi"][k]
        psi = ph - math.pi / 2
        return r * np.cos(psi), r * np.sin(psi), d["L"]

    def image(self, r_rs, psi, k, refine=True, iters=6, tol=2e-4):
        """Chute pela interpolação do leque e, com refine, Newton com o raio exato de cada ponto (o leque sozinho
        errava até ~7 r_s nos piores pontos, onde a imagem comprime perto da sombra)."""
        shape = np.shape(r_rs)
        r_rs = np.asarray(r_rs, float).ravel()
        psi = np.asarray(psi, float).ravel()
        rM = 2 * r_rs
        xt, yt = rM * np.cos(psi), rM * np.sin(psi)
        v = self.interp[k](np.stack([xt, yt], -1))
        ok = np.all(np.isfinite(v), axis=-1)
        al = np.where(ok, v[:, 0], 0.0)
        be = np.where(ok, v[:, 1], 0.0)
        if refine and ok.any():
            idx = np.nonzero(ok)[0]
            A, Bv = al[idx], be[idx]
            conv = np.zeros(idx.size, bool)
            for _ in range(iters):
                dd = 1e-3
                x0, y0, _ = self._disk_xy(A, Bv, k)
                xa, ya, _ = self._disk_xy(A + dd, Bv, k)
                xb, yb, _ = self._disk_xy(A, Bv + dd, k)
                ex, ey = x0 - xt[idx], y0 - yt[idx]
                err = np.hypot(ex, ey)
                conv = np.isfinite(err) & (err < tol * (1 + rM[idx]))
                J11, J21 = (xa - x0) / dd, (ya - y0) / dd
                J12, J22 = (xb - x0) / dd, (yb - y0) / dd
                det = J11 * J22 - J12 * J21
                good = np.isfinite(det) & (np.abs(det) > 1e-12) & ~conv
                stepA = np.where(good, (J22 * ex - J12 * ey) / np.where(good, det, 1), 0)
                stepB = np.where(good, (-J21 * ex + J11 * ey) / np.where(good, det, 1), 0)
                # passo limitado (perto da curva crítica o mapa é muito íngreme)
                sc = np.minimum(1.0, 0.5 / np.maximum(np.hypot(stepA, stepB), 1e-12))
                A, Bv = A - stepA * sc, Bv - stepB * sc
                if conv.all():
                    break
            x0, y0, _ = self._disk_xy(A, Bv, k)
            err = np.hypot(x0 - xt[idx], y0 - yt[idx])
            fine = np.isfinite(err) & (err < 0.02 * (1 + rM[idx]))
            # onde o Newton não convergiu, o chute do leque erra até ~6 r_s (virava espinho na prévia): o ponto sai
            # (ok = False) e quem monta a malha preenche pelos vizinhos (imagem direta) ou descarta (secundária,
            # colada no anel de fótons, mais fina que um pixel)
            al[idx], be[idx] = A, Bv
            ok[idx] = fine
            self.last_refined = float(fine.mean())
        X = np.where(ok, al, 0.0) / 2   # → r_s
        Y = np.where(ok, be, 0.0) / 2
        so = math.sin(max(math.radians(90.0 - self.e), 1e-3))
        L = -al * so
        g = g_factor(rM, L, self.a, self.beta_scale)
        z = r_rs * math.cos(math.radians(self.e)) * np.sin(psi)
        out = {"X": X, "Y": Y, "z": z, "g": g, "ok": ok, "b": np.hypot(X, Y)}
        return {k2: v2.reshape(shape) for k2, v2 in out.items()}

    def shadow(self, n=96):
        X, Y = critical_curve(self.a, self.e, n)
        return X / 2, Y / 2  # r_s
