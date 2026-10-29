"""Sopros: 笛子 dizi, 箫 xiao, 埙 xun, 唢呐 suona, 管子 guanzi, 笙 sheng, 葫芦丝 hulusi, 巴乌 bawu."""
from __future__ import annotations

import numpy as np

from ..composicao.curvas import CurvaAltura
from ..fisica.corpo import CORPOS
from ..fisica.sopro import (membrana_dimo, renderizar_flauta, renderizar_palheta_conica,
                            renderizar_palheta_cilindrica, renderizar_palheta_livre, renderizar_vaso)
from .base import Instrumento, registrar, tecnica, variante
from .continuo_base import ContinuoBase


class SoproBase(ContinuoBase):
    familia = "sopros 吹管"

    def nivel(self, s):
        return 1.0  # amp = só o envelope; a dinâmica vem em self.din

    def rearticular(self, tt, s, interna=False):
        # golpe de língua (吐音): o ar para por ~20 ms e volta
        d = 0.022 if not interna else 0.016
        return np.clip((tt - d * 0.3) / (d * 0.7), 0.05, 1.0)

    # --------------------------------------------------------------- técnicas de sopro

    @tecnica("tuyin", "吐音", "lingua", descricao="golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo)",
             params={"tipo": "单 | 双 | 三", "velocidade": "golpes/s (padrão 8 / 12 / 12)"})
    def _s_tuyin(self, s, nota, rng, tipo="单", velocidade=None):
        v = float(velocidade or {"单": 8.0, "双": 12.0, "三": 12.0}.get(tipo, 8.0))
        d = s.t1 - s.t0
        t = 1.0 / v
        k = 0
        while t < d - 0.4 / v:
            s.trocas.append(t)
            k += 1
            # no 三吐 o ritmo é 'tu-tu-ku': dois rápidos e um mais longo
            passo = (0.75 if (tipo == "三" and k % 3 != 0) else 1.0) / v
            t += passo * (1 + 0.04 * rng.standard_normal())
        return s

    @tecnica("huashe", "花舌", "flatterzunge", "frullato", descricao="língua vibrando (rrrr): som rouco e agitado",
             params={"taxa": "Hz (padrão 26)", "prof": "0–1 (padrão 0.6)"})
    def _s_huashe(self, s, nota, rng, taxa=26.0, prof=0.6):
        s.am = (float(taxa), float(prof))
        s.ruido *= 2.0
        return s

    @tecnica("qizhenyin", "气震音", "vibrato_ar", descricao="vibrato de sopro: o volume pulsa (e a afinação um pouco)",
             params={"taxa": "Hz (padrão 5)", "prof": "0–1 (padrão 0.35)"})
    def _s_qizhen(self, s, nota, rng, taxa=5.0, prof=0.35):
        s.am = (float(taxa), float(prof))
        s.curva.vibrato(0.1, None, taxa, 8.0 * prof / 0.35, "simetrico", ataque=0.2)
        return s

    @tecnica("zengyin", "赠音", descricao="notinha rápida para cima no fim da nota (o 'suspiro' do dizi)",
             params={"intervalo": "semitons (padrão 3)"})
    def _s_zeng(self, s, nota, rng, intervalo=3.0):
        d = s.t1 - s.t0
        t = max(0.0, d - 0.06)
        s.curva.para(t, s.curva.valor_em(t), "degrau").para(t + 0.02, 100.0 * float(intervalo), "rapido")
        s.env = [(0.0, 1.0), (t, 1.0), (d, 0.15)]
        return s

    @tecnica("liyin", "历音", "corrida", descricao="corrida rápida de notas da escala que chega na nota",
             params={"notas": "quantas antes (padrão 5)", "tempo": "s (padrão 0.18)", "de": "baixo | cima"})
    def _s_liyin(self, s, nota, rng, notas=5, tempo=0.18, de="baixo"):
        passos = [0, 2, 4, 7, 9, 12, 14, 16]  # pentatônica
        k = int(notas)
        sinal = -1 if de == "baixo" else 1
        alvo_c = [sinal * 100.0 * (passos[min(k, len(passos) - 1)] - passos[min(i, len(passos) - 1)]) for i in range(k)]
        c = CurvaAltura([(0.0, alvo_c[0] if alvo_c else 0.0, "degrau")])
        for i, v in enumerate(alvo_c):
            c.para(tempo * i / k, v, "degrau")
        c.para(tempo, 0.0, "degrau")
        c.vibratos = s.curva.vibratos
        s.curva = c
        return s

    @tecnica("fanyin", "泛音", "harmonico", descricao="harmônico soprado: mais puro e mais soproso")
    def _s_fanyin(self, s, nota, rng):
        s.brilho *= 0.4
        s.ruido *= 1.8
        s.extra["harmonico"] = True
        return s

    @tecnica("forte_sopro", "强吹", descricao="sopro forçado: mais brilho e ruído")
    def _s_forte(self, s, nota, rng):
        s.brilho *= 1.5
        s.ruido *= 1.3
        return s


class FlautaBase(SoproBase):
    CORPO_PADRAO = "sopro_bambu"
    GANHO_SAIDA = 0.3
    MEMBRANA = True
    PARAMETROS = {
        "membrana": (0.35, "笛膜: quanto a membrana zumbe (0 = sem membrana)"),
        "f_membrana": (3200.0, "ressonância da membrana (Hz): tensão/rugas do 笛膜"),
        "ruido": (1.0, "sopro"),
        "ataque": (0.04, "ataque (s)"),
        "soltura": (0.09, "soltura (s)"),
        "portamento": (0.06, "deslize (s) — 滑音 cobrindo o furo aos poucos"),
        "vibrato": (0.0, "vibrato automático (cents)"),
        "brilho": (0.55, "cor"),
        "razao_jato": (0.32, "atraso do jato/tubo (avançado)"),
    }

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng):
        if float(np.min(f)) < 285 and not getattr(self, "_avisou", False):
            # v1.0: abaixo de ~290 Hz o modelo de jato pula de modo (medido em tests/test_afinacao_fisica.py)
            import warnings
            warnings.warn(f"[{self.id}] notas abaixo de ré4 (~290 Hz) ficam instáveis no modelo de flauta")
            self._avisou = True
        din = self.din
        env = np.clip(amp, 0, 1.6)
        # a pressão só cai abaixo do limiar de oscilação nos golpes de língua e no fim; o 花舌 e o
        # 气震音 modulam o volume sem apagar o jato (env × 3 satura antes)
        sopro = np.clip(env * 3.0, 0, 1.0) * (0.89 + 0.1 * din)
        harm = any(s.extra.get("harmonico") for s in frase)
        br = float(np.clip(np.median(brilho) * 0.5 * (0.8 + 0.4 * float(np.median(din))), 0.05, 1.0))
        rs = 0.06 * float(np.median(ruido)) * (1.25 - 0.5 * float(np.median(din))) * (1.6 if harm else 1.0)
        y = renderizar_flauta(f, sopro, self.sr, rng, razao_jato=self.p["razao_jato"], ruido_sopro=rs, brilho=br)
        if self.MEMBRANA and self.p["membrana"] > 0:
            y = membrana_dimo(y, self.sr, self.p["f_membrana"], 0.08, 4.0, 1.0,
                              self.p["membrana"] * (0.5 + 0.8 * float(np.median(din))))
        g = (0.3 + 0.7 * din) * np.clip(env, 0, 1.6) ** 0.5
        return y * g


@registrar
class Dizi(FlautaBase):
    id = "dizi"
    nome = "Dizi (qudi)"
    nome_cn = "笛子"
    pinyin = "dízi"
    descricao = ("Flauta transversal de bambu com 6 furos e um furo extra coberto por uma membrana fina de junco "
                 "(笛膜). A membrana vibra e dá o zumbido brilhante que é a assinatura do dizi. 曲笛 (qudi, do sul, "
                 "doce, ópera Kunqu) é o padrão; use 'bangdi' para o agudo do norte.")
    historia = ("Flautas de osso de 9000 anos foram achadas em Jiahu (贾湖骨笛). O dizi com membrana aparece na "
                "dinastia Tang/Song. Peças: 鹧鸪飞, 姑苏行, 喜相逢.")
    extensao = ("A4", "E7")


@registrar
class Xiao(FlautaBase):
    id = "xiao"
    nome = "Xiao"
    nome_cn = "箫"
    pinyin = "xiāo"
    descricao = ("Flauta vertical de bambu soprada pela ponta (como a shakuhachi, que descende dela): grave, "
                 "velada, muito ar no som. Sem membrana. Parceira clássica do guqin (琴箫合奏).")
    extensao = ("D4", "D6")
    MEMBRANA = False
    GANHO_SAIDA = 0.33
    PARAMETROS = {"ruido": (1.9, "muito ar"), "brilho": (0.28, "escuro"), "ataque": (0.09, "ataque macio"),
                  "membrana": (0.0, "o xiao não tem membrana"), "soltura": (0.16, "soltura"),
                  "portamento": (0.1, "deslize")}


@registrar
class Xun(SoproBase):
    id = "xun"
    nome = "Xun"
    nome_cn = "埙"
    pinyin = "xūn"
    descricao = ("Flauta de vaso de cerâmica em forma de ovo (ocarina antiga): ressonador de Helmholtz, som "
                 "quase sem harmônicos, oco e melancólico, com muito ar.")
    historia = "Um dos instrumentos mais antigos da China: exemplares de ~7000 anos (cultura Yangshao)."
    extensao = ("G3", "C6")
    GANHO_SAIDA = 0.35
    CORPO_PADRAO = "sopro_bambu"
    PARAMETROS = {"ruido": (1.0, "ar"), "ataque": (0.08, "ataque"), "soltura": (0.15, "soltura"),
                  "portamento": (0.08, "deslize")}

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng):
        din = self.din
        a = np.clip(amp, 0, 1.6) * (0.25 + 0.75 * din)
        return renderizar_vaso(f, a, self.sr, rng, ruido_sopro=0.12 * float(np.median(ruido)))


@registrar
class Suona(SoproBase):
    id = "suona"
    nome = "Suona"
    nome_cn = "唢呐"
    pinyin = "suǒnà"
    descricao = ("Oboé de palheta dupla com tubo cônico de madeira e campana de cobre: o instrumento mais alto da "
                 "China, de casamentos, funerais e festas. O músico controla a palheta com os lábios e faz "
                 "deslizes enormes, imitações de pássaros e de voz.")
    historia = "Chegou da Pérsia/Ásia Central (surnay) por volta da dinastia Jin/Yuan. Peça: 百鸟朝凤 (Cem pássaros saúdam a fênix)."
    extensao = ("D4", "A6")
    CORPO_PADRAO = "suona"
    GANHO_SAIDA = 0.55
    PARAMETROS = {"ruido": (1.0, "sopro"), "brilho": (0.65, "cor"), "ataque": (0.03, "ataque"),
                  "soltura": (0.07, "soltura"), "portamento": (0.12, "deslize de lábio"),
                  "vibrato": (18.0, "vibrato de lábio automático (cents)"), "vibrato_taxa": (6.5, "Hz")}

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng):
        din = self.din
        env = np.clip(amp, 0, 1.6)
        sopro = np.clip(env * 2.5, 0, 1.0) * (0.5 + 0.22 * din)
        br = float(np.clip(np.median(brilho) * 0.5, 0.1, 1.0))
        y = renderizar_palheta_conica(f, sopro, self.sr, rng, posicao=0.4, brilho=br,
                                      ruido_sopro=0.05 * float(np.median(ruido)))
        return y * (0.35 + 0.65 * din) * np.clip(env, 0, 1.6) ** 0.5

    @tecnica("yayin", "压音", "labio", descricao="aperta a palheta com os lábios: a nota cai e volta",
             params={"cents": "quanto cai (padrão 150)", "tempo": "s"})
    def _su_yayin(self, s, nota, rng, cents=150.0, tempo=0.15):
        s.curva.para(0.08, 0, "degrau").para(0.08 + tempo, -float(cents), "suave").para(0.12 + 2 * tempo, 0, "suave")
        return s

    @tecnica("niaoming", "鸟鸣", "passaro", descricao="canto de pássaro: trinados rápidos e deslizes agudos (百鸟朝凤)")
    def _su_passaro(self, s, nota, rng):
        d = s.t1 - s.t0
        t = 0.0
        while t < d - 0.05:
            sobe = 300 + 400 * rng.random()
            s.curva.para(t, 0.0, "degrau").para(t + 0.03, sobe, "rapido").para(t + 0.07, 0.0, "suave")
            t += 0.08 + 0.05 * rng.random()
        s.am = (14.0, 0.25)
        return s


@registrar
class Guanzi(SoproBase):
    id = "guanzi"
    nome = "Guanzi"
    nome_cn = "管子"
    pinyin = "guǎnzi"
    descricao = ("Tubo cilíndrico curto com palheta dupla larga: som rouco, lamentoso e cheio de deslizes. "
                 "Na dinastia Tang era o 觱篥 (bili) da orquestra da corte; o hichiriki do gagaku descende dele.")
    extensao = ("G3", "C6")
    CORPO_PADRAO = "sopro_bambu"
    GANHO_SAIDA = 0.5
    PARAMETROS = {"brilho": (0.45, "cor"), "portamento": (0.14, "deslize"), "vibrato": (25.0, "vibrato"),
                  "vibrato_taxa": (5.0, "Hz"), "ataque": (0.04, "ataque")}

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng):
        din = self.din
        env = np.clip(amp, 0, 1.6)
        sopro = np.clip(env * 2.5, 0, 1.0) * (0.55 + 0.25 * din)
        br = float(np.clip(np.median(brilho) * 0.5, 0.1, 1.0))
        y = renderizar_palheta_cilindrica(f, sopro, self.sr, rng, brilho=br,
                                          ruido_sopro=0.05 * float(np.median(ruido)))
        return y * (0.35 + 0.65 * din) * np.clip(env, 0, 1.6) ** 0.5


variante("bangdi", "dizi", "Dizi bangdi 梆笛", "dizi curto e agudo do norte (ópera 梆子): mais brilhante e zumbido forte",
         membrana=0.5, f_membrana=3800.0, brilho=0.7)
variante("bili", "guanzi", "Bili 觱篥 (Tang)", "o guanzi da orquestra da corte Tang: mais suave", brilho=0.35,
         vibrato=12.0)


# ============================================================================= palheta livre (polifônico)


class PalhetaLivreBase(Instrumento):
    familia = "sopros de palheta livre 簧管"
    polifonico = True
    PARAMETROS = {
        "abertura": (0.35, "fração do ciclo com a fenda aberta (menor = mais brilhante)"),
        "ressonancia": (0.6, "quanto o tubo acima da palheta reforça os harmônicos"),
        "impar": (0.0, "puxa para harmônicos ímpares (som de clarinete)"),
        "ruido": (1.0, "sopro"),
        "ataque": (0.05, "ataque (s)"),
        "soltura": (0.08, "soltura (s)"),
        "bordao": ("", "nota de bordão contínuo (hulusi: tubo extra); vazio = sem"),
        "vibrato": (0.0, "vibrato automático (cents)"),
        "pan": (0.0, "pan"),
        "ganho": (1.0, "ganho"),
    }
    GANHO_SAIDA = 0.5
    CORPO_PADRAO = "sopro_bambu"

    def configurar(self):
        self.corpo = CORPOS[self.CORPO_PADRAO]

    def renderizar(self, notas, n_total, rng):
        sr = self.sr
        buf = np.zeros((2, n_total))
        i0, i1 = n_total, 0
        tocadas = []
        for nota in notas:
            if nota.f0 is None:
                continue
            itens = self.aplicar_tecnicas([dict(f0=nota.f0, t0=nota.t0, dur=nota.dur, vel=nota.vel,
                                                curva=(nota.curva.copiar() if nota.curva else CurvaAltura()),
                                                am=None, trocas=[])], nota, rng)
            for it in itens:
                y = self._uma(it, rng)
                self._colocar(buf, y, it["t0"], self.p["pan"])
                tocadas.append((it["t0"], it["t0"] + it["dur"]))
                i0 = min(i0, int(it["t0"] * sr))
                i1 = max(i1, int(it["t0"] * sr) + y.size)
        if self.p["bordao"] and tocadas:
            self._bordao(buf, tocadas, rng)
        if i1 <= i0:
            return buf
        i1 = min(n_total, i1 + int(0.5 * sr))
        buf[:, i0:i1] = self.corpo.aplicar(buf[:, i0:i1], sr)
        return buf * self.p["ganho"] * self.GANHO_SAIDA

    def _uma(self, it, rng):
        sr = self.sr
        n = int((it["dur"] + self.p["soltura"] * 3) * sr)
        t = np.arange(n) / sr
        cents = it["curva"].avaliar(n, sr, rng)
        if self.p["vibrato"] and it["dur"] > 0.4:
            cents = cents + self.p["vibrato"] * np.sin(2 * np.pi * 5.0 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
        f = it["f0"] * 2 ** (cents / 1200)
        env = np.clip(t / self.p["ataque"], 0, 1) * np.where(t < it["dur"], 1.0,
                                                               np.exp(-(t - it["dur"]) / (self.p["soltura"] / 3)))
        for tr in it["trocas"]:
            env *= np.where(t >= tr, np.clip((t - tr - 0.006) / 0.014, 0.05, 1.0), 1.0)
        if it["am"]:
            taxa, prof = it["am"]
            env *= 1 - prof * 0.5 * (1 - np.cos(2 * np.pi * taxa * t))
        # palheta livre fica um pouco mais aguda com sopro forte (até ~15 cents)
        f *= 2 ** ((10 * (it["vel"] - 0.5)) / 1200)
        y = renderizar_palheta_livre(f, env * (0.3 + 0.7 * it["vel"]), sr, rng, self.p["abertura"],
                                     self.p["ressonancia"], self.p["impar"], 0.03 * self.p["ruido"])
        return y

    def _bordao(self, buf, tocadas, rng):
        f = self.afinacao.hz(self.p["bordao"])
        regioes = []
        for a, b in sorted(tocadas):
            if regioes and a - regioes[-1][1] < 0.4:
                regioes[-1][1] = max(regioes[-1][1], b)
            else:
                regioes.append([a, b])
        for a, b in regioes:
            it = dict(f0=f, t0=a, dur=b - a, vel=0.4, curva=CurvaAltura(), am=None, trocas=[])
            self._colocar(buf, 0.55 * self._uma(it, rng), a, self.p["pan"])

    # --------------------------------------------------------------- técnicas

    @tecnica("hesheng", "和音", "harmonia", descricao="acrescenta notas do acorde tradicional do sheng (quinta e oitava)",
             params={"intervalos": "semitons separados por espaço (padrão '-5 -12': quarta e oitava abaixo)"})
    def _p_hesheng(self, itens, nota, rng, intervalos="-5 -12"):
        extra = []
        for it in itens:
            for s in str(intervalos).split():
                novo = dict(it)
                novo["f0"] = it["f0"] * 2 ** (float(s) / 12)
                novo["vel"] = it["vel"] * 0.8
                novo["curva"] = it["curva"].copiar()
                extra.append(novo)
        return itens + extra

    @tecnica("tuyin", "吐音", "lingua", descricao="golpes de língua repetindo a nota",
             params={"velocidade": "golpes/s (padrão 8)"})
    def _p_tuyin(self, itens, nota, rng, velocidade=8.0):
        for it in itens:
            t = 1.0 / velocidade
            while t < it["dur"] - 0.4 / velocidade:
                it["trocas"].append(t)
                t += 1.0 / velocidade
        return itens

    @tecnica("huashe", "花舌", "flatterzunge", descricao="língua vibrando (rrrr)", params={"taxa": "Hz (26)"})
    def _p_huashe(self, itens, nota, rng, taxa=26.0):
        for it in itens:
            it["am"] = (float(taxa), 0.6)
        return itens

    @tecnica("chanyin", "颤音", "vibrato_ar", descricao="vibrato de sopro (volume pulsando)",
             params={"taxa": "Hz (5)", "prof": "0–1 (0.3)"})
    def _p_chan(self, itens, nota, rng, taxa=5.0, prof=0.3):
        for it in itens:
            it["am"] = (float(taxa), float(prof))
        return itens

    @tecnica("dayin", "打音", "mordente", descricao="toque rápido na nota de cima no ataque")
    def _p_dayin(self, itens, nota, rng):
        for it in itens:
            it["curva"].para(0.0, 0, "degrau").para(0.01, 200, "degrau").para(0.05, 200, "degrau").para(0.06, 0, "degrau")
        return itens

    @tecnica("bend", "滑音", descricao="palhetas livres dobram pouco: até ~meio tom com o sopro",
             params={"cents": "padrão -60", "tempo": "s"})
    def _p_bend(self, itens, nota, rng, cents=-60.0, tempo=0.2):
        for it in itens:
            it["curva"].para(0.1, 0, "degrau").para(0.1 + tempo, float(cents), "suave")
        return itens


@registrar
class Sheng(PalhetaLivreBase):
    id = "sheng"
    nome = "Sheng"
    nome_cn = "笙"
    pinyin = "shēng"
    descricao = ("Órgão de boca: 17 a 37 tubos de bambu numa cabaça, cada um com uma palheta livre de latão. "
                 "Toca acordes (tradicionalmente quartas, quintas e oitavas) e soa tanto soprando quanto "
                 "aspirando. Ancestral do acordeão e da harmônica.")
    historia = "Há sheng em túmulos de 2400 anos (曾侯乙墓). Na corte Tang era central; o shō do gagaku descende dele."
    extensao = ("G3", "A6")
    GANHO_SAIDA = 0.3
    PARAMETROS = {"abertura": (0.32, "fenda"), "ressonancia": (0.65, "tubo"), "ataque": (0.04, "ataque")}


@registrar
class Hulusi(PalhetaLivreBase):
    id = "hulusi"
    nome = "Hulusi"
    nome_cn = "葫芦丝"
    pinyin = "húlúsī"
    descricao = ("Flauta de cabaça com palheta livre do povo Dai (Yunnan): som doce, de clarinete, com um tubo "
                 "de bordão que fica soando junto.")
    extensao = ("F4", "C6")
    GANHO_SAIDA = 0.6
    PARAMETROS = {"abertura": (0.5, "fenda"), "ressonancia": (0.5, "tubo"), "impar": (0.35, "som de clarinete"),
                  "bordao": ("", "nota do tubo de bordão (ex.: 'C5'); vazio = desligado"),
                  "vibrato": (12.0, "vibrato suave"), "ataque": (0.06, "ataque")}


@registrar
class Bawu(PalhetaLivreBase):
    id = "bawu"
    nome = "Bawu"
    nome_cn = "巴乌"
    pinyin = "bāwū"
    descricao = "Flauta transversal de palheta livre do sudoeste (Yi, Miao, Hani): som soproso, doce e anasalado."
    extensao = ("G4", "C6")
    GANHO_SAIDA = 0.6
    PARAMETROS = {"abertura": (0.45, "fenda"), "ressonancia": (0.45, "tubo"), "impar": (0.2, "ímpares"),
                  "ruido": (2.2, "muito ar"), "vibrato": (10.0, "vibrato"), "ataque": (0.07, "ataque")}
