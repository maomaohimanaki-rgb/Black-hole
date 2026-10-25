import unittest

from huayin.afinacao import Tom
from huayin.composicao.jianpu import ler_jianpu


class TestJianpu(unittest.TestCase):
    def ler(self, txt):
        return ler_jianpu(txt, 0, Tom.de_texto("1=D"))

    def test_basico(self):
        ns, fim, _ = self.ler("1 2 3/ 5/ | 6. 5/ 3 - |")
        self.assertEqual([n.altura for n in ns], [62, 64, 66, 69, 71, 69, 66])
        self.assertEqual([n.duracao for n in ns], [1, 1, 0.5, 0.5, 1.5, 0.5, 2])
        self.assertEqual(fim, 7)

    def test_oitavas_acidentes_pausa(self):
        ns, fim, _ = self.ler("1' 1, #4 b7 0 1''")
        self.assertEqual([n.altura for n in ns], [74, 50, 68, 72, 86])
        self.assertEqual(ns[-1].inicio, 5)

    def test_legato_tecnica_quialtera_acorde(self):
        ns, fim, _ = self.ler("(1 2) 5{lun} <3 1 2 3 > 1+3+5")
        self.assertFalse(ns[0].legato)
        self.assertTrue(ns[1].legato)
        self.assertEqual(ns[2].tecnicas, [("lun", {})])
        self.assertAlmostEqual(ns[3].duracao, 2 / 3)
        self.assertEqual(sum(1 for n in ns if n.inicio == 5), 3)

    def test_parametros_de_tecnica(self):
        ns, _, _ = self.ler("5{tui:cents=300,tempo=0.2}{yin}")
        self.assertEqual(ns[0].tecnicas, [("tui", {"cents": 300, "tempo": 0.2}), ("yin", {})])

    def test_apojatura_antes_do_tempo(self):
        ns, _, _ = self.ler("1 [56]3")
        graces = [n for n in ns if n.duracao < 0.2]
        self.assertEqual(len(graces), 2)
        self.assertLess(graces[-1].inicio + graces[-1].duracao, 1.0 + 1e-9)

    def test_dinamica_e_crescendo(self):
        ns, _, _ = self.ler("!p 1 !< 2 3 5 !ff 6")
        self.assertLess(ns[0].vel, ns[2].vel)
        self.assertLess(ns[2].vel, ns[4].vel)

    def test_ligadura_soma(self):
        ns, fim, _ = self.ler("5~ 5 3")
        self.assertEqual(len(ns), 2)
        self.assertEqual(ns[0].duracao, 2)

    def test_erro_claro(self):
        with self.assertRaises(ValueError):
            self.ler("1 2 9")


if __name__ == "__main__":
    unittest.main()
