"""古筝 Guzheng, 箜篌 Konghou (harpa Tang) e 瑟 Se (cítara ritual antiga): cordas fixas com pontes."""
from __future__ import annotations

import numpy as np

from ..afinacao import nota_para_midi
from ..composicao.curvas import CurvaAltura
from .base import Golpe, registrar, tecnica, variante
from .dedilhadas_base import CordaDedilhadaBase


def afinacao_pentatonica(tonica: str = "D", n: int = 21, de: str = "D2") -> list[str]:
    """Cordas em escala pentatônica (宫 商 角 徵 羽) a partir da nota mais próxima de 'de'."""
    graus = [0, 2, 4, 7, 9]
    t = int(nota_para_midi(tonica + "0")) % 12
    m = int(nota_para_midi(de))
    out = []
    while len(out) < n:
        if (m - t) % 12 in graus:
            out.append(m)
        m += 1
    return [_nome(x) for x in out]


def afinacao_diatonica(tonica: str = "C", n: int = 22, de: str = "C3") -> list[str]:
    graus = [0, 2, 4, 5, 7, 9, 11]
    t = int(nota_para_midi(tonica + "0")) % 12
    m = int(nota_para_midi(de))
    out = []
    while len(out) < n:
        if (m - t) % 12 in graus:
            out.append(m)
        m += 1
    return [_nome(x) for x in out]


def _nome(m: int) -> str:
    nomes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{nomes[m % 12]}{m // 12 - 1}"


class _ZitherComum(CordaDedilhadaBase):
    MODO_ALTURA = "cordas_fixas"

    @tecnica("guazou", "刮奏", "glissando", "gua", descricao="glissando pelas cordas (só as notas da escala)",
             params={"ate": "nota final (ex.: 'D5')", "tempo": "duração do glissando (s)",
                     "direcao": "sobe | desce (quando 'ate' não é dado)", "cordas": "nº de cordas (padrão 8)"})
    def _t_guazou(self, gs, nota, rng, ate=None, tempo=0.35, direcao="sobe", cordas=8):
        base = gs[0]
        i0 = base.corda
        if ate is not None:
            f1 = self.afinacao.hz(ate)
            i1 = int(np.argmin([abs(np.log2(f / f1)) for f in self.f_cordas]))
        else:
            i1 = int(np.clip(i0 + (cordas if direcao == "sobe" else -cordas), 0, len(self.f_cordas) - 1))
        passo = 1 if i1 >= i0 else -1
        idx = list(range(i0, i1 + passo, passo))
        out = []
        for k, i in enumerate(idx):
            g = Golpe(**{**base.__dict__, "camadas": []})
            u = k / max(len(idx) - 1, 1)
            g.t0 = base.t0 + tempo * (u ** 0.9) * (1 + 0.04 * rng.standard_normal())
            g.corda, g.f0, g.curva, g.pan = i, self.f_cordas[i], CurvaAltura(), self.pan_corda(i)
            g.vel = base.vel * (0.55 + 0.45 * (u if passo > 0 else 1 - u) ** 0.5) * (0.9 + 0.2 * rng.random())
            g.dur = max(base.dur - (g.t0 - base.t0), 0.3)
            out.append(g)
        out[-1].vel = base.vel
        return out

    @tecnica("huazhi", "花指", descricao="glissando curto e rápido que desemboca na nota (ornamento típico do zheng)",
             params={"cordas": "quantas cordas antes (padrão 5)", "tempo": "s (padrão 0.15)", "de": "cima | baixo"})
    def _t_huazhi(self, gs, nota, rng, cordas=5, tempo=0.15, de="cima"):
        base = gs[0]
        sinal = 1 if de == "cima" else -1
        out = []
        for k in range(int(cordas), 0, -1):
            i = base.corda + sinal * k
            if not 0 <= i < len(self.f_cordas):
                continue
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.t0 = base.t0 - tempo * k / cordas
            g.corda, g.f0, g.curva, g.pan = i, self.f_cordas[i], CurvaAltura(), self.pan_corda(i)
            g.vel = base.vel * 0.5 * (1 - 0.4 * k / cordas)
            g.dur = base.dur + tempo
            out.append(g)
        return out + [base]

    @tecnica("cuo", "撮", "oitava", descricao="duas cordas ao mesmo tempo (oitava abaixo por padrão)",
             params={"intervalo": "semitons abaixo (padrão 12)"})
    def _t_cuo(self, gs, nota, rng, intervalo=12):
        base = gs[0]
        f = base.f0 * 2 ** (-float(intervalo) / 12)
        fake = type(nota)(**{**nota.__dict__, "f0": f, "corda": None, "curva": None})
        g = self.golpe_padrao(fake, rng)
        return [base, g]


@registrar
class Guzheng(_ZitherComum):
    id = "guzheng"
    nome = "Guzheng"
    nome_cn = "古筝"
    pinyin = "gǔzhēng"
    descricao = ("Cítara de 21 cordas sobre pontes móveis (雁柱, 'pés de ganso'), afinada em pentatônica. "
                 "A mão direita dedilha com unhas postiças à direita das pontes; a esquerda APERTA a corda à "
                 "esquerda da ponte para fazer as notas que faltam (按音), vibratos 揉 e deslizes.")
    historia = ("Mais de 2000 anos (dinastia Qin). Ancestral do koto japonês, do gayageum coreano e do đàn "
                "tranh vietnamita. Peças: 高山流水, 渔舟唱晚 (Barco de pesca cantando ao entardecer).")
    extensao = ("D2", "D6")
    AFINACOES = {t: afinacao_pentatonica(t) for t in ("D", "C", "G", "F", "A", "Bb", "E")}
    AFINACAO_PADRAO = "D"
    CORPO_PADRAO = "guzheng"
    MAX_PRESSAO = 300
    PARAMETROS = {
        "afinacao": ("D", "tom da pentatônica (D, C, G, F, A, Bb, E) ou lista de 21 notas"),
        "material": ("aco_nylon", "aço com náilon (moderno) | seda (zheng antigo)"),
        "dureza": (0.9, "unhas postiças 义甲"),
        "posicao": (0.13, "ponto de dedilhado"),
        "largura": (0.65, "abertura estéreo (graves à esquerda, agudos à direita)"),
        "comprimento": (1.0, "comprimento vibrante médio (m)"),
        "abafar": ("soar", "as cordas soam até serem tocadas de novo"),
        "simpatia": (0.12, "o zheng 'canta' por simpatia"),
        "t60_escala": (1.1, "sustentação"),
        "portamento": (0.14, "duração padrão dos deslizes (s)"),
    }

    @tecnica("tuo", "托", descricao="polegar para fora: o toque principal, cheio")
    def _t_tuo(self, gs, nota, rng):
        for g in gs:
            g.vel = min(1.0, g.vel * 1.05)
        return gs

    @tecnica("mo", "抹", descricao="indicador para dentro")
    def _t_mo(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.92
            g.posicao += 0.01
        return gs

    @tecnica("gou", "勾", descricao="médio para dentro: um pouco mais escuro")
    def _t_gou(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.9
            g.dureza -= 0.08
        return gs

    @tecnica("yaozhi", "摇指", "yao", descricao="trêmulo rápido do polegar (vai e volta) — o 'canto' contínuo do zheng",
             params={"velocidade": "golpes por segundo (padrão 15)"})
    def _t_yaozhi(self, gs, nota, rng, velocidade=15.0):
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.88], [], [0.13, 0.135], jitter=0.05)

    @tecnica("saoyao", "扫摇", descricao="baixo no polegar + trêmulo na melodia (alternado)",
             params={"velocidade": "padrão 12", "baixo": "semitons abaixo (padrão 12)"})
    def _t_saoyao(self, gs, nota, rng, velocidade=12.0, baixo=12):
        trem = self._repetir(gs, nota, rng, velocidade, [1.0, 0.85], [])
        f = nota.f0 * 2 ** (-float(baixo) / 12)
        fake = type(nota)(**{**nota.__dict__, "f0": f, "corda": None, "curva": None})
        out = []
        for k, g in enumerate(trem):
            out.append(g)
            if k % 4 == 0:
                b = self.golpe_padrao(fake, rng)
                b.t0, b.dur, b.vel = g.t0, g.dur * 4, g.vel * 0.8
                out.append(b)
        return out

    @tecnica("rou", "揉", "vibrato", descricao="vibrato apertando a corda (só sobe: apertar não abaixa)",
             params={"prof": "cents (padrão 30, 大揉 ~60)", "taxa": "Hz (padrão 5.5)", "atraso": "s"})
    def _t_rou(self, gs, nota, rng, prof=30.0, taxa=5.5, atraso=0.15):
        for g in gs:
            g.curva.vibrato(atraso, None, taxa, prof, "acima", ataque=0.25)
        return gs

    @tecnica("chan", "颤", descricao="tremor rápido e estreito da mão esquerda", params={"prof": "cents (padrão 18)"})
    def _t_chan(self, gs, nota, rng, prof=18.0):
        for g in gs:
            g.curva.vibrato(0.05, None, 8.0, prof, "acima", ataque=0.1)
        return gs

    @tecnica("shanghua", "上滑音", "huaan", "滑按", descricao="dedilha a corda solta e aperta até a nota (sobe)",
             params={"tempo": "s (padrão 0.2)", "atraso": "s"})
    def _t_shanghua(self, gs, nota, rng, tempo=0.2, atraso=0.08):
        for g in gs:
            c = 1200 * np.log2(g.f0 / self.f_cordas[g.corda])
            if c < 30 and g.corda > 0:
                # a nota é a própria corda solta: toca a corda de baixo e aperta até ela
                g.corda -= 1
                g.pan = self.pan_corda(g.corda)
                c = 1200 * np.log2(g.f0 / self.f_cordas[g.corda])
            g.curva = CurvaAltura([(0.0, -c, "degrau")]).para(atraso, -c, "degrau").para(atraso + tempo, 0.0, "suave")
        return gs

    @tecnica("xiahua", "下滑音", "回滑", descricao="dedilha já apertada (um tom acima) e solta até a nota (desce)",
             params={"cents": "padrão 200", "tempo": "s"})
    def _t_xiahua(self, gs, nota, rng, cents=200.0, tempo=0.2):
        for g in gs:
            g.curva.inicio_em(cents).para(0.06, cents, "degrau").para(0.06 + tempo, 0, "suave")
        return gs

    @tecnica("huihua", "回滑音", descricao="sobe apertando e volta (ornamento cantado)",
             params={"cents": "padrão 200", "tempo": "s"})
    def _t_huihua(self, gs, nota, rng, cents=200.0, tempo=0.15):
        for g in gs:
            g.curva.para(0.1, 0, "degrau").para(0.1 + tempo, cents, "suave").para(0.15 + 2.2 * tempo, 0, "suave")
        return gs

    @tecnica("dianan", "点按", descricao="aperta e solta rapidinho logo depois do ataque")
    def _t_dianan(self, gs, nota, rng):
        for g in gs:
            g.curva.para(0.06, 0, "degrau").para(0.1, 150, "rapido").para(0.18, 0, "suave")
        return gs


@registrar
class Konghou(_ZitherComum):
    id = "konghou"
    nome = "Konghou (harpa Tang)"
    nome_cn = "箜篌"
    pinyin = "kōnghóu"
    descricao = ("Harpa angular vertical (竖箜篌) da corte Tang, de origem persa/assíria: cordas de seda numa "
                 "moldura em L, sem pontes nem pedais. Reconstrução: 23 cordas diatônicas, sem bend.")
    historia = ("Desapareceu depois da dinastia Ming; conhecido por pinturas de Dunhuang, pelo exemplar de "
                "Shōsōin e pelo poema 李凭箜篌引 de 李贺. O 雁柱箜篌 moderno (com pontes) é uma recriação do séc. XX.")
    extensao = ("C3", "G6")
    AFINACOES = {t: afinacao_diatonica(t, 23, "C3") for t in ("C", "D", "F", "G", "Bb")}
    AFINACAO_PADRAO = "D"
    CORPO_PADRAO = "konghou"
    MAX_PRESSAO = 0
    PARAMETROS = {
        "afinacao": ("D", "tom da escala diatônica das cordas"),
        "material": ("seda_fina", "seda"),
        "dureza": (0.4, "polpa dos dedos (harpa)"),
        "posicao": (0.3, "harpas são tocadas perto do meio da corda: som redondo"),
        "largura": (0.45, "abertura estéreo"),
        "abafar": ("soar", "as cordas soam livres"),
        "simpatia": (0.1, "ressonância simpática"),
    }

    @tecnica("pai", "拍", "abafar_mao", descricao="a palma abafa as cordas (corte seco)")
    def _t_pai(self, gs, nota, rng):
        for g in gs:
            g.dur = min(g.dur, 0.25)
            g.t60_soltura = 0.05
        return gs


@registrar
class Se(_ZitherComum):
    id = "se"
    nome = "Se"
    nome_cn = "瑟"
    pinyin = "sè"
    descricao = ("Cítara ritual de 25 cordas de seda com pontes, da música 雅乐 dos Zhou aos Han. Grave, "
                 "escura, de sustentação longa; tocada com os dedos sem unhas.")
    historia = "Um 瑟 de 2500 anos foi achado no túmulo do Marquês Yi de Zeng, junto com o 编钟."
    extensao = ("A1", "E5")
    AFINACOES = {t: afinacao_pentatonica(t, 25, "A1") for t in ("D", "C", "G", "F")}
    AFINACAO_PADRAO = "D"
    CORPO_PADRAO = "guqin"
    MAX_PRESSAO = 200
    PARAMETROS = {
        "afinacao": ("D", "tom da pentatônica"),
        "material": ("seda", "seda"),
        "dureza": (0.3, "polpa"),
        "posicao": (0.16, "ponto"),
        "largura": (0.55, "estéreo"),
        "abafar": ("soar", "soa livre"),
        "simpatia": (0.12, "simpatia"),
        "comprimento": (1.1, "m"),
    }


variante("guzheng_seda", "guzheng", "Guzheng com cordas de seda", "o zheng antigo, antes das cordas de aço",
         material="seda", dureza=0.6, t60_escala=0.9)
variante("yanzhu_konghou", "konghou", "Konghou moderno 雁柱箜篌",
         "recriação moderna com pontes: cordas de náilon-aço e mais brilho", material="aco_nylon", dureza=0.55)
