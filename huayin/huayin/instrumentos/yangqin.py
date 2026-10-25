"""扬琴 Yangqin: saltério de cordas percutidas por baquetas de bambu (琴竹)."""
from __future__ import annotations

import numpy as np

from ..composicao.curvas import CurvaAltura
from .base import Golpe, registrar, tecnica
from .dedilhadas_base import CordaDedilhadaBase


def _cromatica(de: str = "G2", ate: str = "A6") -> list[str]:
    from ..afinacao import nota_para_midi
    nomes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return [f"{nomes[m % 12]}{m // 12 - 1}" for m in range(int(nota_para_midi(de)), int(nota_para_midi(ate)) + 1)]


@registrar
class Yangqin(CordaDedilhadaBase):
    id = "yangqin"
    nome = "Yangqin"
    nome_cn = "扬琴"
    pinyin = "yángqín"
    descricao = ("Saltério trapezoidal de cordas de aço em cursos de 2 a 5 cordas por nota, percutido com "
                 "duas baquetas finas de bambu com ponta de borracha. Sem abafadores: as notas soam juntas "
                 "num halo metálico. O trêmulo 轮竹 é a voz característica.")
    historia = ("Veio da Pérsia (santur) pelo mar, no fim da dinastia Ming; o modelo 402 moderno é cromático "
                "com ~4,5 oitavas.")
    extensao = ("G2", "A6")
    AFINACOES = {"402": _cromatica("G2", "A6")}
    AFINACAO_PADRAO = "402"
    CORPO_PADRAO = "yangqin"
    MODO_ALTURA = "cordas_fixas"
    MARTELO = True
    CURSO = 3
    DESAFINACAO_CURSO = 1.2
    PARAMETROS = {
        "material": ("aco", "aço"),
        "dureza": (0.7, "0 = ponta de borracha macia, 1 = bambu nu"),
        "posicao": (0.12, "ponto de golpe"),
        "largura": (0.55, "estéreo (graves à esquerda)"),
        "abafar": ("soar", "sem abafadores: as cordas soam livres"),
        "simpatia": (0.1, "ressonância simpática"),
        "t60_escala": (0.8, "sustentação"),
        "modulacao_tensao": (3.0, "subida no ataque"),
        "ruido_ataque": (0.08, "estalo da baqueta"),
    }

    def curso_da_nota(self, g: Golpe) -> int:
        # graves têm 2 cordas por curso, agudos até 5 (é assim nos yangqin 402)
        f = self.f_cordas[g.corda]
        return 2 if f < 200 else (3 if f < 600 else 4)

    def contato_ms(self, g: Golpe) -> float:
        return 0.35 + 1.4 * (1 - g.dureza)

    @tecnica("dan", "单竹", descricao="golpe simples (padrão)")
    def _t_dan(self, gs, nota, rng):
        return gs

    @tecnica("lunzhu", "轮竹", "lun", "tremolo", descricao="trêmulo alternando as duas baquetas",
             params={"velocidade": "golpes por segundo (padrão 16)"})
    def _t_lunzhu(self, gs, nota, rng, velocidade=16.0):
        # a baqueta não abafa: o curso continua soando e cada golpe soma energia
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.9], [], jitter=0.04, fundir=True)

    @tecnica("chanzhu", "颤竹", descricao="uma baqueta quicando: trêmulo que perde força",
             params={"velocidade": "golpes/s (padrão 20)"})
    def _t_chanzhu(self, gs, nota, rng, velocidade=20.0):
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.8, 0.65, 0.55, 0.5, 0.45], [], jitter=0.03,
                             fundir=True)

    @tecnica("qizhu", "齐竹", "oitava", descricao="as duas baquetas juntas (oitava abaixo)",
             params={"intervalo": "semitons abaixo (padrão 12)"})
    def _t_qizhu(self, gs, nota, rng, intervalo=12):
        base = gs[0]
        f = base.f0 * 2 ** (-float(intervalo) / 12)
        fake = type(nota)(**{**nota.__dict__, "f0": f, "corda": None, "curva": None})
        g = self.golpe_padrao(fake, rng)
        return [base, g]

    @tecnica("huazhu", "滑竹", "glissando", descricao="arrasta a baqueta pelas cordas", params={"semitons": "padrão 12",
                                                                                          "tempo": "s"})
    def _t_huazhu(self, gs, nota, rng, semitons=12, tempo=0.3):
        base = gs[0]
        out = []
        n = int(abs(semitons))
        sinal = 1 if semitons > 0 else -1
        for k in range(n + 1):
            i = int(np.clip(base.corda + sinal * k, 0, len(self.f_cordas) - 1))
            g = Golpe(**{**base.__dict__, "camadas": []})
            g.t0 = base.t0 + tempo * k / max(n, 1)
            g.corda, g.f0, g.curva, g.pan = i, self.f_cordas[i], CurvaAltura(), self.pan_corda(i)
            g.vel = base.vel * (0.5 + 0.5 * k / max(n, 1))
            g.dur = max(base.dur - (g.t0 - base.t0), 0.2)
            out.append(g)
        return out

    @tecnica("tanlun", "弹轮", "pizzicato", "拨弦", descricao="dedilha a corda com a ponta da baqueta/dedo (pizzicato)")
    def _t_pizz(self, gs, nota, rng):
        for g in gs:
            g.dureza = 0.5
            g.posicao = 0.2
            g.martelo = False
        return gs

    @tecnica("zhiyin", "止音", "abafar", descricao="a mão abafa o curso logo depois do golpe",
             params={"depois": "s até abafar (padrão: duração da nota)"})
    def _t_zhiyin(self, gs, nota, rng, depois=None):
        for g in gs:
            g.dur = float(depois) if depois is not None else nota.dur
            g.t60_soltura = 0.06
            g.sem_corte = False
        return gs
