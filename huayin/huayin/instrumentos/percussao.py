"""Percussão e sinos 打击乐: 编钟 bianzhong, 编磬 bianqing, 云锣 yunluo, 碰铃 pengling, 磬 qing,
大锣/小锣/抄锣 gongos, 钹 pratos, 堂鼓/大鼓/板鼓 tambores, 木鱼 muyu, 梆子 bangzi, 拍板 paiban."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..fisica.modal import Modo, ParamsModal, modos_barra_livre, modos_membrana, renderizar_modal
from .base import Instrumento, registrar, tecnica


@dataclass
class Batida:
    t0: float
    vel: float
    f0: float
    dur: float | None
    borda: float
    dureza: float
    t60_escala: float = 1.0
    extra: dict = field(default_factory=dict)


class PercussaoBase(Instrumento):
    familia = "percussão 打击乐"
    F0_PADRAO = 200.0        # altura quando a nota não tem altura (tambores, pratos)
    GANHO_SAIDA = 0.5
    PARAMETROS = {
        "afinacao": (0.0, "Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento)"),
        "dureza": (0.6, "baqueta macia (0) × dura (1)"),
        "borda": (0.0, "ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral"),
        "t60_escala": (1.0, "multiplica a sustentação"),
        "abafar": ("soar", "soar = deixa soar até o fim natural | nota = abafa no fim da nota"),
        "humanizar": (0.5, "variação de força e ponto entre golpes"),
        "pan": (0.0, "pan"),
        "largura": (0.0, "espalha notas agudas/graves no estéreo (conjuntos afinados)"),
        "ganho": (1.0, "ganho"),
    }

    def modos(self, b: Batida) -> list:
        raise NotImplementedError

    def params_modal(self, b: Batida) -> ParamsModal:
        return ParamsModal(b.f0, self.modos(b), vel=b.vel, dur=b.dur, borda=b.borda, dureza=b.dureza,
                           t60_escala=b.t60_escala * self.p["t60_escala"])

    def batida_padrao(self, nota, rng) -> Batida:
        f0 = nota.f0 if nota.f0 is not None else (self.p["afinacao"] or self.F0_PADRAO)
        h = self.p["humanizar"]
        dur = None if self.p["abafar"] == "soar" else nota.dur
        return Batida(nota.t0, float(np.clip(nota.vel * (1 + 0.05 * h * rng.standard_normal()), 0.02, 1)), f0, dur,
                      float(np.clip(self.p["borda"] + 0.05 * h * rng.standard_normal(), 0, 1)), self.p["dureza"])

    def renderizar(self, notas, n_total, rng):
        buf = np.zeros((2, n_total))
        for nota in notas:
            bs = self.aplicar_tecnicas([self.batida_padrao(nota, rng)], nota, rng)
            for b in bs:
                y = renderizar_modal(self.params_modal(b), self.sr, rng)
                y = self.pos_batida(y, b, rng)
                pan = self.p["pan"] if nota.pan is None else nota.pan
                if self.p["largura"] and b.f0:
                    pan = float(np.clip(pan + self.p["largura"] * (np.log2(b.f0 / 440) / 3), -1, 1))
                self._colocar(buf, y, b.t0, pan)
        return buf * self.p["ganho"] * self.GANHO_SAIDA

    def pos_batida(self, y, b, rng):
        return y

    # ------------------------------------------------------------------ técnicas comuns

    @tecnica("centro", "中心", descricao="golpe no centro/face")
    def _p_centro(self, bs, nota, rng):
        for b in bs:
            b.borda = 0.0
        return bs

    @tecnica("borda", "边", "lateral", descricao="golpe na borda/lateral: mais modos agudos")
    def _p_borda(self, bs, nota, rng):
        for b in bs:
            b.borda = 1.0
        return bs

    @tecnica("abafado", "闷", "muted", descricao="abafa logo depois do golpe", params={"tempo": "s (padrão 0.08)"})
    def _p_abafado(self, bs, nota, rng, tempo=0.08):
        for b in bs:
            b.dur = float(tempo)
        return bs

    @tecnica("soar", "延音", descricao="deixa soar até o fim natural")
    def _p_soar(self, bs, nota, rng):
        for b in bs:
            b.dur = None
        return bs

    @tecnica("baqueta_macia", "软槌", descricao="baqueta macia: som redondo, menos ataque")
    def _p_macia(self, bs, nota, rng):
        for b in bs:
            b.dureza = 0.15
        return bs

    @tecnica("baqueta_dura", "硬槌", descricao="baqueta dura: ataque brilhante")
    def _p_dura(self, bs, nota, rng):
        for b in bs:
            b.dureza = 1.0
        return bs

    @tecnica("rufo", "滚奏", "roll", "tremolo", descricao="rufo: golpes rápidos alternando as mãos",
             params={"velocidade": "golpes/s (padrão 18)", "cresc": "crescendo (ex.: 0.5 a 1.0) — 'de-ate'"})
    def _p_rufo(self, bs, nota, rng, velocidade=18.0, cresc=None):
        out = []
        de, ate = (1.0, 1.0)
        if cresc:
            de, ate = (float(x) for x in str(cresc).split("-"))
        for b in bs:
            t, k = 0.0, 0
            while t < nota.dur:
                u = t / max(nota.dur, 1e-6)
                nb = Batida(b.t0 + t, float(np.clip(b.vel * (de + (ate - de) * u) * (0.92 if k % 2 else 1.0)
                                                    * (1 + 0.06 * rng.standard_normal()), 0.02, 1)),
                            b.f0, b.dur, b.borda, b.dureza, b.t60_escala, dict(b.extra))
                out.append(nb)
                t += (1 + 0.05 * rng.standard_normal()) / velocidade
                k += 1
        return out

    @tecnica("flam", "装饰", descricao="dois golpes quase juntos (o primeiro mais fraco)", params={"tempo": "s (0.025)"})
    def _p_flam(self, bs, nota, rng, tempo=0.025):
        out = []
        for b in bs:
            g = Batida(b.t0 - tempo, b.vel * 0.55, b.f0, b.dur, b.borda, b.dureza, b.t60_escala, dict(b.extra))
            out += [g, b]
        return out


# ============================================================================= sinos e pedras afinados


@registrar
class Bianzhong(PercussaoBase):
    id = "bianzhong"
    nome = "Bianzhong (sinos do Marquês Yi)"
    nome_cn = "编钟"
    pinyin = "biānzhōng"
    descricao = ("Conjunto de sinos de bronze de seção amendoada (não redonda): cada sino dá DOIS tons — o 正鼓音, "
                 "batendo no centro da face, e o 侧鼓音, uma terça menor ou maior acima, batendo na lateral. As "
                 "saliências 枚 na superfície amortecem o som, e os sinos param rápido o bastante para tocar melodia.")
    historia = ("O conjunto do túmulo do Marquês Yi de Zeng (曾侯乙, ~433 a.C., achado em 1978): 65 sinos, ~5 oitavas, "
                "com inscrições de afinação. Rossing mediu intervalos entre os dois tons de ~210 a ~490 cents, em "
                "volta de 300 (terça menor) e 400 (terça maior).")
    extensao = ("C2", "D7")
    GANHO_SAIDA = 0.45
    PARAMETROS = {
        "dureza": (0.55, "malho de madeira em T"),
        "terca": ("alternada", "intervalo do 侧鼓音: menor | maior | alternada (como no conjunto de Zeng)"),
        "t60_base": (3.2, "T60 (s) do sino em dó4; graves soam mais, agudos menos"),
        "largura": (0.35, "graves à esquerda, agudos à direita"),
        "golpe": ("zheng", "zheng = 正鼓 (centro) | ce = 侧鼓 (lateral)"),
    }
    # razões dos modos (aproximações a partir dos modos de sinos de seção elíptica; cada modo circular
    # vira um par a/b). Pesos: quanto cada golpe excita o conjunto.
    MODOS_A = [(1.0, 1.0), (2.18, 0.45), (2.95, 0.32), (3.62, 0.26), (4.55, 0.17), (5.7, 0.1)]
    MODOS_B = [(1.0, 1.0), (2.12, 0.42), (2.88, 0.28), (3.7, 0.2), (4.7, 0.13)]

    def _terca(self, f0) -> float:
        t = self.p["terca"]
        if t == "menor":
            return 300.0
        if t == "maior":
            return 400.0
        m = int(round(69 + 12 * np.log2(f0 / 440.0)))
        return 300.0 if m % 2 == 0 else 400.0

    def batida_padrao(self, nota, rng):
        b = super().batida_padrao(nota, rng)
        b.extra["golpe"] = self.p["golpe"]
        return b

    def modos(self, b):
        terca = self._terca(b.f0)
        if b.extra.get("golpe") == "ce":
            # a nota pedida é o 侧鼓音: o sino tem o 正鼓音 uma terça abaixo
            fa, fb = b.f0 * 2 ** (-terca / 1200), b.f0
            pa, pb = 0.22, 1.0
        else:
            fa, fb = b.f0, b.f0 * 2 ** (terca / 1200)
            pa, pb = 1.0, 0.18
        t60 = self.p["t60_base"] * (261.6 / b.f0) ** 0.55
        out = []
        for k, (r, a) in enumerate(self.MODOS_A):
            out.append(Modo(r * fa / b.f0, t60 / (1 + 0.55 * k), a * pa, 1.0 + 0.3 * k, 0.0))
        for k, (r, a) in enumerate(self.MODOS_B):
            out.append(Modo(r * fb / b.f0, t60 * 0.9 / (1 + 0.55 * k), a * pb, 1.0 + 0.3 * k, 0.0))
        return out

    def params_modal(self, b):
        p = super().params_modal(b)
        p.batimento_cents = 2.5
        p.ruido_ataque = 0.06
        p.cor_ruido_hz = 2500
        return p

    @tecnica("zheng", "正鼓", "正鼓音", "centro", descricao="bate no centro da face: soa o tom principal (正鼓音)")
    def _b_zheng(self, bs, nota, rng):
        for b in bs:
            b.extra["golpe"] = "zheng"
        return bs

    @tecnica("ce", "侧鼓", "侧鼓音", "lateral", descricao="bate na lateral: soa o segundo tom, uma terça acima (侧鼓音)")
    def _b_ce(self, bs, nota, rng):
        for b in bs:
            b.extra["golpe"] = "ce"
        return bs

    @tecnica("tronco", "撞钟", descricao="sino grande batido com tronco de madeira: ataque grave e longo")
    def _b_tronco(self, bs, nota, rng):
        for b in bs:
            b.dureza = 0.2
            b.t60_escala = 1.4
            b.vel = min(1.0, b.vel * 1.2)
        return bs


@registrar
class Bianqing(PercussaoBase):
    id = "bianqing"
    nome = "Bianqing (pedras sonoras)"
    nome_cn = "编磬"
    pinyin = "biānqìng"
    descricao = ("Conjunto de lâminas de pedra calcária em forma de L penduradas numa moldura: som seco, cristalino "
                 "e curto, com modos de barra livre (bem inarmônicos). Música ritual 雅乐 junto com o 编钟.")
    historia = "O túmulo do Marquês Yi tinha 32 pedras afinadas. É o 'som da pedra' (石) da classificação 八音."
    extensao = ("A3", "A6")
    GANHO_SAIDA = 0.55
    PARAMETROS = {"dureza": (0.85, "malho duro"), "largura": (0.3, "estéreo"), "t60_base": (1.6, "T60 em lá4")}

    def modos(self, b):
        t60 = self.p["t60_base"] * (440 / b.f0) ** 0.4
        ms = modos_barra_livre(t60, 6)
        # a forma em L desdobra cada modo em dois próximos
        extra = [Modo(m.razao * 1.07, m.t60 * 0.7, m.amp * 0.35, m.peso_borda, 0.0) for m in ms[1:4]]
        return ms + extra

    def params_modal(self, b):
        p = super().params_modal(b)
        p.ruido_ataque = 0.12
        p.cor_ruido_hz = 5000
        p.t60_ruido = 0.015
        return p


@registrar
class Yunluo(PercussaoBase):
    id = "yunluo"
    nome = "Yunluo (gongos de nuvem)"
    nome_cn = "云锣"
    pinyin = "yúnluó"
    descricao = "Moldura com 10+ gonguinhos afinados de bronze: melodia brilhante, com leve subida de altura no ataque."
    extensao = ("D5", "D7")
    GANHO_SAIDA = 0.45
    PARAMETROS = {"dureza": (0.7, "baqueta"), "largura": (0.3, "estéreo")}

    def modos(self, b):
        rs = [(1.0, 1.0), (1.62, 0.35), (2.21, 0.3), (2.8, 0.2), (3.45, 0.15), (4.3, 0.1)]
        return [Modo(r, 2.4 / (1 + 0.5 * k), a, 1 + 0.2 * k, 1.0 if k == 0 else 0.4) for k, (r, a) in enumerate(rs)]

    def params_modal(self, b):
        p = super().params_modal(b)
        p.glide_cents = -35.0
        p.batimento_cents = 1.5
        return p


@registrar
class Pengling(PercussaoBase):
    id = "pengling"
    nome = "Pengling (sininhos de copo)"
    nome_cn = "碰铃"
    pinyin = "pènglíng"
    descricao = "Dois sininhos de copo de bronze presos por um cordão, batidos um no outro: agudo, longo, com batimento."
    extensao = ("C7", "C7")
    F0_PADRAO = 2350.0
    GANHO_SAIDA = 0.3
    PARAMETROS = {"dureza": (1.0, "bronze contra bronze")}

    def modos(self, b):
        rs = [(1.0, 1.0), (1.013, 0.8), (2.62, 0.4), (2.66, 0.3), (4.9, 0.15)]
        return [Modo(r, 3.2 / (1 + 0.6 * (k // 2)), a, 1.0, 0.0) for k, (r, a) in enumerate(rs)]


@registrar
class Qing(PercussaoBase):
    id = "qing"
    nome = "Qing (tigela de templo)"
    nome_cn = "磬"
    pinyin = "qìng"
    descricao = "Tigela de bronze dos templos budistas (铜磬), batida com bastão: ressonância longuíssima com batimentos."
    extensao = ("C3", "C6")
    F0_PADRAO = 320.0
    GANHO_SAIDA = 0.35
    PARAMETROS = {"dureza": (0.45, "bastão de madeira forrado"), "t60_base": (14.0, "T60 (s)")}

    def modos(self, b):
        rs = [(1.0, 1.0), (2.71, 0.55), (5.05, 0.3), (7.9, 0.15), (11.3, 0.08)]
        t = self.p["t60_base"]
        return [Modo(r, t / (1 + 0.9 * k), a, 1.0, 0.0) for k, (r, a) in enumerate(rs)]

    def params_modal(self, b):
        p = super().params_modal(b)
        p.batimento_cents = 3.0
        p.cauda_max = 20.0
        return p


# ============================================================================= gongos


class _Gongo(PercussaoBase):
    GLIDE = 0.0
    FLORESCER = 0.0
    T60 = 3.0
    N_ALEATORIO = 20
    FAIXA = (2.0, 12.0)
    RAZOES = [(1.0, 1.0), (1.48, 0.45), (1.96, 0.35), (2.31, 0.3), (2.73, 0.25), (3.2, 0.2), (3.62, 0.16), (4.3, 0.12)]

    def modos(self, b):
        return [Modo(r, self.T60 / (1 + 0.25 * k), a, 1 + 0.25 * k, 1.0 if k == 0 else 0.6)
                for k, (r, a) in enumerate(self.RAZOES)]

    def params_modal(self, b):
        p = super().params_modal(b)
        p.glide_cents = self.GLIDE * b.extra.get("glide", 1.0)
        p.florescer = self.FLORESCER
        p.n_aleatorio = self.N_ALEATORIO
        p.faixa_aleatoria = self.FAIXA
        p.t60_aleatorio = self.T60 * 0.5
        p.batimento_cents = 4.0
        p.ruido_ataque = 0.05
        p.cor_ruido_hz = 1500
        p.t60_abafado = 0.05
        p.cauda_max = self.T60 * 1.5 + 2
        return p

    @tecnica("sem_glide", "平音", descricao="golpe leve: quase sem glissando")
    def _g_sem(self, bs, nota, rng):
        for b in bs:
            b.extra["glide"] = 0.2
        return bs


@registrar
class Daluo(_Gongo):
    id = "daluo"
    nome = "Daluo (gongo grande da ópera)"
    nome_cn = "大锣"
    pinyin = "dàluó"
    descricao = ("Gongo de bronze da ópera de Pequim, batido com malho forrado: a altura CAI depois do golpe "
                 "(não linearidade geométrica do disco: quanto mais forte, mais cai). Marca entradas e momentos dramáticos.")
    F0_PADRAO = 190.0
    GLIDE = 260.0
    T60 = 3.5
    FLORESCER = 0.15
    PARAMETROS = {"dureza": (0.3, "malho forrado")}
    extensao = ("G2", "G4")


@registrar
class Xiaoluo(_Gongo):
    id = "xiaoluo"
    nome = "Xiaoluo (gongo pequeno da ópera)"
    nome_cn = "小锣"
    pinyin = "xiǎoluó"
    descricao = ("Gongo pequeno da ópera, batido com uma plaquinha de madeira: a altura SOBE depois do golpe "
                 "(centro plano mais fino: o disco amolece com a amplitude; Jossic et al., JASA 2018).")
    F0_PADRAO = 620.0
    GLIDE = -320.0
    T60 = 1.8
    N_ALEATORIO = 10
    PARAMETROS = {"dureza": (0.85, "plaquinha de madeira")}
    extensao = ("C5", "C6")


@registrar
class Chaoluo(_Gongo):
    id = "chaoluo"
    nome = "Chaoluo (tam-tam)"
    nome_cn = "抄锣"
    pinyin = "chāoluó"
    descricao = ("Gongo enorme sem altura definida: depois do golpe, a energia passa dos modos graves para os "
                 "agudos e o som 'floresce' num chiado brilhante que cresce antes de morrer (caos não linear).")
    F0_PADRAO = 55.0
    GLIDE = 40.0
    T60 = 8.0
    FLORESCER = 0.75
    N_ALEATORIO = 140
    FAIXA = (1.5, 80.0)
    GANHO_SAIDA = 0.3
    PARAMETROS = {"dureza": (0.25, "malho grande forrado")}
    extensao = ("A1", "A1")


# ============================================================================= pratos


class _Prato(PercussaoBase):
    GANHO_SAIDA = 0.3
    T60 = 2.0
    N = 160
    FAIXA = (3.0, 60.0)
    F0_PADRAO = 320.0

    def modos(self, b):
        return [Modo(1.0, self.T60 * 0.8, 0.3, 1.0, 0.3), Modo(1.53, self.T60 * 0.6, 0.25, 1.0, 0.3)]

    def params_modal(self, b):
        p = super().params_modal(b)
        p.n_aleatorio = self.N
        p.faixa_aleatoria = self.FAIXA
        p.t60_aleatorio = self.T60
        p.ruido_ataque = 0.6
        p.cor_ruido_hz = 5500
        p.t60_ruido = 0.25 * self.T60
        p.florescer = 0.15
        p.t60_abafado = 0.04
        return p

    def pos_batida(self, y, b, rng):
        # dois pratos batendo nunca se encontram por inteiro: um segundo contato 2–6 ms depois
        d = int(self.sr * (0.002 + 0.004 * rng.random()))
        z = np.zeros_like(y)
        z[d:] = 0.45 * y[:-d] if d < y.size else 0
        return y + z

    @tecnica("men", "闷", "abafado_pratos", descricao="pratos apertados um no outro: 'tchic' curto")
    def _c_men(self, bs, nota, rng):
        for b in bs:
            b.dur = 0.05
        return bs


@registrar
class Jingbo(_Prato):
    id = "jingbo"
    nome = "Jingbo (pratos da ópera)"
    nome_cn = "京钹"
    pinyin = "jīngbó"
    descricao = "Par de pratos médios da ópera de Pequim, com cúpula grande: brilhante e curto."
    T60 = 1.4
    extensao = ("E4", "E4")


@registrar
class Naobo(_Prato):
    id = "naobo"
    nome = "Naobo (pratos grandes)"
    nome_cn = "铙钹"
    pinyin = "náobó"
    descricao = "Pratos grandes de cúpula pequena (铙), dos templos e das procissões: longo e chiado."
    T60 = 3.2
    F0_PADRAO = 220.0
    N = 220
    extensao = ("A3", "A3")


@registrar
class Xiaobo(_Prato):
    id = "xiaobo"
    nome = "Xiaobo (pratos pequenos)"
    nome_cn = "小钹"
    pinyin = "xiǎobó"
    descricao = "Pratinhos agudos, brilhantes e curtos."
    T60 = 0.9
    F0_PADRAO = 700.0
    N = 120
    extensao = ("F5", "F5")


# ============================================================================= tambores


class _Tambor(PercussaoBase):
    T60 = 0.5
    GLIDE = 60.0
    AR = True

    def modos(self, b):
        return modos_membrana(self.T60, 10, self.AR)

    def params_modal(self, b):
        p = super().params_modal(b)
        p.glide_cents = self.GLIDE
        p.ruido_ataque = 0.25
        p.cor_ruido_hz = 1200
        p.t60_ruido = 0.02
        return p

    def pos_batida(self, y, b, rng):
        if b.extra.get("aro"):
            # 鼓边: golpe na borda de madeira — estalo seco por cima de pouca membrana
            n = int(0.02 * self.sr)
            t = np.arange(n) / self.sr
            clique = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1150, 1.0), (2450, 0.6), (3900, 0.3)))
            clique *= np.exp(-t / 0.006) * b.vel
            y = 0.25 * y
            y[:n] += clique
        return y

    @tecnica("aro", "鼓边", "gubian", "rim", descricao="bate na borda de madeira do tambor")
    def _t_aro(self, bs, nota, rng):
        for b in bs:
            b.extra["aro"] = True
        return bs


@registrar
class Tanggu(_Tambor):
    id = "tanggu"
    nome = "Tanggu (tambor de salão)"
    nome_cn = "堂鼓"
    pinyin = "tánggǔ"
    descricao = "Tambor de barril com duas peles de couro bovino pregadas, tocado com duas baquetas: grave e redondo."
    F0_PADRAO = 120.0
    T60 = 0.55
    PARAMETROS = {"dureza": (0.5, "baquetas de madeira")}
    extensao = ("C2", "C4")


@registrar
class Dagu(_Tambor):
    id = "dagu"
    nome = "Dagu (tambor grande)"
    nome_cn = "大鼓"
    pinyin = "dàgǔ"
    descricao = "Tambor enorme de templo e de guerra: grave profundo que se sente no peito."
    F0_PADRAO = 58.0
    T60 = 1.1
    GLIDE = 45.0
    GANHO_SAIDA = 0.7
    PARAMETROS = {"dureza": (0.3, "baquetas grossas")}
    extensao = ("A0", "A2")


@registrar
class Bangu(_Tambor):
    id = "bangu"
    nome = "Bangu (tambor do mestre da ópera)"
    nome_cn = "板鼓"
    pinyin = "bǎngǔ"
    descricao = ("Tamborzinho de uma pele só, muito esticada sobre um bloco grosso de madeira, tocado com duas "
                 "varetas finas de bambu: estalo seco e agudo. O tocador do 板鼓 rege a orquestra da ópera.")
    F0_PADRAO = 480.0
    T60 = 0.12
    GLIDE = 30.0
    AR = False
    PARAMETROS = {"dureza": (0.95, "varetas de bambu")}
    extensao = ("B4", "B4")


# ============================================================================= madeiras


class _Madeira(PercussaoBase):
    RAZOES = [(1.0, 1.0, 0.15), (2.57, 0.4, 0.08), (3.98, 0.2, 0.05)]

    def modos(self, b):
        return [Modo(r, t * self.p["t60_escala"], a, 1.0, 0.0) for r, a, t in self.RAZOES]

    def params_modal(self, b):
        p = super().params_modal(b)
        p.ruido_ataque = 0.3
        p.cor_ruido_hz = 2500
        p.t60_ruido = 0.006
        return p


@registrar
class Muyu(_Madeira):
    id = "muyu"
    nome = "Muyu (peixe de madeira)"
    nome_cn = "木鱼"
    pinyin = "mùyú"
    descricao = ("Bloco oco de madeira em forma de peixe, dos templos budistas (marca o ritmo das recitações): "
                 "'toc' com a cavidade ressoando. Tamanhos diferentes = alturas diferentes.")
    F0_PADRAO = 520.0
    GANHO_SAIDA = 0.6
    RAZOES = [(1.0, 1.0, 0.13), (1.0 * 2.43, 0.35, 0.06), (3.7, 0.15, 0.04)]
    PARAMETROS = {"dureza": (0.6, "baqueta de madeira com ponta")}
    extensao = ("C4", "C6")


@registrar
class Bangzi(_Madeira):
    id = "bangzi"
    nome = "Bangzi (bastões de madeira)"
    nome_cn = "梆子"
    pinyin = "bāngzi"
    descricao = "Dois bastões de madeira dura batidos um no outro: estalo agudo e penetrante das óperas do norte."
    F0_PADRAO = 1450.0
    GANHO_SAIDA = 0.5
    RAZOES = [(1.0, 1.0, 0.07), (2.7, 0.3, 0.03)]
    PARAMETROS = {"dureza": (1.0, "madeira dura")}
    extensao = ("F#6", "F#6")


@registrar
class Paiban(_Madeira):
    id = "paiban"
    nome = "Paiban (castanholas de tábuas)"
    nome_cn = "拍板"
    pinyin = "pāibǎn"
    descricao = ("Tábuas de madeira dura amarradas que batem juntas ('板' da ópera, junto com o 板鼓): marca o "
                 "tempo forte. Na corte Tang tinha 6 a 9 tábuas.")
    F0_PADRAO = 1100.0
    GANHO_SAIDA = 0.6
    RAZOES = [(1.0, 1.0, 0.05), (1.6, 0.6, 0.04), (2.9, 0.3, 0.03)]
    PARAMETROS = {"dureza": (1.0, "madeira")}
    extensao = ("C#6", "C#6")

    def pos_batida(self, y, b, rng):
        # as tábuas não batem todas juntas: 2–3 estalos em ~10 ms
        out = y.copy()
        for k in range(1, 3):
            d = int(self.sr * (0.003 + 0.004 * k * rng.random()))
            if d < y.size:
                out[d:] += (0.5 / k) * y[:-d]
        return out
