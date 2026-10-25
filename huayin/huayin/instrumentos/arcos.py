"""胡琴 Huqin (cordas friccionadas): 二胡 erhu, 高胡 gaohu, 中胡 zhonghu, 板胡 banhu, 京胡 jinghu."""
from __future__ import annotations

import numpy as np

from ..dsp import filtros as F
from ..fisica.arco import renderizar_arco
from ..fisica.corda import MATERIAIS, ParamsCorda, renderizar_corda
from .base import registrar, tecnica
from .continuo_base import ContinuoBase, Segmento


class HuqinBase(ContinuoBase):
    familia = "cordas friccionadas 拉弦"
    CORPO_PADRAO = "erhu"
    CORDAS = ["D4", "A4"]
    BETA = 0.11            # ponto do arco na corda solta (fração a partir da ponte)
    GANHO_SAIDA = 0.75
    PARAMETROS = {
        "afinacao": ("", "notas das duas cordas (interna, externa); vazio = padrão"),
        "forca": (0.0, "pressão extra do arco (-0.3 a +0.3)"),
        "ruido_crina": (0.025, "grão da crina e do breu"),
        "ataque": (0.07, "ataque do começo de frase (s)"),
        "soltura": (0.1, "soltura (s)"),
        "portamento": (0.09, "deslize das ligaduras (s) — o erhu não tem espelho: desliza muito"),
        "vibrato": (22.0, "揉弦 automático em notas longas (cents; 0 desliga)"),
        "vibrato_taxa": (6.0, "Hz"),
        "brilho": (0.5, "cor"),
    }

    def configurar(self):
        super().configurar()
        self.cordas = self.p["afinacao"] or self.CORDAS

    def preparar(self, afinacao):
        super().preparar(afinacao)
        self.f_cordas = [afinacao.hz(n) for n in self.cordas]

    def nivel(self, s):
        return s.vel

    def rearticular(self, tt, s, interna=False):
        # troca de arco: a velocidade passa por zero (o arco para e volta); é aqui que o modelo
        # físico gera o pequeno "raspado" de transição, como no instrumento de verdade
        d = 0.035 if not interna else 0.025
        return np.clip(np.abs(tt - d * 0.4) / (d * 0.6), 0.0, 1.0) ** 0.8

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng):
        f_min = float(np.min(f[amp > 0.01 * max(amp.max(), 1e-6)])) if np.any(amp > 0) else float(f[0])
        cand = [x for x in self.f_cordas if x <= f_min * 1.01]
        f_solta = max(cand) if cand else min(self.f_cordas)
        if any(s.extra.get("corda") is not None for s in frase):
            i = next(s.extra["corda"] for s in frase if s.extra.get("corda") is not None)
            f_solta = self.f_cordas[int(i)]
        a = np.clip(amp, 0, 2.0)
        vel = (0.035 + 0.11 * np.minimum(a, 1.4)) * direcao * (a > 1e-4)
        harm = any(s.extra.get("harmonico") for s in frase)
        forca = np.clip(0.48 + 0.22 * np.minimum(a, 1.3) + self.p["forca"] - (0.25 if harm else 0), 0.15, 0.95)
        acopl = np.clip(a / 0.04, 0, 1)
        beta = self.BETA * float(np.mean([s.extra.get("beta", 1.0) for s in frase]))
        br = float(np.clip(np.median(brilho) * 0.5, 0, 1))
        y = renderizar_arco(f, vel, forca, self.sr, rng, beta=beta, brilho=br,
                            ruido_crina=self.p["ruido_crina"] * float(np.median(ruido)), f_solta=f_solta,
                            acopl=acopl)
        # a velocidade na ponte troca de sinal com o arco: tira o DC que sobra de cada arcada
        return F.dc_block(y, 0.999)

    def renderizar_separado(self, s, rng):
        if s.extra.get("pizz"):
            p = ParamsCorda(f0=s.f0, dur=max(s.t1 - s.t0, 0.3), vel=s.vel * 1.2, posicao=0.25, dureza=0.5,
                            material=MATERIAIS["aco_erhu"], t60_soltura=0.1, modulacao_tensao=4.0)
            return renderizar_corda(p, self.sr, rng) * 0.6
        if s.extra.get("col_legno"):
            # 击弓: a vara do arco bate na corda — corda percutida curta + estalo de madeira
            p = ParamsCorda(f0=s.f0, dur=0.12, vel=s.vel, posicao=0.1, material=MATERIAIS["aco_erhu"],
                            t60_escala=0.3, martelo=True, contato_ms=0.6, t60_soltura=0.05)
            y = renderizar_corda(p, self.sr, rng)
            n = min(y.size, int(0.01 * self.sr))
            y[:n] += 0.3 * s.vel * rng.standard_normal(n) * np.exp(-np.arange(n) / (0.002 * self.sr))
            return y * 0.6
        return np.zeros(1)

    # ------------------------------------------------------------------ técnicas

    @tecnica("yarou", "压揉", descricao="vibrato de pressão: o dedo aperta e solta (afinação só sobe)",
             params={"prof": "cents (padrão 30)", "taxa": "Hz (padrão 6)"})
    def _h_yarou(self, s, nota, rng, prof=30.0, taxa=6.0):
        s.curva.vibratos.clear()
        s.curva.vibrato(0.1, None, taxa, prof, "acima", ataque=0.2)
        return s

    @tecnica("gunrou", "滚揉", descricao="vibrato rolando a ponta do dedo (em volta da nota)",
             params={"prof": "cents (padrão 25)", "taxa": "Hz (padrão 6.5)"})
    def _h_gunrou(self, s, nota, rng, prof=25.0, taxa=6.5):
        s.curva.vibratos.clear()
        s.curva.vibrato(0.08, None, taxa, prof, "simetrico", ataque=0.2)
        return s

    @tecnica("huarou", "滑揉", descricao="vibrato deslizando o dedo: largo e expressivo",
             params={"prof": "cents (padrão 70)", "taxa": "Hz (padrão 4.5)"})
    def _h_huarou(self, s, nota, rng, prof=70.0, taxa=4.5):
        s.curva.vibratos.clear()
        s.curva.vibrato(0.1, None, taxa, prof, "simetrico", ataque=0.3)
        return s

    @tecnica("sem_vibrato", "直音", "liso", descricao="nota lisa, sem vibrato automático")
    def _h_liso(self, s, nota, rng):
        s.curva.vibratos.clear()
        return s

    @tecnica("pizz", "boxian", "拨弦", "pizzicato", descricao="dedilha a corda com o dedo")
    def _h_pizz(self, s, nota, rng):
        s.extra["separado"] = True
        s.extra["pizz"] = True
        return s

    @tecnica("jigong", "击弓", "col_legno", descricao="bate a vara do arco na corda (percussivo)")
    def _h_jigong(self, s, nota, rng):
        s.extra["separado"] = True
        s.extra["col_legno"] = True
        return s

    @tecnica("fanyin", "泛音", "harmonico", descricao="harmônico: dedo encostado de leve, som de flauta")
    def _h_fanyin(self, s, nota, rng):
        s.extra["harmonico"] = True
        s.brilho *= 0.5
        s.ruido *= 1.6
        s.curva.vibratos.clear()
        return s

    @tecnica("dungong", "顿弓", descricao="arcada curta e acentuada que para o arco na corda")
    def _h_dungong(self, s, nota, rng):
        s.articulacao = "acento"
        d = s.t1 - s.t0
        s.env = [(0.0, 1.0), (min(0.12, d * 0.6), 0.6), (min(0.16, d * 0.7), 0.0), (d, 0.0)]
        return s

    @tecnica("tiaogong", "跳弓", "spiccato", descricao="o arco quica: nota curtíssima")
    def _h_tiaogong(self, s, nota, rng):
        d = s.t1 - s.t0
        s.env = [(0.0, 1.1), (min(0.05, d * 0.4), 0.5), (min(0.08, d * 0.6), 0.0), (d, 0.0)]
        return s

    @tecnica("kuaigong", "快弓", descricao="arcadas rápidas destacadas (cada nota troca o arco)")
    def _h_kuaigong(self, s, nota, rng):
        s.legato = False
        return s

    @tecnica("liangong", "连弓", "mesmo_arco", descricao="várias notas no mesmo arco (ligadas sem deslize)")
    def _h_liangong(self, s, nota, rng):
        s.legato = True
        s.portamento = 0.02
        return s

    @tecnica("changong", "颤弓", "tremolo_arco", descricao="trêmulo de arco (trocas rapidíssimas)",
             params={"velocidade": "trocas por segundo (padrão 14)"})
    def _h_changong(self, s, nota, rng, velocidade=14.0):
        d = s.t1 - s.t0
        t = 1.0 / velocidade
        while t < d - 0.03:
            s.trocas.append(t)
            t += (1 + 0.06 * rng.standard_normal()) / velocidade
        return s

    @tecnica("paogong", "抛弓", "ricochete", descricao="joga o arco: quiques que vão ficando mais rápidos e fracos",
             params={"quiques": "padrão 6"})
    def _h_paogong(self, s, nota, rng, quiques=6):
        d = s.t1 - s.t0
        env, t, per, g = [(0.0, 0.0)], 0.0, d / (quiques * 0.8), 1.0
        for _ in range(int(quiques)):
            env += [(t, 0.0), (t + 0.008, g), (t + per * 0.45, g * 0.3), (t + per * 0.6, 0.0)]
            t += per
            per *= 0.85
            g *= 0.82
            if t >= d:
                break
        env.append((d, 0.0))
        s.env = env
        return s

    @tecnica("mati", "马嘶", "relincho", descricao="relincho de cavalo (赛马): sobe deslizando, trina e despenca")
    def _h_mati(self, s, nota, rng):
        d = s.t1 - s.t0
        s.curva.vibratos.clear()
        s.curva.inicio_em(-500).para(0.25 * d, 0.0, "suave")
        t = 0.25 * d
        while t < 0.7 * d:
            s.curva.para(t, 0.0, "degrau").para(t + 0.02, 200.0, "rapido").para(t + 0.045, 200, "degrau").para(t + 0.06, 0.0, "rapido")
            t += 0.07
        s.curva.para(0.72 * d, 0.0, "degrau").para(d, -1200.0, "suave")
        s.articulacao = "acento"
        return s

    @tecnica("jinma", "近码", "perto_ponte", descricao="arco perto da ponte: som vítreo, cheio de harmônicos")
    def _h_jinma(self, s, nota, rng):
        s.extra["beta"] = 0.6
        s.brilho *= 1.4
        return s

    @tecnica("yuanma", "远码", "longe_ponte", descricao="arco longe da ponte: som doce e velado")
    def _h_yuanma(self, s, nota, rng):
        s.extra["beta"] = 1.6
        s.brilho *= 0.7
        return s

    @tecnica("corda_interna", "内弦", descricao="toca na corda interna (mais grave e quente)")
    def _h_interna(self, s, nota, rng):
        s.extra["corda"] = 0
        return s


@registrar
class Erhu(HuqinBase):
    id = "erhu"
    nome = "Erhu"
    nome_cn = "二胡"
    pinyin = "èrhú"
    descricao = ("Violino de 2 cordas sem espelho: o dedo aperta a corda no ar, então a afinação é contínua e "
                 "o deslize 滑音 é a alma do instrumento. A crina passa ENTRE as cordas; o ressonador "
                 "hexagonal coberto de pele de píton dá o timbre nasal, quase vocal.")
    historia = ("Os 胡琴 vieram do norte (povos 'hu') na dinastia Tang/Song. 阿炳 (Abing) e 刘天华 tornaram o erhu "
                "solista: 二泉映月 (A lua refletida na segunda fonte), 赛马 (Corrida de cavalos).")
    extensao = ("D4", "A6")
    CORDAS = ["D4", "A4"]
    CORPO_PADRAO = "erhu"


@registrar
class Gaohu(HuqinBase):
    id = "gaohu"
    nome = "Gaohu"
    nome_cn = "高胡"
    pinyin = "gāohú"
    descricao = "Erhu soprano da música cantonesa 广东音乐, tocado com o ressonador entre os joelhos: brilhante e doce."
    extensao = ("G4", "D7")
    CORDAS = ["G4", "D5"]
    CORPO_PADRAO = "gaohu"
    BETA = 0.1


@registrar
class Zhonghu(HuqinBase):
    id = "zhonghu"
    nome = "Zhonghu"
    nome_cn = "中胡"
    pinyin = "zhōnghú"
    descricao = "Erhu contralto (uma quinta abaixo): o 'viola' da orquestra chinesa."
    extensao = ("G3", "D6")
    CORDAS = ["G3", "D4"]
    CORPO_PADRAO = "zhonghu"
    BETA = 0.12


@registrar
class Banhu(HuqinBase):
    id = "banhu"
    nome = "Banhu"
    nome_cn = "板胡"
    pinyin = "bǎnhú"
    descricao = ("Fiddle com casca de coco e TAMPO DE MADEIRA fino em vez de pele: agudo, estridente e alegre, "
                 "das óperas 秦腔 e 梆子 do norte.")
    extensao = ("D4", "D7")
    CORDAS = ["D5", "A5"]
    CORPO_PADRAO = "banhu"
    BETA = 0.09
    GANHO_SAIDA = 0.7
    PARAMETROS = {"ruido_crina": (0.035, "crina"), "brilho": (0.7, "cor"), "vibrato": (28.0, "vibrato")}


@registrar
class Jinghu(HuqinBase):
    id = "jinghu"
    nome = "Jinghu"
    nome_cn = "京胡"
    pinyin = "jīnghú"
    descricao = ("O fiddle da ópera de Pequim: corpo de bambu com pele de cobra, cordas de seda, muito agudo e "
                 "penetrante. Conduz a melodia junto com a voz.")
    extensao = ("A4", "A6")
    CORDAS = ["A4", "E5"]   # 西皮 (6-3); para 二黄 use afinacao=['G4', 'D5']
    CORPO_PADRAO = "banhu"
    BETA = 0.09
    PARAMETROS = {"ruido_crina": (0.04, "crina"), "brilho": (0.85, "cor"), "vibrato": (15.0, "vibrato quase reto"),
                  "portamento": (0.05, "deslizes curtos e rápidos")}

    def pos_processar(self, x):
        # bambu + pele pequena: corta o grave e realça a região de 2–4 kHz
        x = F.passa_alta(x, 380, self.sr)
        return F.filtrar(x, F.biquad("pico", 3000, self.sr, 1.2, 4.0))
