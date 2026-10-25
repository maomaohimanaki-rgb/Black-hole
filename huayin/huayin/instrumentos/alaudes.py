"""Alaúdes de palheta: 阮 Ruan, 柳琴 Liuqin, 月琴 Yueqin e 三弦 Sanxian."""
from __future__ import annotations

from .base import registrar, tecnica, variante
from .pipa import _PipaComum


class _AlaudePalheta(_PipaComum):
    """Técnicas de palheta (拨片) dos alaúdes modernos da orquestra chinesa."""

    @tecnica("baixo", "下拨", "tan", "弹", descricao="palheta para baixo (forte)")
    def _t_baixo(self, gs, nota, rng):
        return gs

    @tecnica("cima", "上拨", "tiao", "挑", descricao="palheta para cima (um pouco mais fraca)")
    def _t_cima(self, gs, nota, rng):
        for g in gs:
            g.vel *= 0.85
            g.posicao = min(0.5, g.posicao + 0.015)
        return gs

    @tecnica("yaozhi", "摇指", "lun", "轮", "tremolo", descricao="trêmulo de palheta (o 'sustain' dos alaúdes chineses)",
             params={"velocidade": "golpes por segundo (padrão 14)"})
    def _t_yaozhi(self, gs, nota, rng, velocidade=14.0):
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.82], [], jitter=0.05)

    @tecnica("sao", "扫", descricao="varre todas as cordas para baixo", params={"intervalo": "s", "acorde": "semitons"})
    def _t_sao(self, gs, nota, rng, intervalo=0.01, acorde=None):
        return self._estrumar(gs, nota, rng, +1, intervalo, None, acorde)

    @tecnica("fu", "拂", descricao="varre todas as cordas para cima", params={"intervalo": "s", "acorde": "semitons"})
    def _t_fu(self, gs, nota, rng, intervalo=0.012, acorde=None):
        out = self._estrumar(gs, nota, rng, -1, intervalo, None, acorde)
        for g in out:
            g.vel *= 0.85
        return out


@registrar
class Ruan(_AlaudePalheta):
    id = "ruan"
    nome = "Zhongruan"
    nome_cn = "中阮"
    pinyin = "zhōngruǎn"
    descricao = ("Alaúde de caixa redonda com 4 cordas e 24 trastes, tocado com palheta. Som quente, de "
                 "'violão chinês', com graves redondos da caixa com duas bocas.")
    historia = ("Chamado 秦琵琶 na dinastia Han; o nome vem de 阮咸, um dos Sete Sábios do Bosque de Bambu. "
                "Um ruan de Tang está em Shōsōin.")
    extensao = ("G2", "D5")
    AFINACOES = {"moderna": ["G2", "D3", "G3", "D4"], "quartas": ["G2", "C3", "G3", "C4"]}
    AFINACAO_PADRAO = "moderna"
    CORPO_PADRAO = "ruan"
    ALCANCE = 24
    PARAMETROS = {
        "material": ("aco_nylon", "material"),
        "dureza": (0.8, "palheta"),
        "posicao": (0.18, "ponto"),
        "largura": (0.15, "estéreo"),
        "comprimento": (0.6, "m"),
        "t60_escala": (1.1, "sustentação"),
    }


@registrar
class Liuqin(_AlaudePalheta):
    id = "liuqin"
    nome = "Liuqin"
    nome_cn = "柳琴"
    pinyin = "liǔqín"
    descricao = "Pequeno alaúde em pera ('folha de salgueiro'), 4 cordas de aço, palheta: o soprano brilhante dos dedilhados."
    historia = "Nasceu no folclore de Shandong/Jiangsu como acompanhamento da ópera 柳琴戏."
    extensao = ("G3", "G6")
    AFINACOES = {"moderna": ["G3", "D4", "G4", "D5"]}
    AFINACAO_PADRAO = "moderna"
    CORPO_PADRAO = "liuqin"
    ALCANCE = 24
    PARAMETROS = {
        "material": ("aco", "cordas de aço"),
        "dureza": (0.95, "palheta"),
        "posicao": (0.12, "ponto"),
        "largura": (0.1, "estéreo"),
        "comprimento": (0.38, "m"),
    }


@registrar
class Yueqin(_AlaudePalheta):
    id = "yueqin"
    nome = "Yueqin"
    nome_cn = "月琴"
    pinyin = "yuèqín"
    descricao = ("'Viola da lua': caixa redonda chata, braço curtíssimo, 2 cursos de cordas duplas. Na ópera "
                 "de Pequim acompanha o 京胡 com um som seco e metálico.")
    extensao = ("A3", "E6")
    AFINACOES = {"opera": ["A3", "E4"], "quinta": ["D4", "A4"]}
    AFINACAO_PADRAO = "opera"
    CORPO_PADRAO = "liuqin"
    CURSO = 2
    DESAFINACAO_CURSO = 3.0
    ALCANCE = 19
    PARAMETROS = {
        "material": ("aco", "aço"),
        "dureza": (0.95, "palheta"),
        "posicao": (0.15, "ponto"),
        "largura": (0.1, "estéreo"),
        "t60_escala": (0.6, "caixa chata: notas curtas"),
        "comprimento": (0.35, "m"),
    }


@registrar
class Sanxian(_AlaudePalheta):
    id = "sanxian"
    nome = "Sanxian"
    nome_cn = "三弦"
    pinyin = "sānxián"
    descricao = ("Alaúde de 3 cordas sem trastes, braço longo e caixa pequena coberta de pele de cobra: ataque "
                 "de banjo, médios nasais e deslizes livres. Ancestral do shamisen japonês.")
    historia = "Popular desde a dinastia Yuan; acompanha 评弹 de Suzhou, 大鼓 do norte e a ópera."
    extensao = ("G2", "G5")
    AFINACOES = {"quinta_quarta": ["G2", "D3", "G3"], "quarta_quinta": ["G2", "C3", "G3"],
                 "dasanxian": ["D2", "A2", "D3"]}
    AFINACAO_PADRAO = "quinta_quarta"
    CORPO_PADRAO = "sanxian"
    MODO_ALTURA = "livre"
    ALCANCE = 26
    PARAMETROS = {
        "material": ("tripa", "seda/tripa grossa"),
        "dureza": (0.9, "palheta/unha"),
        "posicao": (0.08, "toca bem perto da ponte, sobre a pele"),
        "largura": (0.1, "estéreo"),
        "comprimento": (0.95, "m"),
        "t60_escala": (0.75, "a pele absorve energia"),
        "portamento": (0.1, "deslizes"),
    }

    @tecnica("pele", "sawari", "chiado", descricao="a corda encosta de leve e chia (zumbido de pele/ponte)",
             params={"quanto": "0–1 (padrão 0.3)"})
    def _t_pele(self, gs, nota, rng, quanto=0.3):
        for g in gs:
            g.contato = 0.25 * float(quanto)
        return gs


variante("daruan", "ruan", "Daruan 大阮", "o ruan baixo da orquestra", afinacao=["D2", "A2", "D3", "A3"],
         comprimento=0.8, t60_escala=1.2)
variante("xiaoruan", "ruan", "Xiaoruan 小阮", "o ruan soprano", afinacao=["D3", "A3", "D4", "A4"],
         comprimento=0.45)
