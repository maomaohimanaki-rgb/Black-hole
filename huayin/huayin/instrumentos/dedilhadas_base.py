"""Base das cordas dedilhadas (弹拨乐器): pipa, guqin, guzheng, ruan, liuqin, sanxian, konghou, yangqin.

Fluxo de uma nota:
  nota → escolhe a corda → golpe padrão → técnicas (podem virar vários golpes: 轮指, 扫, 刮奏)
  → corta golpes na mesma corda (o dedo que volta abafa a vibração anterior)
  → guia de onda por golpe (+ ruído de deslizar o dedo, batidas, cliques)
  → corpo do instrumento (uma vez na soma) → ressonância simpática das cordas soltas.
"""
from __future__ import annotations

import numpy as np

from ..composicao.curvas import CurvaAltura
from ..dsp import filtros as F
from ..dsp.kernels import kernel_pentes
from ..dsp.util import ruido
from ..fisica.corda import MATERIAIS, ParamsCorda, amostras_golpe, renderizar_corda
from ..fisica.corpo import CORPOS
from .base import Golpe, Instrumento, tecnica


class CordaDedilhadaBase(Instrumento):
    familia = "cordas dedilhadas 弹拨"
    AFINACOES: dict = {}
    AFINACAO_PADRAO = ""
    MODO_ALTURA = "trastes"       # trastes | livre | cordas_fixas
    TRASTES: list | None = None   # semitons disponíveis sobre a corda solta (None = cromático)
    ALCANCE = 24                  # semitons alcançáveis acima da corda solta
    MAX_PRESSAO = 0               # cordas_fixas: cents que a mão esquerda consegue subir (按音)
    CURSO = 1                     # cordas por nota (yangqin tem 2–5 em uníssono, yueqin 2)
    DESAFINACAO_CURSO = 1.5       # cents entre as cordas do mesmo curso (dá o "coro" natural)
    MARTELO = False               # corda percutida em vez de pinçada

    PARAMETROS = {
        "afinacao": ("", "nome da afinação ou lista de notas das cordas (grave → agudo)"),
        "material": ("aco_nylon", "seda | seda_fina | aco_nylon | aco | tripa"),
        "corpo": ("", "corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento"),
        "mistura_corpo": (1.0, "0 = corda crua, 1 = corpo completo"),
        "posicao": (0.12, "ponto de dedilhado (fração da corda a partir da ponte): menor = mais metálico"),
        "dureza": (0.7, "0 = polpa do dedo, 1 = unha/palheta dura"),
        "largura": (0.25, "abertura estéreo entre as cordas (0 = mono)"),
        "simpatia": (0.06, "ressonância simpática das cordas soltas (0–0.3)"),
        "t60_escala": (1.0, "multiplica a sustentação (0.5 = corda abafada/velha)"),
        "t60_soltura": (0.15, "quanto a nota demora a morrer quando o dedo abafa (s)"),
        "abafar": ("nota", "nota = abafa no fim da nota | soar = deixa soar até repetir a corda"),
        "modulacao_tensao": (6.0, "cents que um dedilhado forte sobe no ataque (física da tensão)"),
        "ruido_ataque": (0.04, "ruído do contato da unha/palheta"),
        "humanizar": (0.5, "variação aleatória de ponto, força e afinação (0 = robô)"),
        "comprimento": (0.7, "comprimento vibrante da corda solta (m) — usado no ruído de deslize"),
        "portamento": (0.12, "duração padrão dos slides (s)"),
        "ganho": (1.0, "ganho de saída"),
    }

    def configurar(self):
        af = self.p["afinacao"] or self.AFINACAO_PADRAO
        if isinstance(af, str):
            if af not in self.AFINACOES:
                raise ValueError(f"[{self.id}] afinação '{af}' não existe. Opções: {', '.join(self.AFINACOES)}")
            notas = self.AFINACOES[af]
        else:
            notas = list(af)
        self.notas_cordas = notas
        self.material = MATERIAIS[self.p["material"]] if isinstance(self.p["material"], str) else self.p["material"]
        self.corpo = CORPOS[self.p["corpo"] or self.CORPO_PADRAO]

    CORPO_PADRAO = "pipa"

    def preparar(self, afinacao):
        super().preparar(afinacao)
        # as cordas seguem o temperamento da música (三分损益, justa...) e o lá de referência
        self.f_cordas = [afinacao.hz(n) for n in self.notas_cordas]

    # ------------------------------------------------------------------ cordas

    def pan_corda(self, i: int) -> float:
        n = len(self.f_cordas)
        if n <= 1:
            return 0.0
        return (i / (n - 1) - 0.5) * self.p["largura"]

    def escolher_corda(self, f: float, nota) -> tuple[int, float]:
        """Devolve (corda, cents de pressão extra). Pressão > 0 só em trastes discretos/cordas fixas."""
        fc = self.f_cordas
        if nota.corda is not None:
            i = int(np.clip(nota.corda, 0, len(fc) - 1))
            return i, 0.0
        cents = [1200 * np.log2(f / x) for x in fc]
        if self.MODO_ALTURA == "cordas_fixas":
            # corda mais próxima por baixo que a mão esquerda consegue empurrar até a nota
            ok = [i for i, c in enumerate(cents) if -15 <= c <= self.MAX_PRESSAO + 15]
            if ok:
                i = min(ok, key=lambda k: cents[k])
                return i, max(cents[i], 0.0)
            i = int(np.argmin(np.abs(cents)))
            return i, 0.0
        ok = [i for i, c in enumerate(cents) if -15 <= c <= self.ALCANCE * 100 + 15]
        if not ok:
            return (0 if cents[0] < 0 else len(fc) - 1), 0.0
        i = min(ok, key=lambda k: cents[k])  # menor posição de mão (corda mais aguda possível)
        if self.TRASTES is not None:
            semis = cents[i] / 100
            abaixo = [t for t in self.TRASTES if t <= semis + 0.15]
            if abaixo:
                tr = max(abaixo)
                extra = (semis - tr) * 100
                if extra > 20:
                    # entre trastes: o músico aperta a corda atrás do traste até subir (推)
                    return i, extra
        return i, 0.0

    # ------------------------------------------------------------------ golpes

    def golpe_padrao(self, nota, rng) -> Golpe:
        i, pressao = self.escolher_corda(nota.f0, nota)
        h = self.p["humanizar"]
        curva = nota.curva.copiar() if nota.curva is not None else CurvaAltura()
        f_ref = nota.f0
        if pressao > 0:
            # nota feita apertando a corda (按音 / entre trastes): o golpe é na altura da nota já
            # apertada, com uma pequena acomodação do dedo nos primeiros ~60 ms
            curva.inicio_em(-min(12.0, pressao * 0.1)).para(0.06, 0.0, "rapido")
        return Golpe(
            t0=nota.t0, dur=nota.dur, corda=i, f0=f_ref, vel=float(np.clip(nota.vel * (1 + h * 0.06 * rng.standard_normal()), 0.02, 1.0)),
            curva=curva,
            posicao=float(np.clip(self.p["posicao"] * (1 + h * 0.08 * rng.standard_normal()), 0.03, 0.5)),
            dureza=self.p["dureza"], ruido_ataque=self.p["ruido_ataque"],
            t60_escala=self.p["t60_escala"], t60_soltura=self.p["t60_soltura"],
            pan=self.pan_corda(i) if nota.pan is None else nota.pan,
        )

    # técnicas que ligam a nota à anterior sem novo ataque → tempo de transição (None = portamento)
    LIGADURAS = {"hammer": 0.0, "puxada": 0.0, "deslizar": None}

    def _tecnica_de_ligadura(self, nota):
        for nome, ps in nota.tecnicas:
            info = self.resolver_tecnica(nome)
            if info.nome in self.LIGADURAS:
                t = ps.get("tempo", ps.get("_", self.LIGADURAS[info.nome]))
                return self.p["portamento"] if t is None else float(t)
        return None

    def _emendar_legato(self, ant: Golpe, nota, rng, transicao=None) -> bool:
        """Liga a nota à anterior sem novo ataque (上/下/滑 no guqin, 打/带 no pipa)."""
        if ant is None or ant.mudo or nota.t0 > ant.t0 + ant.dur + 0.08:
            return False
        f_solta = self.f_cordas[ant.corda]
        semis = 12 * np.log2(nota.f0 / f_solta)
        if semis < -0.3 or semis > self.ALCANCE + 0.3:
            return False
        if self.MODO_ALTURA == "cordas_fixas" and semis * 100 > self.MAX_PRESSAO + 15:
            return False
        desloc = 1200 * np.log2(nota.f0 / ant.f0)
        if transicao is None:
            transicao = float(nota.params.get("slide", self.p["portamento"] if abs(desloc) > 60 else 0.03))
        nova = nota.curva.copiar() if nota.curva is not None else CurvaAltura()
        ant.curva = ant.curva.emendar(nova, nota.t0 - ant.t0, desloc, transicao)
        ant.dur = nota.t1 - ant.t0
        ant.deslize = ant.deslize or transicao > 0.04
        if transicao == 0.0:
            # 打 (hammer-on): o dedo batendo no traste/corda dá um pequeno impulso
            ant.camadas.append(("clique", {"nivel": 0.15, "forca": nota.vel, "_t": nota.t0 - ant.t0}))
        return True

    def preparar_golpes(self, notas, rng) -> list[Golpe]:
        golpes: list[Golpe] = []
        ultimo: Golpe | None = None
        for nota in notas:
            if nota.f0 is None:
                continue
            lig = self._tecnica_de_ligadura(nota)
            if (nota.legato or lig is not None) and self._emendar_legato(ultimo, nota, rng, lig):
                continue
            if lig is not None:
                # sem nota anterior para ligar: vira um ataque comum, sem a técnica de ligadura
                nota = type(nota)(**{**nota.__dict__, "tecnicas": [t for t in nota.tecnicas
                                                                    if self.resolver_tecnica(t[0]).nome not in self.LIGADURAS]})
            gs = [self.golpe_padrao(nota, rng)]
            gs = self.aplicar_tecnicas(gs, nota, rng)
            golpes += gs
            if gs:
                ultimo = max(gs, key=lambda g: g.t0)
        if self.p["abafar"] == "soar":
            # deixa soar: a nota vive até morrer sozinha, a menos que a corda seja tocada de novo
            for g in golpes:
                if not g.mudo:
                    g.dur = max(g.dur, 1.05 * float(self.material.t60(g.f0 * max(g.harmonico, 1))) * g.t60_escala)
        # o mesmo dedo/corda voltando abafa a vibração anterior
        por_corda: dict = {}
        for g in sorted(golpes, key=lambda g: g.t0):
            ant = por_corda.get(g.corda)
            if ant is not None and not ant.sem_corte and not g.mudo and g.t0 < ant.t0 + ant.dur:
                ant.dur = max(g.t0 - ant.t0 + 0.004, 0.005)
                ant.t60_soltura = min(ant.t60_soltura, 0.04)
            if not g.mudo:
                por_corda[g.corda] = g
        return golpes

    # ------------------------------------------------------------------ render

    def renderizar(self, notas, n_total, rng):
        sr = self.sr
        buf = np.zeros((2, n_total))
        golpes = self.preparar_golpes(notas, rng)
        i0, i1 = n_total, 0
        for g in golpes:
            y = self.renderizar_golpe(g, rng, n_total)
            if y is not None:
                self._colocar(buf, y, g.t0, g.pan)
                i0 = min(i0, max(0, int(g.t0 * sr)))
                i1 = max(i1, int(g.t0 * sr) + y.size)
        if i1 <= i0:
            return buf
        # corpo e simpatia só na região que tem som (+ a cauda do corpo e das cordas soltas)
        i1 = min(n_total, i1 + int(3 * sr))
        trecho = buf[:, i0:i1]
        mono = 0.5 * (trecho[0] + trecho[1])
        out = self.corpo.aplicar(trecho, sr, self.p["mistura_corpo"])
        if self.p["simpatia"] > 0 and np.any(mono):
            out = out + self._simpatia(mono, notas)
        buf[:, i0:i1] = out
        buf[:, i1:] = 0.0
        return buf * self.p["ganho"]

    def params_corda(self, g: Golpe, n_max) -> ParamsCorda:
        return ParamsCorda(
            f0=g.f0, dur=g.dur, vel=g.vel, posicao=g.posicao, dureza=g.dureza, material=self.material,
            t60_escala=g.t60_escala, t60_soltura=g.t60_soltura, modulacao_tensao=self.p["modulacao_tensao"],
            ruido_ataque=g.ruido_ataque, contato=g.contato, harmonico=g.harmonico,
            f_solta=self.f_cordas[g.corda], martelo=self.MARTELO if g.martelo is None else g.martelo,
            contato_ms=self.contato_ms(g), reexcitacoes=list(g.reexcitacoes))

    def curso_da_nota(self, g: Golpe) -> int:
        return self.CURSO

    def contato_ms(self, g: Golpe) -> float:
        return 1.5 - g.dureza

    def renderizar_golpe(self, g: Golpe, rng, n_total):
        sr = self.sr
        y = None
        if not g.mudo:
            pc = self.params_corda(g, n_total)
            n_max = n_total - int(g.t0 * sr)
            pc.cents = g.curva.avaliar(amostras_golpe(pc, sr, n_max), sr, rng)
            y = renderizar_corda(pc, sr, rng, n_max=n_max)
            curso = self.curso_da_nota(g)
            if curso > 1:
                # cordas do mesmo curso: desafinadas de leve, batidas quase juntas → batimento e
                # decaimento em dois estágios (como no piano e no yangqin)
                soma = y.copy()
                for k in range(1, curso):
                    d = self.DESAFINACAO_CURSO * (k - (curso - 1) / 2) * (1 + 0.3 * rng.standard_normal())
                    pk = ParamsCorda(**{**pc.__dict__, "cents": pc.cents + d,
                                        "vel": pc.vel * (0.9 + 0.2 * rng.random())})
                    yk = renderizar_corda(pk, sr, rng, n_max=n_max)
                    n = min(soma.size, yk.size)
                    soma[:n] += yk[:n]
                y = soma / np.sqrt(curso)
            if g.deslize and self.material.ruido_atrito > 0:
                y = y + self._ruido_deslize(pc.cents[:y.size], self.f_cordas[g.corda], g.f0, g.vel, rng)
        for tipo, ps in g.camadas:
            ps = dict(ps)
            atraso = int(ps.pop("_t", 0.0) * sr)
            c = np.concatenate([np.zeros(atraso), self.camada(tipo, g, rng, **ps)])
            if y is None:
                y = c
            else:
                n = max(y.size, c.size)
                y = np.pad(y, (0, n - y.size)) + np.pad(c, (0, n - c.size))
        return y

    # ------------------------------------------------------------------ camadas de ruído

    def camada(self, tipo: str, g: Golpe, rng, **ps) -> np.ndarray:
        sr = self.sr
        forca = ps.get("forca", g.vel)
        if tipo == "batida":
            # dedo/palheta batendo no tampo: o corpo (aplicado depois) dá a cor de madeira
            n = int(0.03 * sr)
            r = ruido(n, rng) * np.exp(-np.arange(n) / (0.004 * sr))
            r = F.passa_baixa(r, ps.get("brilho", 2500), sr)
            t = np.arange(n) / sr
            baque = np.sin(2 * np.pi * ps.get("f", 140) * t) * np.exp(-t / 0.012)
            return forca * (0.8 * r + 1.2 * baque)
        if tipo == "clique":
            n = int(0.006 * sr)
            r = F.passa_alta(ruido(n, rng), 3000, sr) * np.exp(-np.arange(n) / (0.0008 * sr))
            return forca * ps.get("nivel", 0.3) * r
        if tipo == "rasgo":
            # 裂帛: "os quatro fios num só som, como seda rasgando" (白居易, 琵琶行)
            d = ps.get("dur", 0.09)
            n = int(d * sr)
            t = np.arange(n) / sr
            r = ruido(n, rng) * (np.abs(rng.standard_normal(n)) ** 0.5)
            r = F.passa_banda(r, 2600, sr, 0.5)
            env = np.minimum(t / 0.004, 1) * np.exp(-t / (d * 0.45))
            return forca * 0.9 * r * env
        raise ValueError(f"camada desconhecida: {tipo}")

    def _ruido_deslize(self, cents, f_solta, f0, vel, rng) -> np.ndarray:
        """Atrito do dedo deslizando na corda enrolada (Penttinen et al. 2006, guqin): o ruído tem
        uma ressonância cuja frequência = velocidade do dedo × enrolamentos por metro."""
        sr = self.sr
        n = cents.size
        f = f0 * 2 ** (cents / 1200)
        L = self.p["comprimento"] * f_solta / np.maximum(f, 1.0)
        v = np.abs(np.gradient(L) * sr)
        v = F.um_polo(v, F.coef_um_polo(30, sr))
        if v.max() < 1e-3:
            return np.zeros(n)
        fc = np.clip(v * max(self.material.enrolamentos_por_m, 300), 80, 6000)
        r = ruido(n, rng)
        out = np.zeros(n)
        bloco = 256
        zi = np.zeros((1, 2))
        from scipy.signal import sosfilt
        for i in range(0, n, bloco):
            sos = F.biquad("passa_banda", float(fc[min(i + bloco // 2, n - 1)]), sr, 4.0)
            out[i:i + bloco], zi = sosfilt(sos, r[i:i + bloco], zi=zi)
        amp = np.clip(v / 0.3, 0, 1) ** 0.8
        return self.material.ruido_atrito * 0.08 * (0.3 + vel) * out * amp

    def _simpatia(self, mono: np.ndarray, notas=()) -> np.ndarray:
        """Cordas soltas que vibram por simpatia. Em instrumentos com muitas cordas, só as ~10 mais
        aparentadas (uníssono, oitava, quinta) com as notas tocadas — as outras quase não respondem."""
        sr = self.sr
        fs = [f for f in self.f_cordas if f < 0.4 * sr]
        if len(fs) > 10 and notas:
            def afinidade(fc):
                s = 0.0
                for n in notas:
                    if n.f0 is None:
                        continue
                    r = n.f0 / fc if n.f0 > fc else fc / n.f0
                    k = round(r)
                    if 1 <= k <= 4 and abs(1200 * np.log2(r / k)) < 20:
                        s += 1.0 / k
                return s
            fs = sorted(fs, key=afinidade, reverse=True)[:10]
        if not fs:
            return np.zeros((2, mono.size))
        ativo = np.nonzero(np.abs(mono) > 1e-6)[0]
        if ativo.size == 0:
            return np.zeros((2, mono.size))
        i0, i1 = ativo[0], min(mono.size, ativo[-1] + int(3 * sr))
        atrasos = np.array([sr / f - 0.5 for f in fs])
        t60 = np.array([float(self.material.t60(f)) * 0.5 for f in fs])
        ganhos = 10 ** (-3 * atrasos / (t60 * sr))
        y = np.zeros(mono.size)
        y[i0:i1] = kernel_pentes(mono[i0:i1] * 0.02, atrasos, ganhos, 0.35, int(atrasos.max()) + 8)
        y = self.corpo.aplicar(y, sr, self.p["mistura_corpo"]) * self.p["simpatia"] * 8
        return np.vstack([y, y]) * np.sqrt(0.5)

    # ------------------------------------------------------------------ técnicas comuns
    # (todas recebem e devolvem a lista de golpes)

    @tecnica("tan", "弹", "dedilhar", descricao="dedilhado simples (padrão)")
    def _t_tan(self, gs, nota, rng):
        return gs

    @tecnica("hammer", "da", "打", "ligado", descricao="liga à nota anterior batendo o dedo (sem dedilhar)")
    def _t_hammer(self, gs, nota, rng):
        return gs

    @tecnica("puxada", "dai", "带", "pull_off", descricao="liga à nota anterior puxando o dedo (sem dedilhar)")
    def _t_puxada(self, gs, nota, rng):
        return gs

    @tecnica("deslizar", "hua", "滑", "shang", "上", "xia", "下", "slide",
             descricao="desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce)",
             params={"tempo": "duração do deslize (s)"})
    def _t_deslizar(self, gs, nota, rng, tempo=None):
        return gs

    @tecnica("abafado", "muted", "闷", descricao="corda abafada pela mão: som curto e surdo",
             params={"quanto": "0–1 (padrão 0.8)"})
    def _t_abafado(self, gs, nota, rng, quanto=0.8):
        for g in gs:
            g.t60_escala *= max(0.03, 1 - quanto)
            g.dureza *= 1 - 0.5 * quanto
        return gs

    @tecnica("fanyin", "泛音", "harmonico", descricao="harmônico natural: dedo encostado no nó da corda",
             params={"n": "número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura"})
    def _t_fanyin(self, gs, nota, rng, n=None):
        for g in gs:
            if n is not None:
                # n dado: a nota escrita é a fundamental (corda solta ou apertada = harmônico
                # artificial) e soa n vezes mais aguda
                g.harmonico = int(n)
                continue
            # sem n: a nota escrita é a que SOA; procura a corda solta e o harmônico que a dão
            melhor = None
            for i, fs in enumerate(self.f_cordas):
                for k in range(2, 9):
                    err = abs(1200 * np.log2(nota.f0 / (fs * k)))
                    if err < 35 and (melhor is None or err < melhor[0]):
                        melhor = (err, i, k)
            if melhor is None:
                k = max(2, int(round(nota.f0 / self.f_cordas[g.corda])))
                i = g.corda
            else:
                _, i, k = melhor
            g.corda, g.harmonico = i, k
            g.f0 = nota.f0 / k
            g.pan = self.pan_corda(i)
            g.dureza = min(1.0, g.dureza + 0.1)
        return gs

    @tecnica("vibrato", "yin", "吟", "rou", "揉", descricao="vibrato da mão esquerda",
             params={"taxa": "Hz (padrão 5.5)", "prof": "cents (padrão 25)", "atraso": "s antes de começar",
                     "forma": "acima | simetrico | abaixo"})
    def _t_vibrato(self, gs, nota, rng, taxa=5.5, prof=25.0, atraso=0.12, forma="acima"):
        for g in gs:
            g.curva.vibrato(atraso, None, taxa, prof, forma, ataque=0.2)
        return gs

    @tecnica("bend", "tui", "推", "la", "拉", descricao="empurra/puxa a corda depois do ataque e sobe a afinação",
             params={"cents": "quanto sobe (padrão 200)", "tempo": "duração da subida (s)", "atraso": "s antes"})
    def _t_bend(self, gs, nota, rng, cents=200.0, tempo=0.15, atraso=0.05):
        for g in gs:
            v = g.curva.valor_em(atraso)
            g.curva.para(atraso, v, "degrau").para(atraso + tempo, v + cents, "suave")
        return gs

    @tecnica("bend_volta", "tuifu", "推复", "lafu", "拉复", descricao="sobe e volta (推复/拉复)",
             params={"cents": "padrão 200", "tempo": "s de cada movimento", "atraso": "s"})
    def _t_bend_volta(self, gs, nota, rng, cents=200.0, tempo=0.12, atraso=0.05):
        for g in gs:
            v = g.curva.valor_em(atraso)
            g.curva.para(atraso, v, "degrau").para(atraso + tempo, v + cents, "suave")
            g.curva.para(atraso + 2.5 * tempo, v + cents, "degrau").para(atraso + 3.5 * tempo, v, "suave")
        return gs

    @tecnica("pre_bend", "huiyin", "回音", descricao="começa já esticada e desce até a nota",
             params={"cents": "padrão 200", "tempo": "s"})
    def _t_pre_bend(self, gs, nota, rng, cents=200.0, tempo=0.18):
        for g in gs:
            g.curva.inicio_em(cents).para(0.03, cents, "degrau").para(0.03 + tempo, 0.0, "suave")
        return gs

    @tecnica("slide_in", "chuo", "绰", descricao="entra na nota deslizando de baixo (绰)",
             params={"cents": "de quanto abaixo (padrão 150)", "tempo": "s"})
    def _t_chuo(self, gs, nota, rng, cents=150.0, tempo=0.12):
        for g in gs:
            g.curva.inicio_em(-cents).para(tempo, 0.0, "rapido")
            g.deslize = True
        return gs

    @tecnica("slide_down_in", "zhu", "注", descricao="entra na nota deslizando de cima (注)",
             params={"cents": "de quanto acima (padrão 150)", "tempo": "s"})
    def _t_zhu(self, gs, nota, rng, cents=150.0, tempo=0.12):
        for g in gs:
            g.curva.inicio_em(cents).para(tempo, 0.0, "rapido")
            g.deslize = True
        return gs

    @tecnica("glissando_saida", "xiahua", "下滑", descricao="no fim da nota desliza para baixo (cai)",
             params={"cents": "padrão 300", "tempo": "s"})
    def _t_queda(self, gs, nota, rng, cents=300.0, tempo=0.2):
        for g in gs:
            t = max(0.02, g.dur - tempo)
            g.curva.para(t, g.curva.valor_em(t), "degrau").para(g.dur, -cents, "suave")
            g.deslize = True
        return gs

    @tecnica("acento", ">", "重音", descricao="ataque mais forte e brilhante", params={"quanto": "0–1"})
    def _t_acento(self, gs, nota, rng, quanto=0.35):
        for g in gs:
            g.vel = min(1.0, g.vel * (1 + quanto))
            g.dureza = min(1.0, g.dureza + 0.2 * quanto)
        return gs

    @tecnica("posicao", "ponto", descricao="muda o ponto do dedilhado (perto da ponte = metálico)",
             params={"valor": "fração 0.03–0.5"})
    def _t_posicao(self, gs, nota, rng, valor=0.12):
        for g in gs:
            g.posicao = float(valor)
        return gs

    @tecnica("soar", "let_ring", "延音", descricao="deixa a nota soar até a corda ser tocada de novo")
    def _t_soar(self, gs, nota, rng):
        for g in gs:
            g.dur = max(g.dur, 20.0)
        return gs

    @tecnica("arpejo", "琶音", descricao="acorde arpejado: toca a nota em várias cordas em sequência",
             params={"notas": "intervalos em semitons separados por espaço, ex.: '0 7 12'",
                     "intervalo": "s entre cordas"})
    def _t_arpejo(self, gs, nota, rng, notas="0 7 12", intervalo=0.04):
        base = gs[0]
        out = []
        for k, s in enumerate(str(notas).split()):
            f = nota.f0 * 2 ** (float(s) / 12)
            fake = type(nota)(**{**nota.__dict__, "f0": f, "corda": None})
            g = self.golpe_padrao(fake, rng)
            g.t0 = base.t0 + k * intervalo
            g.dur = max(base.dur - k * intervalo, 0.05)
            g.vel = base.vel * (0.9 + 0.1 * rng.random())
            out.append(g)
        return out

    @tecnica("tremolo", "tremolo_simples", descricao="repetição rápida e regular da nota",
             params={"velocidade": "golpes por segundo (padrão 14)"})
    def _t_tremolo(self, gs, nota, rng, velocidade=14.0):
        return self._repetir(gs, nota, rng, velocidade, [1.0, 0.85], [0.0, 0.0])

    def _repetir(self, gs, nota, rng, velocidade, forcas, dur_extra, posicoes=None, dureza=None,
                 jitter=0.08, fundir=False) -> list[Golpe]:
        """Transforma cada golpe numa sequência (trêmulo). forcas/posicoes ciclam (dedos diferentes).

        fundir=True: os golpes não abafam a corda (baqueta do yangqin), então viram UM golpe com
        várias excitações somadas no mesmo laço."""
        if fundir:
            for g in gs:
                t, k, ex = 1.0 / velocidade, 1, []
                while t < g.dur - 0.3 / velocidade:
                    v = g.vel * forcas[k % len(forcas)] * (1 + 0.07 * rng.standard_normal())
                    ex.append((t, float(np.clip(v, 0.02, 1.0))))
                    t += (1 + jitter * rng.standard_normal()) / velocidade
                    k += 1
                g.reexcitacoes = ex
            return gs
        out = []
        for g in gs:
            t, k = 0.0, 0
            per = 1.0 / velocidade
            while t < g.dur - per * 0.3:
                ng = Golpe(**{**g.__dict__, "camadas": list(g.camadas)})
                ng.t0 = g.t0 + t
                ng.dur = min(per * 1.05, g.dur - t)
                ng.vel = g.vel * forcas[k % len(forcas)] * (1 + 0.07 * rng.standard_normal())
                ng.vel = float(np.clip(ng.vel, 0.02, 1.0))
                if posicoes:
                    ng.posicao = posicoes[k % len(posicoes)]
                if dureza:
                    ng.dureza = dureza[k % len(dureza)]
                # a curva continua de onde estava (bend/vibrato sobre o trêmulo inteiro)
                ng.curva = g.curva.deslocar(-t)
                ng.camadas = g.camadas if k == 0 else []
                out.append(ng)
                t += per * (1 + jitter * rng.standard_normal())
                k += 1
            if not out or out[-1].t0 < g.t0:
                out.append(g)
            # a última batida pode soar até o fim da nota
            out[-1].dur = g.t0 + g.dur - out[-1].t0
        return out

