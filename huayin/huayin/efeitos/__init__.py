"""Efeitos: reverb de espaços (palácio Tang, templo, gruta de Dunhuang...), EQ, compressor,
limitador, eco, chorus, saturação e distância.

Todos recebem e devolvem estéreo (2, N). Use pelo nome em faixa.efeito('eq', ...) ou
diretamente: huayin.efeitos.reverb(x, sr, 'templo').
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..dsp import filtros as F
from ..dsp.kernels import kernel_allpass, kernel_atraso_modulado, kernel_envelope, kernel_fdn
from ..dsp.util import db_para_lin, ruido

# ---------------------------------------------------------------------- reverb


@dataclass
class Sala:
    nome: str
    t60_grave: float          # s (abaixo de ~500 Hz)
    t60_agudo: float          # s (acima de ~4 kHz)
    tamanho: float            # escala das linhas de atraso (1 = sala média)
    pre_atraso: float         # s
    reflexoes: list           # [(atraso s, ganho, pan)] — primeiras reflexões
    difusao: float = 0.6
    passa_baixa: float = 9000.0
    modulacao: float = 0.3
    descricao: str = ""


SALAS = {
    "sala": Sala("sala", 1.2, 0.6, 1.0, 0.012, [(0.011, 0.5, -0.4), (0.017, 0.4, 0.5), (0.023, 0.35, -0.2),
                                                 (0.031, 0.3, 0.3)], descricao="sala de música de madeira, média"),
    "palacio_tang": Sala("palacio_tang", 2.4, 1.1, 1.8, 0.03,
                         [(0.024, 0.55, -0.6), (0.037, 0.45, 0.6), (0.049, 0.4, -0.3), (0.063, 0.32, 0.4),
                          (0.081, 0.25, 0.0)], 0.7, 7500,
                         descricao="salão de madeira da corte Tang (大明宫): grande, quente, colunas e vigas"),
    "templo": Sala("templo", 4.5, 2.0, 2.4, 0.045,
                   [(0.039, 0.5, -0.5), (0.058, 0.42, 0.5), (0.077, 0.36, -0.1), (0.101, 0.3, 0.2)],
                   0.75, 6500, descricao="templo budista de pedra e madeira, cauda longa"),
    "gruta_dunhuang": Sala("gruta_dunhuang", 1.9, 0.5, 0.9, 0.008,
                           [(0.006, 0.7, -0.3), (0.009, 0.6, 0.4), (0.014, 0.5, -0.5), (0.019, 0.45, 0.2),
                            (0.026, 0.35, 0.0)], 0.8, 5000,
                           descricao="gruta de Mogao (莫高窟): paredes de rocha próximas, reflexões densas e escuras"),
    "patio": Sala("patio", 0.9, 0.4, 1.5, 0.02,
                  [(0.035, 0.45, -0.7), (0.052, 0.4, 0.7), (0.089, 0.3, 0.0), (0.12, 0.2, -0.3)],
                  0.35, 10000, descricao="pátio de casa 四合院 ao ar livre: ecos esparsos, quase sem cauda"),
    "jardim": Sala("jardim", 0.6, 0.3, 1.3, 0.015, [(0.045, 0.3, -0.5), (0.07, 0.25, 0.6)], 0.3, 11000,
                   descricao="jardim de Suzhou com pavilhão: ar livre, só um toque de espaço"),
    "teatro_opera": Sala("teatro_opera", 1.5, 0.8, 1.3, 0.018,
                         [(0.015, 0.5, -0.4), (0.022, 0.45, 0.4), (0.034, 0.35, 0.0), (0.045, 0.3, -0.3)],
                         0.6, 9000, descricao="teatro de ópera de Pequim (戏楼) com palco de madeira"),
    "caverna": Sala("caverna", 6.5, 3.0, 3.0, 0.06,
                    [(0.05, 0.5, -0.5), (0.08, 0.45, 0.5), (0.13, 0.4, 0.0)], 0.85, 4500,
                    descricao="caverna enorme / espaço cósmico: cauda muito longa e escura"),
}

_ATRASOS_BASE = np.array([1031, 1327, 1523, 1801, 2053, 2311, 2633, 2939], float)  # amostras @48 kHz


def reverb(x: np.ndarray, sr: int, sala: str | Sala = "sala", mistura: float = 1.0) -> np.ndarray:
    """Reverb FDN 8×8. mistura=1 devolve só o som molhado (para usar como envio/bus)."""
    s = SALAS[sala] if isinstance(sala, str) else sala
    x = np.atleast_2d(x)
    if x.shape[0] == 1:
        x = np.vstack([x[0], x[0]])
    n_extra = int((s.t60_grave * 1.2 + s.pre_atraso) * sr)
    xl = np.concatenate([x[0], np.zeros(n_extra)])
    xr = np.concatenate([x[1], np.zeros(n_extra)])
    pre = int(s.pre_atraso * sr)
    xl = np.concatenate([np.zeros(pre), xl])[:xl.size]
    xr = np.concatenate([np.zeros(pre), xr])[:xr.size]
    # difusão de entrada: 4 passa-tudos de Schroeder em série
    for d, g in ((142, 0.7), (107, 0.7), (379, 0.65), (277, 0.65)):
        d = int(d * sr / 48000)
        xl = kernel_allpass(xl, d, g * s.difusao)
        xr = kernel_allpass(xr, d + 7, g * s.difusao)
    atrasos = _ATRASOS_BASE * s.tamanho * sr / 48000
    g = np.zeros(8)
    p = np.zeros(8)
    for i, d in enumerate(atrasos):
        g[i], p[i] = F.projetar_perda(sr / d, s.t60_grave, s.t60_agudo, 4000, sr)
    yl, yr = kernel_fdn(xl, xr, atrasos, g, p, s.modulacao * 8 * sr / 48000, 0.7, float(sr),
                        int(atrasos.max() + 32))
    # primeiras reflexões (taps esparsos) a partir do sinal seco
    er_l = np.zeros_like(yl)
    er_r = np.zeros_like(yr)
    for atraso, ganho, pan in s.reflexoes:
        k = int(atraso * sr)
        gl, gr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        er_l[k:] += ganho * gl * np.concatenate([x[0], np.zeros(n_extra)])[:er_l.size - k]
        er_r[k:] += ganho * gr * np.concatenate([x[1], np.zeros(n_extra)])[:er_r.size - k]
    y = np.vstack([yl + 0.5 * er_l, yr + 0.5 * er_r])
    y = F.passa_baixa(y, s.passa_baixa, sr)
    y = F.passa_alta(y, 80, sr)
    if mistura < 1:
        seco = np.vstack([np.concatenate([x[0], np.zeros(n_extra)]), np.concatenate([x[1], np.zeros(n_extra)])])
        y = (1 - mistura) * seco + mistura * y
    return y


# ---------------------------------------------------------------------- EQ e dinâmica


def eq(x, sr, bandas):
    """bandas: [(tipo, Hz, Q, dB)] ex.: [('prateleira_baixa', 120, 0.7, -3), ('pico', 2500, 1, 2)]."""
    y = x
    for tipo, f, q, db in bandas:
        y = F.filtrar(y, F.biquad(tipo, f, sr, q, db))
    return y


def compressor(x, sr, limiar_db=-18.0, razao=3.0, ataque=0.01, soltura=0.15, joelho_db=6.0,
               ganho_db=0.0):
    """Compressor estéreo ligado (detecção de pico suavizada, joelho macio)."""
    nivel = np.max(np.abs(np.atleast_2d(x)), axis=0)
    db = 20 * np.log10(np.maximum(nivel, 1e-9))
    acima = db - limiar_db
    red = np.where(acima <= -joelho_db / 2, 0.0,
                   np.where(acima >= joelho_db / 2, acima * (1 - 1 / razao),
                            (1 - 1 / razao) * (acima + joelho_db / 2) ** 2 / (2 * joelho_db)))
    red = _suavizar_envelope(red, sr, ataque, soltura)
    return x * db_para_lin(ganho_db - red)


def _suavizar_envelope(red, sr, ataque, soltura):
    return kernel_envelope(np.asarray(red, float), np.exp(-1 / (ataque * sr)), np.exp(-1 / (soltura * sr)))


def limitador(x, sr, teto_db=-1.0, soltura=0.08, antecipacao=0.005):
    """Limitador com antecipação: nunca passa do teto."""
    x = np.atleast_2d(x)
    teto = db_para_lin(teto_db)
    look = int(antecipacao * sr)
    nivel = np.max(np.abs(x), axis=0)
    # máximo móvel na janela de antecipação
    from scipy.ndimage import maximum_filter1d
    pico = maximum_filter1d(nivel, size=2 * look + 1)
    ganho = np.minimum(1.0, teto / np.maximum(pico, 1e-9))
    red = -20 * np.log10(ganho)
    red = _suavizar_envelope(red, sr, antecipacao / 3, soltura)
    y = x * db_para_lin(-red)
    return np.clip(y, -teto, teto)


def saturacao(x, sr, drive=2.0, mistura=0.5):
    """Saturação suave (tanh): engrossa e ajuda caixinhas de celular a 'ouvirem' o grave."""
    y = np.tanh(drive * x) / np.tanh(drive)
    return (1 - mistura) * x + mistura * y


def eco(x, sr, tempo=0.35, realimentacao=0.35, mistura=0.25, passa_baixa=4000.0, pingue_pongue=True):
    """Eco com repetições cada vez mais escuras; pingue_pongue alterna esquerda/direita."""
    x = np.atleast_2d(x)
    d = int(tempo * sr)
    reps = max(1, int(np.ceil(np.log(0.001) / np.log(max(min(realimentacao, 0.95), 1e-3)))))
    n = x.shape[1] + d * reps
    y = np.zeros((2, n))
    m = x.mean(axis=0) if pingue_pongue else None
    atual = x.copy()
    for k in range(1, reps + 1):
        atual = F.passa_baixa(atual, passa_baixa, sr)
        g = realimentacao ** (k - 1)
        i0 = k * d
        if pingue_pongue:
            fonte = F.passa_baixa(m, passa_baixa, sr) if k == 1 else atual.mean(axis=0)
            y[(k + 1) % 2, i0:i0 + x.shape[1]] += g * fonte
        else:
            y[:, i0:i0 + x.shape[1]] += g * atual
    return np.pad(x, ((0, 0), (0, n - x.shape[1]))) + mistura * y


def chorus(x, sr, prof_ms=2.5, taxa=0.8, mistura=0.3):
    """Duplica com atraso modulado (uníssono de vários instrumentos, ex.: naipe de erhus)."""
    x = np.atleast_2d(x)
    base = 0.012 * sr
    prof = prof_ms * 1e-3 * sr
    w = 2 * np.pi * taxa / sr
    y = np.vstack([kernel_atraso_modulado(x[0], base, prof, w, 0.0),
                   kernel_atraso_modulado(x[1], base, prof, w, 1.7)])
    return (1 - 0.5 * mistura) * x + mistura * y


def distancia(x, sr, metros=5.0):
    """Afasta a fonte: perde nível (1/r) e agudos (absorção do ar)."""
    g = 1.0 / max(metros / 2.0, 1.0)
    fc = float(np.clip(20000 / (1 + metros / 15), 2000, 20000))
    return F.passa_baixa(x, fc, sr) * g


def ar(x, sr, quantidade=0.02, rng=None):
    """Ruído de ambiente bem baixo (sala viva). Evita o 'silêncio digital' entre notas."""
    rng = rng or np.random.default_rng(7)
    x = np.atleast_2d(x)
    r = np.vstack([ruido(x.shape[1], rng, "rosa"), ruido(x.shape[1], rng, "rosa")])
    r = F.passa_baixa(r, 3000, sr)
    return x + quantidade * 0.05 * r


EFEITOS = {
    "eq": eq, "compressor": compressor, "limitador": limitador, "saturacao": saturacao, "eco": eco,
    "chorus": chorus, "distancia": distancia, "reverb": reverb, "ar": ar,
}


def aplicar(nome: str, x, sr, **params):
    if nome not in EFEITOS:
        raise ValueError(f"efeito desconhecido '{nome}'. Opções: {', '.join(EFEITOS)}")
    return EFEITOS[nome](x, sr, **params)
