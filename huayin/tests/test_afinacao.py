import math
import unittest

from huayin.afinacao import TEMPERAMENTOS, Afinacao, Tom, nota_para_midi


class TestAfinacao(unittest.TestCase):
    def test_nomes(self):
        self.assertEqual(nota_para_midi("A4"), 69)
        self.assertEqual(nota_para_midi("C#5"), 73)
        self.assertEqual(nota_para_midi("Bb3"), 58)
        self.assertEqual(nota_para_midi("sol3"), 55)
        self.assertAlmostEqual(nota_para_midi("A4+50"), 69.5)
        with self.assertRaises(ValueError):
            nota_para_midi("H9")

    def test_hz(self):
        a = Afinacao()
        self.assertAlmostEqual(a.hz("A4"), 440.0, places=6)
        self.assertAlmostEqual(a.hz(60), 261.6256, places=3)
        self.assertEqual(a.hz(440.0), 440.0)
        self.assertAlmostEqual(Afinacao(la4=430).hz("A4"), 430.0)

    def test_sanfen_sunyi_quintas_puras(self):
        r = TEMPERAMENTOS["sanfen_sunyi"]
        self.assertAlmostEqual(r[7], 1.5)                      # 林钟 = quinta pura
        self.assertAlmostEqual(r[2], 9 / 8)                    # 太簇
        # o ciclo não fecha: 仲吕 fica ~23,5 cents acima do 4/3 (a famosa "coma")
        self.assertAlmostEqual(1200 * math.log2(r[5] / (4 / 3)), 23.46, places=1)

    def test_temperamento_relativo_a_tonica(self):
        a = Afinacao(temperamento="justa", tonica="D")
        self.assertAlmostEqual(a.hz("F#4") / a.hz("D4"), 5 / 4, places=6)

    def test_tom_jianpu(self):
        t = Tom.de_texto("1=D")
        self.assertEqual(t.midi_do_grau(1), 62)
        self.assertEqual(t.midi_do_grau(5, 0, 1), 81)
        self.assertEqual(t.midi_do_grau(7, -1), 72)


if __name__ == "__main__":
    unittest.main()
