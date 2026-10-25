"""Base dos instrumentos de som contínuo (arco e sopro): erhu, dizi, suona, xiao...

Diferente das cordas dedilhadas, aqui o som é sustentado pelo músico o tempo todo. As notas
próximas viram uma FRASE renderizada de uma vez, com curvas por amostra:
  * f (Hz): notas + técnicas + portamento nas ligaduras (o dedo desliza: 滑音);
  * amp: velocidade do arco ou pressão do sopro (ataques, trocas de arco, golpes de língua);
  * brilho e ruido: cor do som ao longo da frase.
Assim os transientes de troca de arco e de língua saem do próprio modelo físico.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..composicao.curvas import CurvaAltura
from ..dsp.util import interp_pontos
from ..fisica.corpo import CORPOS
from .base import Instrumento, tecnica


@dataclass
class Segmento:
    t0: float
    t1: float
    f0: float
    vel: float
    curva: CurvaAltura
    legato: bool = False
    articulacao: str = "normal"     # normal | staccato | acento | sforzando | tenuto
    portamento: float | None = None
    env: list = field(default_factory=list)       # [(t_rel, multiplicador)] contorno extra de volume
    trocas: list = field(default_factory=list)    # [t_rel] trocas de arco / golpes de língua dentro da nota
    am: tuple | None = None                       # (taxa Hz, profundidade 0–1): 气震音, 花舌, trêmulo de arco
    brilho: float = 1.0
    ruido: float = 1.0
    extra: dict = field(default_factory=dict)
    nota: object = None


class ContinuoBase(Instrumento):
    polifonico = False
    CORPO_PADRAO = "sopro_bambu"
    GANHO_SAIDA = 1.0
    PARAMETROS = {
        "corpo": ("", "corpo ressonante; vazio = o do instrumento"),
        "mistura_corpo": (1.0, "0 = sem corpo, 1 = completo"),
        "ataque": (0.05, "tempo de ataque do começo de frase (s)"),
        "soltura": (0.12, "tempo de soltura do fim de frase (s)"),
        "portamento": (0.07, "duração dos deslizes de ligadura (s)"),
        "brilho": (0.5, "cor do som 0–1"),
        "ruido": (1.0, "multiplica o ruído de arco/sopro"),
        "vibrato": (0.0, "vibrato automático em notas longas (cents; 0 = desligado)"),
        "vibrato_taxa": (5.5, "Hz do vibrato automático"),
        "humanizar": (0.5, "pequenas instabilidades de afinação e volume"),
        "pan": (0.0, "posição no estéreo dentro da faixa"),
        "ganho": (1.0, "ganho de saída"),
        "intervalo_frase": (0.08, "silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco)"),
    }

    def configurar(self):
        self.corpo = CORPOS[self.p["corpo"] or self.CORPO_PADRAO]

    # ------------------------------------------------------------------ montagem

    def segmento_padrao(self, nota, rng) -> Segmento:
        curva = nota.curva.copiar() if nota.curva is not None else CurvaAltura()
        h = self.p["humanizar"]
        if h:
            curva.deriva = max(curva.deriva, 2.5 * h)
        if self.p["vibrato"] and nota.dur > 0.45:
            curva.vibrato(0.25, None, self.p["vibrato_taxa"], self.p["vibrato"], "simetrico", ataque=0.3)
        return Segmento(nota.t0, nota.t1, nota.f0, nota.vel, curva, nota.legato, nota=nota)

    def frases(self, segs: list[Segmento]) -> list[list[Segmento]]:
        out, atual = [], []
        for s in segs:
            if atual and (s.t0 - atual[-1].t1 > self.p["intervalo_frase"]) and not s.legato:
                out.append(atual)
                atual = []
            atual.append(s)
        if atual:
            out.append(atual)
        return out

    def renderizar(self, notas, n_total, rng):
        sr = self.sr
        buf = np.zeros((2, n_total))
        segs = []
        for nota in notas:
            if nota.f0 is None:
                continue
            s = self.segmento_padrao(nota, rng)
            s = self.aplicar_tecnicas(s, nota, rng)
            if isinstance(s, list):
                segs += s
            else:
                segs.append(s)
        segs.sort(key=lambda s: s.t0)
        # pizzicato e outros sons à parte (Segmento com extra['separado'])
        separados = [s for s in segs if s.extra.get("separado")]
        segs = [s for s in segs if not s.extra.get("separado")]
        i0, i1 = n_total, 0
        for fr in self.frases(segs):
            y, t_ini = self.renderizar_frase(fr, rng)
            self._colocar(buf, y, t_ini, self.p["pan"])
            i0 = min(i0, max(0, int(t_ini * sr)))
            i1 = max(i1, int(t_ini * sr) + y.size)
        for s in separados:
            y = self.renderizar_separado(s, rng)
            self._colocar(buf, y, s.t0, self.p["pan"])
            i0 = min(i0, max(0, int(s.t0 * sr)))
            i1 = max(i1, int(s.t0 * sr) + y.size)
        if i1 <= i0:
            return buf
        i1 = min(n_total, i1 + int(1.0 * sr))
        trecho = self.pos_processar(buf[:, i0:i1])
        buf[:, i0:i1] = self.corpo.aplicar(trecho, sr, self.p["mistura_corpo"])
        return buf * self.p["ganho"] * self.GANHO_SAIDA

    def renderizar_separado(self, s: Segmento, rng) -> np.ndarray:
        raise NotImplementedError

    def pos_processar(self, x):
        return x

    def renderizar_frase(self, fr: list[Segmento], rng):
        sr = self.sr
        ataque = self.p["ataque"]
        sol = self.p["soltura"]
        t_ini = max(0.0, fr[0].t0 - 0.005)
        t_fim = fr[-1].t1 + sol * 2.5 + 0.05
        n = int((t_fim - t_ini) * sr) + 1
        t = t_ini + np.arange(n) / sr
        logf = np.zeros(n)
        amp = np.zeros(n)
        din = np.zeros(n)
        brilho = np.zeros(n)
        ruido = np.zeros(n)
        direcao = np.ones(n)
        sentido = 1.0
        for k, s in enumerate(fr):
            prox = fr[k + 1] if k + 1 < len(fr) else None
            a = int((s.t0 - t_ini) * sr)
            b = int(((prox.t0 if prox else t_fim) - t_ini) * sr)
            b = min(max(b, a + 1), n)
            tt = np.arange(b - a) / sr
            cents = s.curva.avaliar(b - a, sr, rng)
            logf[a:b] = np.log2(s.f0) + cents / 1200
            if k == 0:
                logf[:a] = logf[a]
            # volume da nota
            nivel = self.nivel(s)
            dur = s.t1 - s.t0
            env = np.ones(b - a)
            if s.articulacao == "staccato":
                env *= np.clip((dur * 0.55 - tt) / 0.03, 0, 1)
            elif s.articulacao in ("acento", "sforzando"):
                pico, tau = (1.6, 0.08) if s.articulacao == "acento" else (2.0, 0.15)
                env *= 1 + (pico - 1) * np.exp(-tt / tau)
            if s.env:
                env *= interp_pontos(s.env, tt, "linear")
            if s.am:
                taxa, prof = s.am
                env *= 1 - prof * 0.5 * (1 - np.cos(2 * np.pi * taxa * tt))
            # fim da nota antes da próxima (silêncio curto entre notas destacadas)
            fim_rel = dur
            env *= np.clip((fim_rel + 0.01 - tt) / 0.03, 0, 1) if not (prox and prox.legato) else 1.0
            # re-articulação (troca de arco / golpe de língua) no começo de notas não ligadas
            if k > 0 and not s.legato:
                sentido = -sentido
                env *= self.rearticular(tt, s)
            elif k == 0:
                env *= np.clip(tt / max(ataque * (1.4 - s.vel), 0.004), 0, 1) ** 0.7
            for tr in s.trocas:
                m = tt >= tr
                env *= np.where(m, self.rearticular(tt - tr, s, interna=True), 1.0)
                direcao[a:b][m] *= -1
            amp[a:b] = nivel * env
            din[a:b] = s.vel
            direcao[a:b] *= sentido
            brilho[a:b] = s.brilho
            ruido[a:b] = s.ruido
        # portamento nas ligaduras: o dedo desliza da nota anterior até a nova (滑音)
        for k in range(1, len(fr)):
            s = fr[k]
            if not s.legato:
                continue
            port = s.portamento if s.portamento is not None else self.p["portamento"]
            nb = int(port * sr)
            c = int((s.t0 - t_ini) * sr)
            j0, j1 = max(0, c - nb // 2), min(n - 1, c + nb // 2)
            if j1 - j0 > 1:
                u = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, j1 - j0))
                logf[j0:j1] = logf[j0] + (logf[j1] - logf[j0]) * u
        # soltura no fim da frase
        ult = fr[-1]
        c = int((ult.t1 - t_ini) * sr)
        if c < n:
            tt = np.arange(n - c) / sr
            amp[c:] = amp[max(c - 1, 0)] * np.exp(-tt / max(sol / 3, 1e-3))
        if ult.articulacao != "staccato" and c < n:
            logf[c:] = logf[max(c - 1, 0)]
        if c < n:
            din[c:] = din[max(c - 1, 0)]
        # suaviza degraus (o dedo nunca troca de nota em zero segundos)
        from ..dsp.filtros import coef_um_polo, um_polo
        logf = um_polo(np.concatenate([np.full(64, logf[0]), logf]), coef_um_polo(80, sr))[64:]
        amp = um_polo(amp, coef_um_polo(120, sr))
        self.din = um_polo(din, coef_um_polo(20, sr))
        y = self.sintetizar(2 ** logf, amp, brilho * self.p["brilho"] * 2, ruido * self.p["ruido"],
                            direcao, fr, rng)
        return y, t_ini

    def nivel(self, s: Segmento) -> float:
        return s.vel

    def rearticular(self, tt, s, interna=False):
        """Multiplicador de volume no começo de uma nota não ligada (subclasses redefinem)."""
        return np.clip(tt / 0.02, 0.15, 1.0)

    def sintetizar(self, f, amp, brilho, ruido, direcao, frase, rng) -> np.ndarray:
        """f: Hz, amp: nivel(s) × envelope, brilho/ruido: multiplicadores, direcao: ±1 (arco),
        self.din: dinâmica (vel) por amostra. Devolve mono."""
        raise NotImplementedError

    # ------------------------------------------------------------------ técnicas comuns

    @tecnica("legato", "连", "ligado", descricao="liga à nota anterior (sem rearticular)")
    def _c_legato(self, s, nota, rng):
        s.legato = True
        return s

    @tecnica("staccato", "顿", "destacado", descricao="nota curta e separada")
    def _c_staccato(self, s, nota, rng):
        s.articulacao = "staccato"
        return s

    @tecnica("acento", ">", "重音", descricao="ataque mais forte")
    def _c_acento(self, s, nota, rng):
        s.articulacao = "acento"
        return s

    @tecnica("sforzando", "sfz", "突强", descricao="ataque muito forte que cai logo")
    def _c_sfz(self, s, nota, rng):
        s.articulacao = "sforzando"
        return s

    @tecnica("crescendo", "cresc", "渐强", descricao="cresce durante a nota", params={"de": "mult. inicial (0.3)",
                                                                                   "ate": "mult. final (1.3)"})
    def _c_cresc(self, s, nota, rng, de=0.3, ate=1.3):
        s.env = [(0.0, de), (s.t1 - s.t0, ate)]
        return s

    @tecnica("diminuendo", "dim", "渐弱", descricao="diminui durante a nota", params={"de": "1.2", "ate": "0.2"})
    def _c_dim(self, s, nota, rng, de=1.2, ate=0.2):
        s.env = [(0.0, de), (s.t1 - s.t0, ate)]
        return s

    @tecnica("vibrato", "揉", "rou", "颤", descricao="vibrato de afinação",
             params={"taxa": "Hz (padrão 5.8)", "prof": "cents (padrão 25)", "atraso": "s", "forma": "simetrico | acima | abaixo"})
    def _c_vibrato(self, s, nota, rng, taxa=5.8, prof=25.0, atraso=0.12, forma="simetrico"):
        s.curva.vibrato(atraso, None, taxa, prof, forma, ataque=0.25)
        return s

    @tecnica("trinado", "chanyin", "颤音", "trill", descricao="trinado com o dedo (alterna com a nota de cima)",
             params={"intervalo": "semitons (padrão 2)", "taxa": "batidas/s (padrão 9)", "atraso": "s"})
    def _c_trinado(self, s, nota, rng, intervalo=2.0, taxa=9.0, atraso=0.0):
        dur = s.t1 - s.t0
        t = atraso
        per = 1.0 / taxa
        c = 100.0 * float(intervalo)
        while t < dur - per:
            s.curva.para(t, 0.0, "degrau").para(t + 0.012, c, "rapido")
            s.curva.para(t + per * 0.5, c, "degrau").para(t + per * 0.5 + 0.012, 0.0, "rapido")
            t += per * (1 + 0.05 * rng.standard_normal())
        return s

    @tecnica("mordente", "dayin", "打音", descricao="toque rápido na nota vizinha logo no ataque",
             params={"intervalo": "semitons (padrão 2; negativo = abaixo)", "tempo": "s (padrão 0.05)"})
    def _c_mordente(self, s, nota, rng, intervalo=2.0, tempo=0.05):
        c = 100.0 * float(intervalo)
        s.curva.para(0.0, 0.0, "degrau").para(0.012, c, "rapido").para(0.012 + tempo, c, "degrau")
        s.curva.para(0.024 + tempo, 0.0, "rapido")
        return s

    @tecnica("apojatura", "dieyin", "叠音", "倚音", descricao="nota de passagem rápida de cima antes da nota",
             params={"intervalo": "semitons acima (padrão 2)", "tempo": "s (padrão 0.06)"})
    def _c_apoj(self, s, nota, rng, intervalo=2.0, tempo=0.06):
        s.curva.inicio_em(100.0 * float(intervalo)).para(tempo, 100.0 * float(intervalo), "degrau")
        s.curva.para(tempo + 0.015, 0.0, "rapido")
        return s

    @tecnica("slide_in", "shanghua", "上滑音", "绰", descricao="entra deslizando de baixo",
             params={"cents": "padrão 200", "tempo": "s (padrão 0.12)"})
    def _c_slide_in(self, s, nota, rng, cents=200.0, tempo=0.12):
        s.curva.inicio_em(-float(cents)).para(tempo, 0.0, "suave")
        return s

    @tecnica("slide_down_in", "xiahua", "下滑音", "注", descricao="entra deslizando de cima",
             params={"cents": "padrão 200", "tempo": "s"})
    def _c_slide_down(self, s, nota, rng, cents=200.0, tempo=0.12):
        s.curva.inicio_em(float(cents)).para(tempo, 0.0, "suave")
        return s

    @tecnica("queda", "fall", "下滑", descricao="cai de afinação no fim da nota", params={"cents": "padrão 300", "tempo": "s"})
    def _c_queda(self, s, nota, rng, cents=300.0, tempo=0.18):
        d = s.t1 - s.t0
        t = max(0.0, d - tempo)
        s.curva.para(t, s.curva.valor_em(t), "degrau").para(d, -float(cents), "suave")
        return s

    @tecnica("huihua", "回滑音", descricao="sobe e volta deslizando (ornamento vocal)",
             params={"cents": "padrão 200", "tempo": "s"})
    def _c_huihua(self, s, nota, rng, cents=200.0, tempo=0.12):
        s.curva.para(0.08, 0.0, "degrau").para(0.08 + tempo, float(cents), "suave").para(0.12 + 2 * tempo, 0.0, "suave")
        return s

    @tecnica("portamento", "滑", "glide", descricao="liga à anterior com deslize longo",
             params={"tempo": "duração do deslize (s, padrão 0.25)"})
    def _c_port(self, s, nota, rng, tempo=0.25):
        s.legato = True
        s.portamento = float(tempo)
        return s
