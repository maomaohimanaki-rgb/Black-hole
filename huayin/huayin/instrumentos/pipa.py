"""琵琶 Pipa moderno e 曲项琵琶 pipa da dinastia Tang (618–907)."""
from __future__ import annotations

import numpy as np

from ..composicao.curvas import CurvaAltura
from .base import Golpe, registrar, tecnica, variante
from .dedilhadas_base import CordaDedilhadaBase


class _PipaComum(CordaDedilhadaBase):
    """Técnicas que o pipa moderno e o Tang compartilham."""

    def _estrumar(self, gs, nota, rng, direcao, intervalo, cordas, acorde, forca_batida=0.0):
        base = gs[0]
        n = len(self.f_cordas)
        idx = list(range(n)) if cordas is None else [int(c) for c in str(cordas).split()]
        if direcao < 0:
            idx = idx[::-1]
        notas_extra = {}
        if acorde:
            # acorde explícito: semitons acima da nota, distribuídos nas cordas vizinhas
            for k, s in enumerate(str(acorde).split()):
                f = nota.f0 * 2 ** (float(s) / 12)
                i, _ = self.escolher_corda(f, type(nota)(**{**nota.__dict__, "f0": f, "corda": None}))
                notas_extra[i] = f
        out = []
        for k, i in enumerate(idx):
            if i == base.corda:
                f = base.f0
                curva = base.curva
            else:
                # cordas que não têm a nota soam soltas (é assim no 扫拂 do 十面埋伏)
                f = notas_extra.get(i, self.f_cordas[i])
                curva = CurvaAltura()
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.corda, g.f0, g.curva = i, f, curva
            g.t0 = base.t0 + k * intervalo * (1 + 0.15 * rng.standard_normal())
            g.dur = max(base.dur - k * intervalo, 0.05)
            g.pan = self.pan_corda(i)
            g.vel = float(np.clip(base.vel * (0.85 + 0.25 * rng.random()), 0.02, 1))
            out.append(g)
        if forca_batida > 0:
            out[0].camadas.append(("batida", {"forca": base.vel * forca_batida, "f": 150}))
        return out


@registrar
class Pipa(_PipaComum):
    id = "pipa"
    nome = "Pipa"
    nome_cn = "琵琶"
    pinyin = "pípa"
    descricao = ("Alaúde em forma de pera com 4 cordas, 6 相 e 24–25 品 (trastes altos: a corda não toca "
                 "o braço, então apertar mais forte sobe a nota). Tocado com unhas postiças 义甲 nos cinco "
                 "dedos. Som brilhante, ataque seco, trêmulo 轮指 contínuo.")
    historia = ("Chegou da Ásia Central pela Rota da Seda; a forma moderna (vertical, dedos) firmou-se nas "
                "dinastias Ming e Qing. Peças: 十面埋伏 (Emboscada de todos os lados), 春江花月夜.")
    extensao = ("A2", "D6")
    AFINACOES = {
        "moderna": ["A2", "D3", "E3", "A3"],
        "baixa": ["G2", "C3", "D3", "G3"],
        "nanyin": ["D3", "G3", "A3", "D4"],
    }
    AFINACAO_PADRAO = "moderna"
    CORPO_PADRAO = "pipa"
    ALCANCE = 26
    PARAMETROS = {
        "material": ("aco_nylon", "aço com náilon (moderno); 'seda' para o som antigo"),
        "dureza": (0.85, "unhas postiças 义甲 (duras)"),
        "posicao": (0.11, "ponto de dedilhado"),
        "largura": (0.15, "abertura estéreo"),
        "comprimento": (0.66, "comprimento vibrante (m)"),
        "t60_soltura": (0.2, "abafamento"),
    }

    @tecnica("tiao", "挑", "polegar", descricao="polegar para dentro: um pouco mais escuro e suave que o 弹")
    def _t_tiao(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.88
            g.dureza = max(0.0, g.dureza - 0.12)
            g.posicao = min(0.5, g.posicao + 0.02)
        return gs

    @tecnica("lun", "轮指", "lunzhi", "轮", descricao="trêmulo dos cinco dedos (小→无→中→食 para fora, 大 para dentro)",
             params={"velocidade": "golpes por segundo (padrão 16)", "tipo": "longo (5 dedos) | meio (3) | curto (2)"})
    def _t_lun(self, gs, nota, rng, velocidade=16.0, tipo="longo"):
        # cada dedo tem força e ângulo diferentes: o mindinho é o mais fraco, o indicador o mais forte
        if tipo == "meio":
            forcas, pos = [0.85, 1.0, 0.8], [0.12, 0.11, 0.13]
        elif tipo == "curto":
            forcas, pos = [1.0, 0.82], [0.11, 0.13]
        else:
            forcas, pos = [0.72, 0.8, 0.9, 1.0, 0.82], [0.125, 0.12, 0.115, 0.11, 0.13]
        dur = [self.p["dureza"]] * (len(forcas) - 1) + [self.p["dureza"] - 0.12]
        return self._repetir(gs, nota, rng, velocidade, forcas, [], pos, dur, jitter=0.06)

    @tecnica("yaozhi", "摇指", "gun", "滚", descricao="um dedo indo e voltando muito rápido (弹挑 contínuo)",
             params={"velocidade": "golpes por segundo (padrão 18)"})
    def _t_yaozhi(self, gs, nota, rng, velocidade=18.0):
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.86], [], [0.11, 0.12], jitter=0.05)

    @tecnica("sao", "扫", descricao="indicador varre as 4 cordas para fora (acorde batido)",
             params={"intervalo": "s entre cordas (padrão 0.012)", "cordas": "ex.: '0 1 2 3'",
                     "acorde": "semitons extras, ex.: '7 12'"})
    def _t_sao(self, gs, nota, rng, intervalo=0.012, cordas=None, acorde=None):
        return self._estrumar(gs, nota, rng, +1, intervalo, cordas, acorde)

    @tecnica("fu", "拂", descricao="varre as cordas para dentro (do agudo ao grave)",
             params={"intervalo": "s", "cordas": "lista", "acorde": "semitons"})
    def _t_fu(self, gs, nota, rng, intervalo=0.014, cordas=None, acorde=None):
        return self._estrumar(gs, nota, rng, -1, intervalo, cordas, acorde)

    @tecnica("saofu", "扫拂", descricao="扫 e 拂 alternados em sequência rápida (rufar de acordes)",
             params={"velocidade": "batidas por segundo (padrão 10)", "acorde": "semitons"})
    def _t_saofu(self, gs, nota, rng, velocidade=10.0, acorde=None):
        out, t, k = [], 0.0, 0
        base = gs[0]
        per = 1.0 / velocidade
        while t < base.dur - per * 0.3:
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.t0, g.dur = base.t0 + t, max(base.dur - t, 0.05)
            g.vel = base.vel * (1.0 if k % 2 == 0 else 0.85)
            out += self._estrumar([g], nota, rng, +1 if k % 2 == 0 else -1, 0.01, None, acorde)
            t += per * (1 + 0.05 * rng.standard_normal())
            k += 1
        return out or gs

    @tecnica("fen", "分", descricao="indicador e polegar ao mesmo tempo em duas cordas vizinhas",
             params={"intervalo": "semitons da segunda nota (padrão: corda vizinha solta)"})
    def _t_fen(self, gs, nota, rng, intervalo=None):
        base = gs[0]
        g = Golpe(**{**base.__dict__, "camadas": []})
        if intervalo is None:
            g.corda = base.corda - 1 if base.corda > 0 else base.corda + 1
            g.f0, g.curva = self.f_cordas[g.corda], CurvaAltura()
        else:
            g.f0 = base.f0 * 2 ** (float(intervalo) / 12)
            g.corda, _ = self.escolher_corda(g.f0, type(nota)(**{**nota.__dict__, "f0": g.f0, "corda": None}))
        g.pan = self.pan_corda(g.corda)
        g.vel *= 0.9
        return [base, g]

    @tecnica("jiaoxian", "绞弦", descricao="cruza as duas cordas graves e bate: chiado de caixa (tambores do 十面埋伏)",
             params={"forca": "0–1"})
    def _t_jiaoxian(self, gs, nota, rng, forca=None):
        base = gs[0]
        out = []
        for i in (0, 1):
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.corda, g.f0, g.curva = i, self.f_cordas[i] * (1.02 if i else 1.0), CurvaAltura()
            g.contato = 0.55
            g.t60_escala = 0.18
            g.vel = base.vel if forca is None else float(forca)
            g.ruido_ataque = 0.25
            g.pan = self.pan_corda(i)
            out.append(g)
        out[0].camadas.append(("rasgo", {"dur": 0.05, "forca": 0.5 * out[0].vel}))
        return out

    @tecnica("shayin", "煞音", descricao="belisca a corda junto ao traste: nota surda e percussiva")
    def _t_shayin(self, gs, nota, rng):
        for g in gs:
            g.t60_escala = 0.05
            g.t60_soltura = 0.03
            g.contato = 0.3
            g.camadas.append(("clique", {"nivel": 0.5}))
        return gs

    @tecnica("pai", "拍", descricao="bate a mão no tampo (percussão, sem nota)")
    def _t_pai(self, gs, nota, rng):
        for g in gs:
            g.mudo = True
            g.camadas.append(("batida", {"forca": g.vel, "f": 180, "brilho": 1800}))
        return gs

    @tecnica("ti", "提", descricao="puxa a corda para cima e solta: estalo contra os trastes")
    def _t_ti(self, gs, nota, rng):
        for g in gs:
            g.vel = min(1.0, g.vel * 1.25)
            g.contato = 0.15
            g.camadas.append(("clique", {"nivel": 0.8}))
        return gs


@registrar
class PipaTang(_PipaComum):
    id = "pipa_tang"
    nome = "Pipa da dinastia Tang"
    nome_cn = "曲项琵琶"
    pinyin = "qūxiàng pípa"
    descricao = ("Reconstrução do pipa de pescoço curvo da corte Tang: 4 cordas de SEDA, só 4 trastes (相) "
                 "— solto, +2, +3, +4 e +5 semitons por corda —, tocado na horizontal com uma PALHETA de "
                 "madeira grande (拨子) que bate no protetor de couro (捍拨) a cada golpe para baixo. "
                 "Golpe para baixo forte, para cima fraco (como no gakubiwa japonês, descendente direto).")
    historia = ("白居易, 琵琶行 (816): 「大弦嘈嘈如急雨，小弦切切如私语」 — a corda grave rufa como chuva "
                "repentina, a aguda sussurra; 「轻拢慢捻抹复挑」 — leve 拢, lento 捻, 抹 e de novo 挑; "
                "「曲终收拨当心画，四弦一声如裂帛」 — no fim, a palheta risca o centro: quatro cordas, um som "
                "de seda rasgando. O 五弦琵琶 de Shōsōin (Nara) e as partituras de Dunhuang (P.3808, 933 d.C.) "
                "são as fontes materiais.")
    extensao = ("D2", "B3")
    # v1.0: afinações reconstruídas por analogia com o gakubiwa (mesmo desenho de 4 cordas/4 trastes,
    # afinação por modo da peça). As alturas exatas das fontes Tang são discutidas pelos estudiosos;
    # trate como pontos de partida. Para o lá do gagaku use Musica(la4=430).
    AFINACOES = {
        "yiyue": ["D2", "A2", "D3", "E3"],       # 壹越调 (modo em ré)
        "pingdiao": ["E2", "B2", "E3", "F#3"],   # 平调 (modo em mi)
        "huangzhong": ["A1", "E2", "A2", "B2"],  # 黄钟调 (modo em lá)
        "shuangdiao": ["G2", "D3", "G3", "A3"],  # 双调 (modo em sol)
        "moderna": ["A2", "D3", "E3", "A3"],
    }
    AFINACAO_PADRAO = "yiyue"
    CORPO_PADRAO = "pipa_tang"
    TRASTES = [0, 2, 3, 4, 5]
    ALCANCE = 7
    PARAMETROS = {
        "material": ("seda_fina", "seda (o som antigo); 'aco_nylon' para comparar"),
        "dureza": (1.0, "palheta de madeira"),
        "posicao": (0.16, "a palheta bate mais longe da ponte"),
        "largura": (0.12, "abertura estéreo"),
        "comprimento": (0.75, "comprimento vibrante (m)"),
        "ruido_ataque": (0.12, "a palheta raspa a seda"),
        "batida": (0.35, "quanto a palheta bate no protetor de couro 捍拨 nos golpes para baixo"),
        "t60_soltura": (0.25, "abafamento"),
        "simpatia": (0.08, "ressonância simpática"),
    }

    def golpe_padrao(self, nota, rng):
        g = super().golpe_padrao(nota, rng)
        if self.p["batida"] > 0:
            g.camadas.append(("batida", {"forca": g.vel * self.p["batida"] * 0.6, "f": 130}))
        return g

    @tecnica("mo", "抹", "baixo", "下拨", "kakubachi", descricao="palheta para baixo: o golpe forte (抹)")
    def _t_mo(self, gs, nota, rng):
        for g in gs:
            g.vel = min(1.0, g.vel * 1.1)
        return gs

    @tecnica("tiao", "挑", "cima", "上拨", "kaeshibachi", descricao="palheta para cima: fraco, sem batida no couro")
    def _t_tiao(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.6
            g.camadas = [c for c in g.camadas if c[0] != "batida"]
            g.posicao = min(0.5, g.posicao + 0.02)
        return gs

    @tecnica("long", "拢", descricao="(interpretação) mão esquerda empurra a corda de leve: sobe ~1/4 de tom e volta",
             params={"cents": "padrão 45"})
    def _t_long(self, gs, nota, rng, cents=45.0):
        for g in gs:
            g.curva.para(0.08, 0, "degrau").para(0.3, cents, "suave").para(0.6, 0, "suave")
        return gs

    @tecnica("nian", "捻", descricao="(interpretação) mão esquerda esfrega a corda: vibrato lento e largo",
             params={"taxa": "Hz (padrão 3.5)", "prof": "cents (padrão 40)"})
    def _t_nian(self, gs, nota, rng, taxa=3.5, prof=40.0):
        for g in gs:
            g.curva.vibrato(0.15, None, taxa, prof, "acima", ataque=0.3)
        return gs

    @tecnica("sao", "扫", "扫拨", descricao="palheta varre as 4 cordas para baixo, batendo no couro",
             params={"intervalo": "s entre cordas (padrão 0.009)", "acorde": "semitons extras"})
    def _t_sao(self, gs, nota, rng, intervalo=0.009, acorde=None):
        return self._estrumar(gs, nota, rng, +1, intervalo, None, acorde, forca_batida=self.p["batida"] * 1.6)

    @tecnica("fu", "拂", "回拨", descricao="palheta volta para cima pelas 4 cordas (mais fraco)",
             params={"intervalo": "s", "acorde": "semitons"})
    def _t_fu(self, gs, nota, rng, intervalo=0.011, acorde=None):
        out = self._estrumar(gs, nota, rng, -1, intervalo, None, acorde)
        for g in out:
            g.vel *= 0.65
        return out

    @tecnica("huaxian", "当心画", "划弦", "裂帛", descricao="o golpe final do 琵琶行: a palheta risca as 4 cordas "
             "no centro com toda a força — 'seda rasgando'")
    def _t_huaxian(self, gs, nota, rng):
        out = self._estrumar(gs, nota, rng, +1, 0.006, None, None, forca_batida=1.2)
        for g in out:
            g.vel = min(1.0, g.vel * 1.3 + 0.1)
            g.posicao = 0.45  # centro da corda
            g.ruido_ataque = 0.4
        out[0].camadas.append(("rasgo", {"dur": 0.12, "forca": min(1.0, gs[0].vel * 1.4)}))
        return out

    @tecnica("yaobo", "摇拨", "lun", "轮", descricao="trêmulo de palheta (para baixo/para cima alternados)",
             params={"velocidade": "golpes por segundo (padrão 12)"})
    def _t_yaobo(self, gs, nota, rng, velocidade=12.0):
        out = self._repetir(gs, nota, rng, velocidade, [1.0, 0.62], [], jitter=0.07)
        for k, g in enumerate(out):
            if k % 2 == 1:
                g.camadas = []
        return out

    @tecnica("cuo", "撮", descricao="duas cordas de uma vez (a da nota e a vizinha grave)")
    def _t_cuo(self, gs, nota, rng):
        base = gs[0]
        g = Golpe(**{**base.__dict__, "camadas": []})
        g.corda = max(0, base.corda - 1)
        g.f0, g.curva, g.pan = self.f_cordas[g.corda], CurvaAltura(), self.pan_corda(g.corda)
        return [base, g]


variante("pipa_seda", "pipa", "Pipa com cordas de seda", "pipa moderno com as cordas antigas de seda",
         material="seda_fina", t60_soltura=0.18, ruido_ataque=0.06)
