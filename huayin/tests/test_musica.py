import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

import huayin as hy

SR = 32000  # mais rápido nos testes


def musica_teste(semente=0):
    m = hy.Musica("teste 测试", tempo=120, tom="1=D", sr=SR, semente=semente, reverb="sala")
    p = m.faixa("pipa", "pipa", pan=-0.3)
    p.jianpu("1 2 3 5 | 6{lun} - 5 3 |")
    e = m.faixa("erhu", "erhu", volume_db=-3)
    e.jianpu("3 - 5 6 | (5 - 3 2) |", 0)
    t = m.faixa("tg", "tanggu")
    t.nota(None, 0, 1, 0.7)
    t.nota(None, 4, 1, 0.7, "aro")
    return m


class TestMusica(unittest.TestCase):
    def test_render_estereo_e_loudness(self):
        m = musica_teste()
        y = m.renderizar()
        self.assertEqual(y.shape[0], 2)
        self.assertTrue(np.all(np.isfinite(y)))
        self.assertLessEqual(np.max(np.abs(y)), 10 ** (-1 / 20) + 1e-6)
        self.assertLess(abs(m.estatisticas["lufs"] - (-16)), 2.0)

    def test_determinismo(self):
        a = musica_teste(1).renderizar()
        b = musica_teste(1).renderizar()
        c = musica_teste(2).renderizar()
        n = min(a.shape[1], b.shape[1], c.shape[1])
        self.assertTrue(np.allclose(a[:, :n], b[:, :n]))
        self.assertFalse(np.allclose(a[:, :n], c[:, :n]))

    def test_salvar_carregar_json(self):
        m = musica_teste()
        m.faixas[0].automacao("pan", [(0, -1), (8, 1)])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            m.salvar(p)
            m2 = hy.Musica.carregar(p)
        self.assertEqual(len(m2.faixas), 3)
        self.assertEqual(len(m2.faixas[0].notas), len(m.faixas[0].notas))
        self.assertEqual(m2.faixas[0].notas[4].tecnicas, [("lun", {})])
        self.assertEqual(m2.faixas[0].automacoes[0].pontos, [[0, -1], [8, 1]])

    def test_exportar_formatos(self):
        m = musica_teste()
        y = m.renderizar()
        with tempfile.TemporaryDirectory() as d:
            for suf in (".wav", ".flac", ".ogg"):
                p = m.exportar(Path(d) / f"x{suf}", audio=y, verbose=False)
                z, sr = sf.read(p)
                self.assertEqual(sr, SR)
                self.assertGreater(z.shape[0], SR)
            # OGG longo (o libsndfile caía gravando tudo de uma vez)
            longo = np.random.default_rng(0).normal(0, 0.1, (2, 60 * SR))
            p = hy.salvar_audio(Path(d) / "longo.ogg", longo, SR)
            self.assertGreater(sf.info(str(p)).duration, 59)
            stems = m.exportar_stems(Path(d) / "stems")
            self.assertTrue(any(s.name == "erhu.wav" for s in stems))

    def test_midi_ida_e_volta(self):
        m = musica_teste()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.mid"
            m.exportar_midi(p)
            m2 = hy.Musica.carregar(p)
        n1 = sum(len(f.notas) for f in m.faixas)
        n2 = sum(len(f.notas) for f in m2.faixas)
        self.assertEqual(n1, n2)
        self.assertAlmostEqual(m2.tempo.bpm_inicial, 120, places=3)

    def test_arquivo_jp(self):
        txt = """titulo: teste jp
tempo: 90
tom: 1=G

[faixa melodia: dizi]
volume_db: -2
5 6 1' 2' | 3' - - - |

[faixa base: guzheng]
oitava: 3
1 - 5 - | 1 - - - |
"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.jp"
            p.write_text(txt, encoding="utf-8")
            m = hy.Musica.carregar(p)
        self.assertEqual(m.titulo, "teste jp")
        self.assertEqual([f.instrumento.id for f in m.faixas], ["dizi", "guzheng"])
        self.assertEqual(m.faixas[0].volume_db, -2)
        self.assertEqual(m.faixas[1].notas[0].altura, hy.nota_para_midi("G3"))

    def test_andamento_rampa(self):
        m = hy.Musica(tempo=60)
        m.andamento(4, 120, rampa=True)
        self.assertAlmostEqual(m.tempo.segundos(4), 4 * np.log(2), places=6)
        self.assertAlmostEqual(m.tempo.segundos(8), 4 * np.log(2) + 2, places=6)

    def test_humanizar_muda_mas_e_reproduzivel(self):
        def r(h):
            m = hy.Musica(tempo=120, sr=SR, reverb=None)
            f = m.faixa("p", "pipa")
            f.sequencia("A3 B3 C#4 D4", 0.5)
            if h:
                f.humanizar(15, 0.1, 5)
            return m.renderizar(normalizar=None)
        a, b = r(False), r(True)
        n = min(a.shape[1], b.shape[1])
        self.assertFalse(np.allclose(a[:, :n], b[:, :n]))


if __name__ == "__main__":
    unittest.main()
