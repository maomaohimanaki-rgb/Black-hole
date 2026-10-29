"""Trava a afinação dos modelos físicos (compensações em fisica/arco.py e fisica/sopro.py)."""
import unittest

import numpy as np

from huayin.fisica import arco, sopro
from huayin.fisica.corda import MATERIAIS, ParamsCorda, renderizar_corda
from util_audio import cents, pico_espectral, yin

SR = 48000


def env(n, a=0.08):
    e = np.ones(n)
    k = int(a * SR)
    e[:k] = np.linspace(0, 1, k)
    return e


class TestAfinacaoFisica(unittest.TestCase):
    def test_corda_fundamental(self):
        rng = np.random.default_rng(0)
        for mat in ("seda", "aco_nylon", "aco"):
            for f in (65.4, 220.0, 880.0):
                y = renderizar_corda(ParamsCorda(f0=f, dur=1.2, material=MATERIAIS[mat]), SR, rng)
                fe = pico_espectral(y[int(0.1 * SR):int(1.1 * SR)], SR, f * 0.8, f * 1.2)
                self.assertLess(abs(cents(fe, f)), 3.0, f"{mat} {f}")

    def test_corda_rigida_tem_parciais_agudas(self):
        rng = np.random.default_rng(0)
        f = 110.0
        y = renderizar_corda(ParamsCorda(f0=f, dur=1.2, material=MATERIAIS["aco"]), SR, rng)
        seg = y[int(0.1 * SR):int(1.1 * SR)]
        p6 = pico_espectral(seg, SR, 6 * f * 0.97, 6 * f * 1.03)
        self.assertGreater(cents(p6, 6 * f), 3.0)  # inarmonicidade: a 6ª parcial sobe

    def test_arco(self):
        rng = np.random.default_rng(1)
        n = SR
        for f in (293.66, 440.0, 880.0, 1320.0, 1760.0):
            y = arco.renderizar_arco(np.full(n, f), 0.12 * env(n), np.full(n, 0.6), SR, rng, f_solta=293.66)
            self.assertLess(abs(cents(yin(y[SR // 2:], SR), f)), 8.0, f"erhu {f}")

    def test_flauta(self):
        rng = np.random.default_rng(1)
        n = SR
        # o modelo de jato é estável de ~290 Hz para cima (o xiao, mais grave, começa em ré4)
        for f in (293.66, 440.0, 880.0, 1760.0):
            y = sopro.renderizar_flauta(np.full(n, f), 0.92 * env(n), SR, rng)
            self.assertLess(abs(cents(yin(y[SR // 2:], SR), f)), 8.0, f"dizi {f}")

    def test_palhetas(self):
        rng = np.random.default_rng(1)
        n = SR
        for f in (293.66, 523.25, 1046.5):
            y = sopro.renderizar_palheta_conica(np.full(n, f), 0.65 * env(n), SR, rng)
            self.assertLess(abs(cents(yin(y[SR // 2:], SR), f)), 10.0, f"suona {f}")
        for f in (196.0, 440.0, 880.0):
            y = sopro.renderizar_palheta_cilindrica(np.full(n, f), 0.7 * env(n), SR, rng)
            self.assertLess(abs(cents(yin(y[SR // 2:], SR), f)), 10.0, f"guanzi {f}")


if __name__ == "__main__":
    unittest.main()
