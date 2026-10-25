import unittest

import numpy as np

from huayin import efeitos as FX
from huayin.dsp.util import lufs_integrado

SR = 48000


class TestEfeitos(unittest.TestCase):
    def test_lufs_seno_referencia(self):
        # BS.1770: seno de 997 Hz a 0 dBFS num canal só = -3,01 LUFS
        t = np.arange(5 * SR) / SR
        x = np.vstack([np.sin(2 * np.pi * 997 * t), np.zeros_like(t)])
        self.assertAlmostEqual(lufs_integrado(x, SR), -3.01, delta=0.1)

    def test_limitador_teto(self):
        x = np.random.default_rng(0).normal(0, 0.8, (2, SR))
        y = FX.limitador(x, SR, -1.0)
        self.assertLessEqual(np.max(np.abs(y)), 10 ** (-1 / 20) + 1e-9)

    def test_reverb_tem_cauda(self):
        x = np.zeros((2, SR))
        x[:, 100] = 1.0
        for sala in FX.SALAS:
            y = FX.reverb(x, SR, sala)
            self.assertTrue(np.all(np.isfinite(y)), sala)
            energia_tarde = np.mean(y[:, int(0.3 * SR):int(0.5 * SR)] ** 2)
            self.assertGreater(energia_tarde, 1e-10, sala)

    def test_reverb_decai(self):
        x = np.zeros((2, SR))
        x[:, 0] = 1.0
        y = FX.reverb(x, SR, "templo")
        a = np.mean(y[:, int(0.2 * SR):int(0.4 * SR)] ** 2)
        b = np.mean(y[:, int(3.0 * SR):int(3.2 * SR)] ** 2)
        self.assertLess(b, a / 100)

    def test_eco_chorus_eq(self):
        x = np.random.default_rng(1).normal(0, 0.1, (2, SR))
        for nome, ps in (("eco", {}), ("chorus", {}), ("eq", {"bandas": [("pico", 1000, 1, 6)]}),
                         ("compressor", {}), ("saturacao", {}), ("distancia", {}), ("ar", {})):
            y = FX.aplicar(nome, x, SR, **ps)
            self.assertTrue(np.all(np.isfinite(y)), nome)


if __name__ == "__main__":
    unittest.main()
