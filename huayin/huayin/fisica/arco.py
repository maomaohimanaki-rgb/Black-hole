"""Corda friccionada pelo arco (erhu 二胡, gaohu 高胡, zhonghu 中胡, banhu 板胡).

O erhu não tem espelho: o dedo aperta a corda no ar, então a afinação é contínua e o
portamento (滑音) é natural. A crina do arco passa ENTRE as duas cordas.
"""
from __future__ import annotations

import numpy as np

from ..dsp import filtros as F
from ..dsp.kernels import kernel_arco
from ..dsp.util import ruido

# v1.0: compensação de afinação medida (tests/test_afinacao_fisica.py). O atrito do arco soma
# um pouco de atraso efetivo à malha; com a compensação só do filtro a nota saía ~12–85 cents aguda.
_COMP_BASE = -0.25


def renderizar_arco(f_hz: np.ndarray, vel_arco: np.ndarray, forca: np.ndarray, sr: int,
                    rng: np.random.Generator, beta: float = 0.11, brilho: float = 0.5,
                    ruido_crina: float = 0.02, f_solta: float | None = None,
                    acopl: np.ndarray | None = None) -> np.ndarray:
    """f_hz, vel_arco, forca: curvas por amostra (mesmo tamanho).

    vel_arco ~0.05–0.35 (sinal = direção do arco), forca 0–1, beta = ponto do arco a partir da
    ponte (fração da corda SOLTA), brilho 0–1 (perda na ponte), ruido_crina = textura da crina/breu.
    f_solta: frequência da corda solta; com ela o ponto relativo do arco sobe quando o dedo
    encurta a corda (sem isso as notas agudas pulam de modo, como um arco mal colocado).
    """
    n = f_hz.shape[0]
    p_ponte = float(np.clip(0.75 - 0.45 * brilho, 0.05, 0.9)) * (44100.0 / sr) ** 0.5
    p_ponte = min(p_ponte, 0.95)
    f_ref = float(np.median(f_hz))
    comp = F.atraso_fase_um_polo(p_ponte, f_ref, sr) + _COMP_BASE
    atraso = np.maximum(sr / np.maximum(f_hz, 20.0) - comp, 5.0)
    v = np.asarray(vel_arco, float).copy()
    if ruido_crina > 0:
        # crina de cavalo + breu: microirregularidade da velocidade (o "grão" do som)
        r = F.passa_baixa(ruido(n, rng), 3000, sr)
        v = v + ruido_crina * np.abs(v).max(initial=0.05) * r
    if f_solta:
        b = np.clip(beta * f_hz / f_solta, 0.04, 0.3)
    else:
        b = np.full(n, float(beta))
    n_buf = int(atraso.max()) + 8
    if acopl is None:
        acopl = np.ones(n)
    return kernel_arco(atraso, b, v, np.asarray(forca, float), np.asarray(acopl, float), n_buf, p_ponte, 0.95, 0.99)
