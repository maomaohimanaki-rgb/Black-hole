"""Todo instrumento renderiza; toda técnica de todo instrumento passa pela preparação sem erro."""
import unittest

import numpy as np

import huayin as hy
from huayin.composicao.nota import NotaR
from huayin.fisica.modal import ParamsModal, renderizar_modal  # noqa: F401
from huayin.instrumentos.continuo_base import ContinuoBase
from huayin.instrumentos.dedilhadas_base import CordaDedilhadaBase
from huayin.instrumentos.percussao import PercussaoBase
from util_audio import cents, pico_espectral

SR = 48000
SEM_ALTURA = {"daluo", "xiaoluo", "chaoluo", "jingbo", "naobo", "xiaobo", "tanggu", "dagu", "bangu", "muyu",
              "bangzi", "paiban", "pengling", "qing"}


def altura_meio(inst):
    lo, hi = (hy.nota_para_midi(x) for x in inst.extensao)
    return int(round(lo + 0.4 * (hi - lo)))


class TestInstrumentos(unittest.TestCase):
    def test_lista(self):
        ids = {i["id"] for i in hy.listar_instrumentos()}
        for k in ("pipa", "pipa_tang", "guqin", "guzheng", "erhu", "dizi", "suona", "sheng", "bianzhong", "daluo"):
            self.assertIn(k, ids)
        self.assertGreaterEqual(len(ids), 40)

    def test_todos_renderizam(self):
        for info in hy.listar_instrumentos():
            iid = info["id"]
            inst = hy.criar(iid, SR)
            alt = None if iid in SEM_ALTURA else altura_meio(inst)
            y = hy.nota_unica(iid, alt, 0.8, 0.7, sr=SR)
            self.assertTrue(np.all(np.isfinite(y)), iid)
            self.assertGreater(np.max(np.abs(y)), 0.05, iid)

    def test_todas_as_tecnicas_preparam(self):
        afin = hy.Afinacao()
        rng = np.random.default_rng(0)
        total = 0
        for iid in list(hy.REGISTRO):
            inst = hy.criar(iid, SR)
            inst.preparar(afin)
            midi = altura_meio(inst)
            f0 = None if iid in SEM_ALTURA else afin.hz(midi)
            for nome in inst.TECNICAS:
                nota = NotaR(0.5, 1.0, f0 or (None if isinstance(inst, PercussaoBase) else 440.0), midi, 0.7,
                             [(nome, {})])
                if isinstance(inst, CordaDedilhadaBase):
                    anterior = NotaR(0.0, 0.5, nota.f0 * 2 ** (-2 / 12), midi - 2, 0.7, [])
                    gs = inst.preparar_golpes([anterior, nota], rng)
                    self.assertTrue(gs, f"{iid}.{nome}")
                elif isinstance(inst, ContinuoBase):
                    s = inst.aplicar_tecnicas(inst.segmento_padrao(nota, rng), nota, rng)
                    self.assertIsNotNone(s)
                elif isinstance(inst, PercussaoBase):
                    bs = inst.aplicar_tecnicas([inst.batida_padrao(nota, rng)], nota, rng)
                    self.assertTrue(bs)
                else:
                    itens = [dict(f0=nota.f0, t0=0.5, dur=1.0, vel=0.7, curva=hy.CurvaAltura(), am=None, trocas=[])]
                    self.assertTrue(inst.aplicar_tecnicas(itens, nota, rng))
                total += 1
        self.assertGreater(total, 500)

    def test_aliases_chineses(self):
        inst = hy.criar("pipa")
        self.assertEqual(inst.resolver_tecnica("轮指").nome, "lun")
        self.assertEqual(hy.criar("guqin").resolver_tecnica("猱").nome, "nao")
        self.assertEqual(hy.criar("erhu").resolver_tecnica("滑揉").nome, "huarou")
        with self.assertRaises(ValueError) as cm:
            inst.resolver_tecnica("lunn")
        self.assertIn("lun", str(cm.exception))  # sugestão

    def test_parametro_errado_sugere(self):
        with self.assertRaises(ValueError) as cm:
            hy.criar("pipa", materail="seda")
        self.assertIn("material", str(cm.exception))

    def test_bend_sobe(self):
        y = hy.nota_unica("pipa", "A3", 1.5, 0.8, "bend:cents=200,tempo=0.1,atraso=0.05", sr=SR)[0]
        f_fim = pico_espectral(y[int(0.6 * SR):int(1.2 * SR)], SR, 200, 300)
        self.assertLess(abs(cents(f_fim, 220 * 2 ** (2 / 12))), 25)

    def test_gongos_glissando(self):
        # 小锣 sobe, 大锣 desce (Jossic et al. 2018)
        for iid, sinal in (("xiaoluo", +1), ("daluo", -1)):
            inst = hy.criar(iid, SR)
            f0 = inst.F0_PADRAO
            y = hy.nota_unica(iid, None, 2.0, 1.0, sr=SR)[0]
            ini = pico_espectral(y[int(0.01 * SR):int(0.09 * SR)], SR, f0 * 0.7, f0 * 1.3)
            fim = pico_espectral(y[int(0.6 * SR):int(1.0 * SR)], SR, f0 * 0.7, f0 * 1.3)
            self.assertGreater(sinal * cents(fim, ini), 40, iid)

    def test_bianzhong_dois_tons(self):
        # o 侧鼓音 (lateral) do mesmo sino soa uma terça acima do 正鼓音 (centro)
        y = hy.nota_unica("bianzhong", "C4", 1.5, 0.8, "ce", sr=SR)[0]
        alvo = pico_espectral(y[int(0.05 * SR):int(1.0 * SR)], SR, 200, 300)
        self.assertLess(abs(cents(alvo, 261.63)), 15)
        inst = hy.criar("bianzhong")
        from huayin.instrumentos.percussao import Batida
        b = Batida(0, 0.8, 261.63, None, 0, 0.5, extra={"golpe": "ce"})
        razoes = sorted(m.razao for m in inst.modos(b))
        self.assertTrue(any(abs(1200 * np.log2(r) + inst._terca(261.63)) < 1 for r in razoes))


if __name__ == "__main__":
    unittest.main()
