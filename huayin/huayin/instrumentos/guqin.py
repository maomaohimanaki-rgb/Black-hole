"""古琴 Guqin: cítara de 7 cordas de seda sem trastes, com 13 徽 (marcas de madrepérola)."""
from __future__ import annotations

from fractions import Fraction

import numpy as np

from ..composicao.curvas import CurvaAltura
from .base import Golpe, registrar, tecnica
from .dedilhadas_base import CordaDedilhadaBase

# posição de cada 徽 a partir do 岳山 (ponte do lado da mão direita), como fração da corda
HUI = {1: Fraction(1, 8), 2: Fraction(1, 6), 3: Fraction(1, 5), 4: Fraction(1, 4), 5: Fraction(1, 3),
       6: Fraction(2, 5), 7: Fraction(1, 2), 8: Fraction(3, 5), 9: Fraction(2, 3), 10: Fraction(3, 4),
       11: Fraction(4, 5), 12: Fraction(5, 6), 13: Fraction(7, 8)}


def hui_fracao(h: float) -> float:
    """徽 fracionário (ex.: 7.6 = '七徽六', seis décimos do caminho entre o 7 e o 8)."""
    if h <= 0:
        return 0.0
    if h >= 13:
        # depois do 13 até o 龙龈: interpola até a corda inteira (posição 14 = 1.0)
        return float(HUI[13]) + (1.0 - float(HUI[13])) * min(h - 13, 1.0)
    a = int(np.floor(h))
    fa = float(HUI[a]) if a >= 1 else 0.0
    fb = float(HUI[a + 1])
    return fa + (fb - fa) * (h - a)


def hui_razao_apertada(h: float) -> float:
    """Razão de frequência de uma nota apertada no 徽 h: a parte que vibra vai do dedo ao 岳山."""
    return 1.0 / max(hui_fracao(h), 1e-3)


def hui_harmonico(h: int) -> int:
    """Harmônico tocado com o dedo encostado no 徽 h (denominador da fração)."""
    return HUI[int(h)].denominator


@registrar
class Guqin(CordaDedilhadaBase):
    id = "guqin"
    nome = "Guqin"
    nome_cn = "古琴"
    pinyin = "gǔqín"
    descricao = ("Cítara de 7 cordas de seda sobre uma caixa longa de paulównia, sem trastes nem pontes "
                 "móveis. Três sons: 散音 (corda solta, 'terra'), 按音 (apertada, 'homem') e 泛音 (harmônico "
                 "nos 徽, 'céu'). A arte está na mão esquerda: deslizes 上/下, vibratos 吟/猱 e o ruído do "
                 "dedo na seda, tudo sobre o som que já está morrendo.")
    historia = ("Instrumento dos letrados há ~3000 anos (Confúcio, 嵇康). Patrimônio da UNESCO (2003). "
                "流水 (Água corrente) foi ao espaço no disco de ouro da Voyager (1977).")
    extensao = ("C2", "D6")
    AFINACOES = {
        "zhengdiao": ["C2", "D2", "F2", "G2", "A2", "C3", "D3"],     # 正调 (padrão)
        "manjiao": ["C2", "D2", "E2", "G2", "A2", "C3", "D3"],       # 慢角调: 3ª corda meio tom abaixo
        "ruibin": ["C2", "D2", "F2", "G2", "Bb2", "C3", "D3"],       # 蕤宾调 (紧五): 5ª meio tom acima
        "mangong": ["Bb1", "D2", "Eb2", "G2", "A2", "Bb2", "D3"],    # 慢宫调: 1ª, 3ª, 6ª abaixadas
        "qingshang": ["C2", "Eb2", "F2", "G2", "Bb2", "C3", "Eb3"],  # 清商调 (aproximação)
    }
    AFINACAO_PADRAO = "zhengdiao"
    CORPO_PADRAO = "guqin"
    MODO_ALTURA = "livre"
    ALCANCE = 26
    PARAMETROS = {
        "material": ("seda", "seda (tradicional) | aco_nylon (cordas modernas de metal-náilon)"),
        "dureza": (0.35, "polpa do dedo + um pouco de unha"),
        "posicao": (0.09, "a mão direita toca perto do 岳山"),
        "largura": (0.3, "abertura estéreo"),
        "comprimento": (1.12, "comprimento vibrante (m)"),
        "abafar": ("soar", "no guqin as notas soam até a corda ser tocada de novo"),
        "t60_soltura": (0.35, "abafamento"),
        "modulacao_tensao": (9.0, "a seda frouxa sobe bastante no ataque forte"),
        "portamento": (0.18, "duração padrão de 上/下 (s)"),
        "simpatia": (0.07, "ressonância simpática"),
        "ruido_ataque": (0.025, "ruído do contato"),
        "amortecimento_apertada": (0.55, "o dedo da mão esquerda absorve energia: notas 按 duram menos"),
    }

    def golpe_padrao(self, nota, rng):
        g = super().golpe_padrao(nota, rng)
        if "hui" in nota.params:
            # 徽 explícito: a nota é feita naquela posição da corda indicada (corda obrigatória)
            g.f0 = self.f_cordas[g.corda] * hui_razao_apertada(float(nota.params["hui"]))
        semis = 12 * np.log2(g.f0 / self.f_cordas[g.corda])
        if semis > 0.3:
            # 按音: a polpa do dedo é uma terminação com perdas (mais curta e mais escura)
            g.t60_escala *= self.p["amortecimento_apertada"] + (1 - self.p["amortecimento_apertada"]) * np.exp(-semis / 24)
            g.dureza *= 0.85
        return g

    # ------------------------------------------------------------------ mão direita
    # para dentro (勾 抹 打 托) usa a polpa: mais escuro; para fora (挑 剔 摘 擘) usa a unha: mais claro

    def _dedo(self, gs, brilho, forca=1.0, pos=0.0):
        for g in gs:
            g.dureza = float(np.clip(g.dureza + brilho, 0, 1))
            g.vel = float(np.clip(g.vel * forca, 0.02, 1))
            g.posicao = float(np.clip(g.posicao + pos, 0.03, 0.4))
        return gs

    @tecnica("gou", "勾", descricao="dedo médio para dentro (polpa): o toque mais comum, redondo")
    def _t_gou(self, gs, nota, rng):
        return self._dedo(gs, 0.0, 1.0)

    @tecnica("mo", "抹", descricao="indicador para dentro (polpa)")
    def _t_mo(self, gs, nota, rng):
        return self._dedo(gs, -0.05, 0.92)

    @tecnica("tiao", "挑", descricao="indicador para fora (unha): mais claro")
    def _t_tiao(self, gs, nota, rng):
        return self._dedo(gs, 0.3, 0.95)

    @tecnica("ti", "剔", descricao="médio para fora (unha)")
    def _t_ti(self, gs, nota, rng):
        return self._dedo(gs, 0.25, 0.9)

    @tecnica("da", "打", descricao="anelar para dentro: mais fraco")
    def _t_da(self, gs, nota, rng):
        return self._dedo(gs, -0.05, 0.8)

    @tecnica("zhai", "摘", descricao="anelar para fora")
    def _t_zhai(self, gs, nota, rng):
        return self._dedo(gs, 0.2, 0.78)

    @tecnica("bo", "擘", descricao="polegar para fora: forte e cheio, usado nas cordas graves")
    def _t_bo(self, gs, nota, rng):
        return self._dedo(gs, 0.1, 1.15, 0.02)

    @tecnica("tuo", "托", descricao="polegar para dentro")
    def _t_tuo(self, gs, nota, rng):
        return self._dedo(gs, -0.05, 1.05, 0.02)

    @tecnica("cuo", "撮", descricao="duas cordas juntas (oitava por padrão)",
             params={"intervalo": "semitons abaixo da nota (padrão 12)"})
    def _t_cuo(self, gs, nota, rng, intervalo=12):
        base = gs[0]
        f = base.f0 * 2 ** (-float(intervalo) / 12)
        fake = type(nota)(**{**nota.__dict__, "f0": f, "corda": None, "params": {}})
        g = self.golpe_padrao(fake, rng)
        if g.corda == base.corda:
            g.corda = max(0, base.corda - 1)
        return [base, g]

    @tecnica("lun", "轮", descricao="anelar, médio e indicador para fora em sequência rápida: 3 notas iguais",
             params={"velocidade": "golpes por segundo (padrão 12)"})
    def _t_lun(self, gs, nota, rng, velocidade=12.0):
        out = []
        for g in gs:
            for k, (forca, br) in enumerate(((0.78, 0.2), (0.88, 0.25), (1.0, 0.3))):
                ng = Golpe(**{**g.__dict__, "camadas": []})
                ng.t0 = g.t0 + k / velocidade
                ng.dur = max(g.dur - k / velocidade, 0.05)
                ng.vel *= forca
                ng.dureza = min(1.0, g.dureza + br)
                ng.curva = g.curva.deslocar(-k / velocidade)
                out.append(ng)
        return out

    @tecnica("suo", "锁", descricao="'tranca': três notas repetidas (抹挑抹) em ritmo rápido-lento",
             params={"velocidade": "golpes por segundo (padrão 9)"})
    def _t_suo(self, gs, nota, rng, velocidade=9.0):
        out = self._repetir(gs, nota, rng, velocidade, [0.95, 0.9, 1.0], [], dureza=[0.3, 0.6, 0.3])
        return out[:3] if len(out) > 3 else out

    @tecnica("gunfu", "滚拂", "gun", "滚", "fu", "拂", descricao="glissando pelas 7 cordas (滚 do agudo ao grave, "
             "拂 do grave ao agudo, ou os dois)",
             params={"direcao": "desce | sobe | desce_sobe", "velocidade": "cordas por segundo (padrão 22)"})
    def _t_gunfu(self, gs, nota, rng, direcao="desce_sobe", velocidade=22.0):
        base = gs[0]
        n = len(self.f_cordas)
        ordem = {"desce": list(range(n - 1, -1, -1)), "sobe": list(range(n)),
                 "desce_sobe": list(range(n - 1, -1, -1)) + list(range(1, n))}[direcao]
        out = []
        for k, i in enumerate(ordem):
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.corda, g.f0, g.curva = i, self.f_cordas[i], CurvaAltura()
            g.t0 = base.t0 + k / velocidade * (1 + 0.1 * rng.standard_normal())
            g.dur = max(base.dur - k / velocidade, 0.1)
            g.vel = base.vel * (0.75 + 0.25 * rng.random())
            g.pan = self.pan_corda(i)
            out.append(g)
        return out

    @tecnica("san", "散", "solta", descricao="força corda solta (散音): escolhe a corda com essa altura")
    def _t_san(self, gs, nota, rng):
        for g in gs:
            cents = [abs(1200 * np.log2(nota.f0 / f)) for f in self.f_cordas]
            i = int(np.argmin(cents))
            g.corda, g.f0, g.pan = i, self.f_cordas[i], self.pan_corda(i)
            g.t60_escala = self.p["t60_escala"]
        return gs

    @tecnica("fanyin", "泛", "泛音", "harmonico", descricao="泛音 no 徽: dedo encostado de leve na corda",
             params={"hui": "徽 (1–13); sem hui escolhe pela altura", "n": "harmônico direto"})
    def _t_fanyin_qin(self, gs, nota, rng, hui=None, n=None):
        if hui is not None:
            for g in gs:
                k = hui_harmonico(int(hui))
                if nota.corda is None:
                    # corda cujo harmônico nesse 徽 dá a altura pedida
                    i = int(np.argmin([abs(1200 * np.log2(nota.f0 / (f * k))) for f in self.f_cordas]))
                else:
                    i = int(nota.corda)
                g.corda, g.harmonico, g.f0 = i, k, self.f_cordas[i]
                g.pan = self.pan_corda(i)
                g.t60_escala = self.p["t60_escala"] * 1.15
                g.dureza = min(1.0, g.dureza + 0.15)
            return gs
        gs = self._t_fanyin(gs, nota, rng, n=n)
        for g in gs:
            g.t60_escala = self.p["t60_escala"] * 1.15
        return gs

    # ------------------------------------------------------------------ mão esquerda

    @tecnica("yin", "吟", descricao="vibrato pequeno e rápido em volta da nota (细吟 / 长吟)",
             params={"prof": "cents (padrão 18)", "taxa": "Hz (padrão 5)", "tipo": "细 | 长 | 定"})
    def _t_yin(self, gs, nota, rng, prof=18.0, taxa=5.0, tipo="长"):
        if tipo in ("细", "xi"):
            prof, taxa = prof * 0.6, taxa * 1.2
        if tipo in ("定", "ding"):
            prof = prof * 0.35  # 定吟: quase só pressão
        for g in gs:
            g.curva.vibrato(0.1, None, taxa, prof, "simetrico", ataque=0.15, decaimento=0.25)
            g.deslize = True
        return gs

    @tecnica("nao", "猱", descricao="vibrato largo e mais lento, que vai fechando (o dedo rola sobre a corda)",
             params={"prof": "cents (padrão 60)", "taxa": "Hz (padrão 3.2)"})
    def _t_nao(self, gs, nota, rng, prof=60.0, taxa=3.2):
        for g in gs:
            g.curva.vibrato(0.08, None, taxa, prof, "simetrico", ataque=0.08, decaimento=0.6, aceleracao=0.4)
            g.deslize = True
        return gs

    @tecnica("jinfu", "进复", descricao="desliza um passo acima e volta", params={"cents": "padrão 200", "tempo": "s"})
    def _t_jinfu(self, gs, nota, rng, cents=200.0, tempo=0.18):
        for g in gs:
            g.curva.para(0.15, 0, "degrau").para(0.15 + tempo, cents, "suave").para(0.25 + 2 * tempo, 0, "suave")
            g.deslize = True
        return gs

    @tecnica("tuifu", "退复", descricao="desliza um passo abaixo e volta", params={"cents": "padrão 200", "tempo": "s"})
    def _t_tuifu(self, gs, nota, rng, cents=200.0, tempo=0.18):
        for g in gs:
            g.curva.para(0.15, 0, "degrau").para(0.15 + tempo, -cents, "suave").para(0.25 + 2 * tempo, 0, "suave")
            g.deslize = True
        return gs

    @tecnica("wanglai", "往来", descricao="vai e volta entre a nota e a de cima várias vezes (balanço)",
             params={"cents": "padrão 200", "vezes": "padrão 2", "tempo": "s por ida"})
    def _t_wanglai(self, gs, nota, rng, cents=200.0, vezes=2, tempo=0.22):
        for g in gs:
            t = 0.15
            g.curva.para(t, 0, "degrau")
            for _ in range(int(vezes)):
                g.curva.para(t + tempo, cents, "suave").para(t + 2 * tempo, 0, "suave")
                t += 2 * tempo
            g.deslize = True
        return gs

    @tecnica("zhuang", "撞", descricao="toque rápido para cima e volta (um 'soluço' na nota)",
             params={"cents": "padrão 200"})
    def _t_zhuang(self, gs, nota, rng, cents=200.0):
        for g in gs:
            g.curva.para(0.12, 0, "degrau").para(0.17, cents, "rapido").para(0.27, 0, "suave")
            g.deslize = True
        return gs

    @tecnica("qiaqi", "掐起", descricao="a mão esquerda belisca a corda ao sair: soa a corda solta sem a direita")
    def _t_qiaqi(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.55
            g.dureza = 0.2
            g.posicao = min(0.45, g.posicao * 3)
        return gs

    @tecnica("yan", "罨", descricao="o polegar esquerdo bate na corda (hammer-on sem nota anterior): som surdo")
    def _t_yan(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.45
            g.dureza = 0.05
            g.posicao = 0.4
            g.ruido_ataque = 0.0
            g.camadas.append(("clique", {"nivel": 0.1}))
        return gs
