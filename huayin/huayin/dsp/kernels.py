"""Laços de amostra (o coração físico do motor), compilados com numba.

Guias de onda digitais (Smith, Välimäki, Karjalainen) só funcionam amostra a amostra:
a saída de agora depende da saída de um período atrás. Em Python puro isso custa
~1 µs por amostra; compilado, ~10–30 ns. Sem numba o motor continua funcionando,
só que bem mais lento (use HUAYIN_SEM_NUMBA=1 para forçar e testar).
"""
from __future__ import annotations

import math
import os

import numpy as np

TEM_NUMBA = False
if os.environ.get("HUAYIN_SEM_NUMBA") != "1":
    try:
        from numba import njit  # noqa: F811

        TEM_NUMBA = True
    except ImportError:  # pragma: no cover
        pass

if not TEM_NUMBA:
    def njit(*a, **k):  # noqa: F811 — substituto transparente
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


@njit(cache=True)
def _ler(buf, pos, n_buf):
    """Leitura fracionária com interpolação de Lagrange cúbica (pos pode ser negativo)."""
    ri = int(math.floor(pos))
    fr = pos - ri
    xm1 = buf[(ri - 1) % n_buf]
    x0 = buf[ri % n_buf]
    x1 = buf[(ri + 1) % n_buf]
    x2 = buf[(ri + 2) % n_buf]
    hm1 = -fr * (fr - 1.0) * (fr - 2.0) / 6.0
    h0 = (fr + 1.0) * (fr - 1.0) * (fr - 2.0) / 2.0
    h1 = -(fr + 1.0) * fr * (fr - 2.0) / 2.0
    h2 = (fr + 1.0) * fr * (fr - 1.0) / 6.0
    return hm1 * xm1 + h0 * x0 + h1 * x1 + h2 * x2


# --------------------------------------------------------------------------- corda dedilhada


@njit(cache=True)
def kernel_corda(exc, atraso, g1, p1, g2, p2, n_solta, ap_a, ap_m, n_buf, contato, limiar):
    """Corda de laço único (Karplus-Strong estendido / Välimäki 1996).

    exc     : excitação injetada nas primeiras amostras (forma do dedilhado)
    atraso  : comprimento da malha em amostras, por amostra (permite bend, vibrato, slide)
    g1,p1   : filtro de perda enquanto a corda soa;  g2,p2 depois de abafada (n >= n_solta)
    ap_a/m  : coeficiente e número de passa-tudos de dispersão (rigidez)
    contato : >0 liga um choque não linear (corda batendo no traste / na outra corda)
    """
    n = atraso.shape[0]
    out = np.zeros(n)
    buf = np.zeros(n_buf)
    m = max(ap_m, 1)
    ax = np.zeros(m)
    ay = np.zeros(m)
    lp = 0.0
    ne = exc.shape[0]
    for i in range(n):
        y = _ler(buf, i - atraso[i], n_buf)
        if i < n_solta:
            lp = g1 * (1.0 - p1) * y + p1 * lp
        else:
            lp = g2 * (1.0 - p2) * y + p2 * lp
        v = lp
        for k in range(ap_m):
            o = ap_a * v + ax[k] - ap_a * ay[k]
            ax[k] = v
            ay[k] = o
            v = o
        if contato > 0.0:
            # v1.0: choque unilateral suave — acima do limiar a onda é rebatida e perde energia,
            # o que gera o "chiado" do 绞弦 (cordas cruzadas) e do 煞音.
            if v > limiar:
                v = limiar + (v - limiar) * (1.0 - contato)
            elif v < -limiar:
                v = -limiar + (v + limiar) * (1.0 - contato)
        if i < ne:
            v += exc[i]
        buf[i % n_buf] = v
        out[i] = v
    return out


# --------------------------------------------------------------------------- corda friccionada


@njit(cache=True)
def kernel_arco(atraso, beta, vel_arco, forca, acopl, n_buf, p_ponte, g_ponte, g_pestana):
    """Corda friccionada (McIntyre–Schumacher–Woodhouse, forma de Smith/STK).

    A crina do arco alterna entre grudar e escorregar na corda (curva de atrito hiperbólica).
    Isso produz o movimento de Helmholtz e, de graça, os transientes de troca de arco.
    beta    : ponto do arco (fração a partir da ponte), por amostra — cresce quando o dedo encurta
              a corda, porque o arco fica parado e a parte que vibra diminui.
    vel_arco pode trocar de sinal: é a troca de direção do arco (换弓).
    forca (0–1) é a pressão do arco: pouca = som "assobiado", muita = áspero.
    acopl (0–1) é o arco encostado na corda: 0 = arco levantado, a corda soa livre e morre sozinha.
    """
    n = atraso.shape[0]
    out = np.zeros(n)
    bn = np.zeros(n_buf)  # lado da pestana (千斤)
    bp = np.zeros(n_buf)  # lado da ponte (码子)
    lp = 0.0
    for i in range(n):
        D = atraso[i]
        dn = D * (1.0 - beta[i])
        dp = D * beta[i]
        if dp < 2.2:
            dp = 2.2
        if dn < 2.2:
            dn = 2.2
        s_pest = _ler(bn, i - dn, n_buf)
        s_ponte = _ler(bp, i - dp, n_buf)
        lp = (1.0 - p_ponte) * s_ponte + p_ponte * lp
        refl_ponte = -g_ponte * lp
        refl_pest = -g_pestana * s_pest
        v_corda = refl_ponte + refl_pest
        dv = vel_arco[i] - v_corda
        incl = 5.0 - 4.0 * forca[i]
        t = abs(dv * incl) + 0.75
        f = t ** -4.0
        if f > 1.0:
            f = 1.0
        novo = dv * f * acopl[i]
        bn[i % n_buf] = refl_ponte + novo
        bp[i % n_buf] = refl_pest + novo
        out[i] = s_ponte
    return out


# --------------------------------------------------------------------------- flauta (jato de ar)


@njit(cache=True)
def kernel_flauta(atraso_tubo, razao_jato, sopro, p_refl, refl_jato, refl_fim, n_buf):
    """Flauta transversal (modelo de jato de Cook/STK).

    O jato de ar oscila sobre a borda do bocal; o atraso do jato (razao_jato × tubo) decide
    qual modo do tubo é alimentado. sopro já vem com ruído de respiração e vibrato.
    """
    n = atraso_tubo.shape[0]
    out = np.zeros(n)
    tubo = np.zeros(n_buf)
    jato = np.zeros(n_buf)
    lp = 0.0
    dx = 0.0
    dy = 0.0
    for i in range(n):
        D = atraso_tubo[i]
        s = _ler(tubo, i - D, n_buf)
        lp = (1.0 - p_refl) * s + p_refl * lp
        temp = -lp
        y = temp - dx + 0.995 * dy
        dx = temp
        dy = y
        temp = y
        pd = sopro[i] - refl_jato * temp
        jato[i % n_buf] = pd
        dj = D * razao_jato
        if dj < 2.2:
            dj = 2.2
        pd = _ler(jato, i - dj, n_buf)
        pd = pd * (pd * pd - 1.0)
        if pd > 1.0:
            pd = 1.0
        elif pd < -1.0:
            pd = -1.0
        pd = pd + refl_fim * temp
        tubo[i % n_buf] = pd
        out[i] = s
    return out


# --------------------------------------------------------------------------- palheta dupla


@njit(cache=True)
def kernel_palheta_conica(atraso, posicao, sopro, p_refl, g_refl, offset, incl, n_buf):
    """Palheta + tubo cônico (forma "Saxofony" de Cook/STK): duas linhas de atraso aproximam
    o cone. Base do suona (唢呐): palheta dupla de junco, tubo cônico de madeira e campana de cobre.
    """
    n = atraso.shape[0]
    out = np.zeros(n)
    d0 = np.zeros(n_buf)
    d1 = np.zeros(n_buf)
    lp = 0.0
    for i in range(n):
        D = atraso[i]
        a0 = D * (1.0 - posicao)
        a1 = D * posicao
        if a0 < 2.2:
            a0 = 2.2
        if a1 < 2.2:
            a1 = 2.2
        s0 = _ler(d0, i - a0, n_buf)
        s1 = _ler(d1, i - a1, n_buf)
        lp = (1.0 - p_refl) * s0 + p_refl * lp
        temp = -g_refl * lp
        ultimo = temp - s1
        pd = sopro[i] - ultimo
        r = offset + incl * pd
        if r > 1.0:
            r = 1.0
        elif r < -1.0:
            r = -1.0
        d1[i % n_buf] = temp
        d0[i % n_buf] = sopro[i] - pd * r - temp
        out[i] = ultimo
    return out


@njit(cache=True)
def kernel_palheta_cilindrica(atraso, sopro, p_refl, g_refl, offset, incl, n_buf):
    """Palheta + tubo cilíndrico (forma "Clarinet" de STK): quase só harmônicos ímpares.
    Base do guanzi (管子), de tubo cilíndrico e palheta dupla larga.
    """
    n = atraso.shape[0]
    out = np.zeros(n)
    d = np.zeros(n_buf)
    lp = 0.0
    for i in range(n):
        s = _ler(d, i - atraso[i], n_buf)
        lp = (1.0 - p_refl) * s + p_refl * lp
        pd = -g_refl * lp - sopro[i]
        r = offset + incl * pd
        if r > 1.0:
            r = 1.0
        elif r < -1.0:
            r = -1.0
        v = sopro[i] + pd * r
        d[i % n_buf] = v
        out[i] = s
    return out


# --------------------------------------------------------------------------- membrana do dizi


@njit(cache=True)
def kernel_membrana(p, sr, f_m, zeta, kappa, ganho):
    """Membrana 笛膜 (dimó) como oscilador de Duffing amortecido excitado pela pressão do tubo.

    Tsai (2003): as rugas da membrana reduzem a não linearidade e ela reforça os harmônicos
    altos. kappa > 0 = endurecimento (mais "zumbido" com sopro forte).
    """
    n = p.shape[0]
    out = np.zeros(n)
    w = 2.0 * math.pi * f_m
    dt = 1.0 / sr
    x = 0.0
    v = 0.0
    for i in range(n):
        a = ganho * p[i] - 2.0 * zeta * w * v - w * w * (x + kappa * x * x * x)
        v += dt * a
        x += dt * v
        out[i] = v
    return out


# --------------------------------------------------------------------------- pentes (ressonância simpática)


@njit(cache=True)
def kernel_pentes(x, atrasos, ganhos, p_lp, n_buf):
    """Pentes realimentados em paralelo com passa-baixa na malha: cordas soltas vibrando por
    simpatia (o guzheng e o pipa "cantam" sozinhos quando outra corda toca a mesma nota)."""
    n = x.shape[0]
    k = atrasos.shape[0]
    out = np.zeros(n)
    bufs = np.zeros((k, n_buf))
    lps = np.zeros(k)
    for i in range(n):
        acc = 0.0
        for j in range(k):
            s = _ler(bufs[j], i - atrasos[j], n_buf)
            lps[j] = (1.0 - p_lp) * s + p_lp * lps[j]
            v = x[i] + ganhos[j] * lps[j]
            bufs[j, i % n_buf] = v
            acc += lps[j]
        out[i] = acc
    return out


# --------------------------------------------------------------------------- reverb FDN


@njit(cache=True)
def kernel_fdn(xl, xr, atrasos, g, p, mod_prof, mod_taxa, sr, n_buf):
    """Rede de atraso realimentada (Jot/Stautner-Puckette) com 8 linhas, matriz de Hadamard,
    absorção dependente da frequência em cada linha e leve modulação (tira o som metálico)."""
    n = xl.shape[0]
    L = 8
    outl = np.zeros(n)
    outr = np.zeros(n)
    bufs = np.zeros((L, n_buf))
    lps = np.zeros(L)
    s = np.zeros(L)
    fases = np.zeros(L)
    for j in range(L):
        fases[j] = j * 0.7853981
    sinal_in = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    sinal_l = np.array([1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0])
    sinal_r = np.array([1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0])
    w = 2.0 * math.pi * mod_taxa / sr
    for i in range(n):
        for j in range(L):
            d = atrasos[j] + mod_prof * math.sin(w * i * (1.0 + 0.13 * j) + fases[j])
            v = _ler(bufs[j], i - d, n_buf)
            lps[j] = g[j] * (1.0 - p[j]) * v + p[j] * lps[j]
            s[j] = lps[j]
        # Hadamard 8×8 rápida (borboletas), normalizada por 1/sqrt(8)
        h = 1
        while h < L:
            for a in range(0, L, 2 * h):
                for b in range(a, a + h):
                    u = s[b]
                    t = s[b + h]
                    s[b] = u + t
                    s[b + h] = u - t
            h *= 2
        ol = 0.0
        orr = 0.0
        for j in range(L):
            fb = s[j] * 0.35355339
            entrada = xl[i] if (j % 2 == 0) else xr[i]
            bufs[j, i % n_buf] = fb + entrada * sinal_in[j] * 0.5
            ol += lps[j] * sinal_l[j]
            orr += lps[j] * sinal_r[j]
        outl[i] = ol * 0.35355339
        outr[i] = orr * 0.35355339
    return outl, outr


# --------------------------------------------------------------------------- utilitários de efeitos


@njit(cache=True)
def kernel_allpass(x, d, g):
    """Passa-tudo de Schroeder y[n] = -g x[n] + x[n-d] + g y[n-d] (difusão do reverb)."""
    n = x.shape[0]
    y = np.zeros(n)
    for i in range(n):
        xd = x[i - d] if i >= d else 0.0
        yd = y[i - d] if i >= d else 0.0
        y[i] = -g * x[i] + xd + g * yd
    return y


@njit(cache=True)
def kernel_envelope(r, ca, cs):
    """Seguidor de envelope com ataque (ca) e soltura (cs) diferentes."""
    out = np.empty_like(r)
    e = 0.0
    for i in range(r.shape[0]):
        c = ca if r[i] > e else cs
        e = c * e + (1.0 - c) * r[i]
        out[i] = e
    return out


@njit(cache=True)
def kernel_atraso_modulado(x, base, prof, w, fase):
    """Atraso com modulação senoidal (chorus/uníssono)."""
    n = x.shape[0]
    nb = int(base + prof) + 8
    buf = np.zeros(nb)
    out = np.zeros(n)
    for i in range(n):
        buf[i % nb] = x[i]
        d = base + prof * math.sin(w * i + fase)
        out[i] = _ler(buf, i - d, nb)
    return out
