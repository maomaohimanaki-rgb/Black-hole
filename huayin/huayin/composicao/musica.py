"""Musica (a peça inteira) e Faixa (um instrumento/músico): sequenciador, mixer e exportação.

    import huayin as hy
    m = hy.Musica("Teste", tempo=72, tom="1=D")
    pipa = m.faixa("pipa", "pipa", pan=-0.3)
    pipa.nota("A3", 0, 1, vel=0.7)
    pipa.nota("D4", 1, 2, tecnica="lun")
    m.exportar("teste.wav")
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .. import efeitos as FX
from ..afinacao import Afinacao, Tom
from ..dsp.util import db_para_lin, fade, lufs_integrado, normalizar_pico, pan_ganhos, pico
from ..instrumentos import criar
from ..instrumentos.base import Instrumento
from .curvas import Automacao, CurvaAltura
from .nota import DINAMICAS, Nota, NotaR
from .tempo import MapaTempo


class Faixa:
    def __init__(self, musica: "Musica", nome: str, instrumento, volume_db: float = 0.0, pan: float = 0.0,
                 largura: float = 1.0, reverb: float = 0.25, mudo: bool = False, solo: bool = False,
                 **params_instrumento):
        self.musica = musica
        self.nome = nome
        if isinstance(instrumento, Instrumento):
            self.instrumento = instrumento
        else:
            self.instrumento = criar(instrumento, musica.sr, **params_instrumento)
        self.volume_db = volume_db
        self.pan = pan
        self.largura = largura
        self.reverb = reverb
        self.mudo = mudo
        self.solo = solo
        self.notas: list[Nota] = []
        self.efeitos: list[tuple[str, dict]] = []
        self.automacoes: list[Automacao] = []
        self.human = {"tempo_ms": 0.0, "vel": 0.0, "cents": 0.0}
        self.cursor = 0.0  # tempo (beat) logo depois da última nota escrita
        self.ultimo_audio: np.ndarray | None = None

    # ------------------------------------------------------------------ escrever

    def nota(self, altura, t: float | None = None, dur: float = 1.0, vel=0.6, tecnica=None, **kw) -> Nota:
        """Adiciona uma nota. t em tempos (beats); None = logo depois da última (cursor)."""
        if t is None:
            t = self.cursor
        n = Nota(float(t), float(dur), altura, vel, tecnica, **kw)
        self.notas.append(n)
        self.cursor = max(self.cursor, n.fim)
        return n

    def pausa(self, dur: float = 1.0):
        self.cursor += dur
        return self

    def sequencia(self, alturas, dur: float = 1.0, t: float | None = None, vel=0.6, tecnica=None, legato=False):
        """'A4 B4 C#5 -' (traço = pausa) ou lista. Todas com a mesma duração."""
        if isinstance(alturas, str):
            alturas = alturas.split()
        t = self.cursor if t is None else t
        out = []
        for i, a in enumerate(alturas):
            if a not in ("-", "0", None):
                out.append(self.nota(a, t, dur, vel, tecnica, legato=legato and i > 0))
            t += dur
        self.cursor = max(self.cursor, t)
        return out

    def acorde(self, alturas, t: float | None = None, dur: float = 1.0, vel=0.6, arpejo: float = 0.0,
               tecnica=None):
        """Várias notas juntas. arpejo = tempos entre cada nota (0 = bloco)."""
        if isinstance(alturas, str):
            alturas = alturas.split()
        t = self.cursor if t is None else t
        return [self.nota(a, t + i * arpejo, dur - i * arpejo, vel, tecnica) for i, a in enumerate(alturas)]

    def jianpu(self, texto: str, inicio: float | None = None, tom: str | None = None, oitava: int | None = None,
               vel=None, tecnica=None) -> float:
        """Escreve em 简谱 (notação numérica). Veja docs/PARTITURA.md. Devolve o tempo final."""
        from .jianpu import ler_jianpu
        ini = self.cursor if inicio is None else inicio
        t_tom = Tom.de_texto(tom or self.musica.tom_texto, oitava if oitava is not None else self.musica.oitava)
        notas, fim, diretivas = ler_jianpu(texto, ini, t_tom, vel=vel, tecnica=tecnica)
        self.notas += notas
        for beat, bpm, rampa in diretivas.get("andamento", []):
            if bpm is None:  # âncora de @rit/@accel: fixa o andamento que valia ali
                bpm = self.musica.tempo.bpm_em(beat)
            self.musica.andamento(beat, bpm, rampa)
        self.cursor = max(self.cursor, fim)
        return fim

    # ------------------------------------------------------------------ mixer

    def efeito(self, nome: str, **params):
        """Efeito de inserção (na ordem em que são adicionados). Ex.: faixa.efeito('eq', bandas=[...])."""
        self.efeitos.append((nome, params))
        return self

    def automacao(self, parametro: str, pontos, forma: str = "linear"):
        """parametro: volume_db | pan | reverb | largura. pontos = [(tempo, valor), ...]."""
        if parametro not in ("volume_db", "pan", "reverb", "largura"):
            raise ValueError("automação aceita: volume_db, pan, reverb, largura")
        self.automacoes.append(Automacao(parametro, list(pontos), forma))
        return self

    def humanizar(self, tempo_ms: float = 8.0, vel: float = 0.06, cents: float = 2.0):
        """Imprecisão humana reproduzível (usa a semente da música)."""
        self.human = {"tempo_ms": tempo_ms, "vel": vel, "cents": cents}
        return self

    # ------------------------------------------------------------------ render

    def resolver(self, rng) -> list[NotaR]:
        m = self.musica
        out = []
        for i, n in enumerate(sorted(self.notas, key=lambda x: x.inicio)):
            t0 = m.tempo.segundos(n.inicio)
            t1 = m.tempo.segundos(n.fim)
            if self.human["tempo_ms"] and not n.legato:
                t0 += rng.normal(0, self.human["tempo_ms"] / 1000)
                t0 = max(t0, 0.0)
            vel = n.vel
            if self.human["vel"]:
                vel = float(np.clip(vel * (1 + rng.normal(0, self.human["vel"])), 0.02, 1.0))
            f0 = midi = None
            curva = n.curva
            if n.altura is not None:
                f0 = m.afinacao.hz(n.altura)
                midi = 69 + 12 * np.log2(f0 / m.afinacao.la4)
                if self.human["cents"]:
                    desv = rng.normal(0, self.human["cents"])
                    curva = (curva.copiar() if curva else CurvaAltura())
                    curva.pontos = [(t, v + desv, f) for t, v, f in curva.pontos]
            out.append(NotaR(t0, max(t1 - t0, 0.005), f0, midi, vel, n.tecnicas, n.corda, n.legato, curva,
                             n.pan, dict(n.params), i))
        return out

    def renderizar(self, n_total: int, rng) -> np.ndarray:
        sr = self.musica.sr
        inst = self.instrumento
        inst.preparar(self.musica.afinacao)
        notas = self.resolver(rng)
        y = inst.renderizar(notas, n_total, rng) if notas else np.zeros((2, n_total))
        for nome, ps in self.efeitos:
            y = FX.aplicar(nome, y, sr, **ps)
            if y.shape[1] > n_total:
                y = y[:, :n_total]
            elif y.shape[1] < n_total:
                y = np.pad(y, ((0, 0), (0, n_total - y.shape[1])))
        t = np.arange(n_total) / sr
        vol = np.full(n_total, self.volume_db, float)
        pan = np.full(n_total, self.pan, float)
        larg = np.full(n_total, self.largura, float)
        for a in self.automacoes:
            v = a.avaliar_segundos(t, self.musica.tempo.segundos)
            if a.parametro == "volume_db":
                vol = v
            elif a.parametro == "pan":
                pan = v
            elif a.parametro == "largura":
                larg = v
        # largura (mid/side) e balanço de potência constante (centro = ganho 1)
        mid = 0.5 * (y[0] + y[1])
        side = 0.5 * (y[0] - y[1]) * larg
        gl, gr = pan_ganhos(pan)
        g = db_para_lin(vol)
        y = np.vstack([(mid + side) * gl * np.sqrt(2) * g, (mid - side) * gr * np.sqrt(2) * g])
        self.ultimo_audio = y
        return y

    def envio_reverb(self, n_total: int) -> np.ndarray:
        env = np.full(n_total, self.reverb, float)
        for a in self.automacoes:
            if a.parametro == "reverb":
                env = a.avaliar_segundos(np.arange(n_total) / self.musica.sr, self.musica.tempo.segundos)
        return env

    @property
    def fim(self) -> float:
        return max((n.fim for n in self.notas), default=0.0)


class Musica:
    def __init__(self, titulo: str = "Sem título", tempo: float = 90.0, compasso: str = "4/4", tom: str = "1=C",
                 la4: float = 440.0, temperamento: str = "igual", tonica_temperamento: str | None = None,
                 sr: int = 48000, semente: int = 0, reverb: str | None = "palacio_tang", nivel_reverb: float = 1.0,
                 oitava: int = 4, autor: str = ""):
        self.titulo = titulo
        self.autor = autor
        self.sr = int(sr)
        self.semente = semente
        self.tempo = MapaTempo(float(tempo))
        self.compasso = compasso
        self.tom_texto = tom
        self.oitava = oitava
        tonica = tonica_temperamento or Tom.de_texto(tom).tonica
        self.afinacao = Afinacao(la4=la4, temperamento=temperamento, tonica=tonica)
        self.faixas: list[Faixa] = []
        self.sala = reverb
        self.nivel_reverb = nivel_reverb
        self.master: list[tuple[str, dict]] = []
        self.loudness_alvo: float | None = -16.0
        self.teto_db = -1.0
        self.limite_db = 6.0     # quanto o limitador do master pode segurar ao normalizar
        self.cauda = 3.0
        self.estatisticas: dict = {}

    # ------------------------------------------------------------------ estrutura

    def faixa(self, nome: str, instrumento, **kw) -> Faixa:
        f = Faixa(self, nome, instrumento, **kw)
        self.faixas.append(f)
        return f

    def andamento(self, tempo_beat: float, bpm: float, rampa: bool = False):
        """Muda o andamento no tempo dado. rampa=True acelera/desacelera até lá (rit./accel.)."""
        self.tempo.mudar(tempo_beat, bpm, rampa)
        return self

    def compasso_em(self, numero: int, tempo: float = 1.0) -> float:
        """Tempo (beat) do compasso 'numero' (começa em 1), tempo dentro do compasso (começa em 1)."""
        num, den = (int(x) for x in self.compasso.split("/"))
        return (numero - 1) * num * 4 / den + (tempo - 1) * 4 / den

    def efeito_master(self, nome: str, **params):
        self.master.append((nome, params))
        return self

    def duracao(self) -> float:
        fim = max((f.fim for f in self.faixas), default=0.0)
        return self.tempo.segundos(fim)

    # ------------------------------------------------------------------ render

    def renderizar(self, normalizar: str | None = "lufs", stems: bool = False, verbose: bool = False):
        """Renderiza tudo. normalizar: 'lufs' (alvo self.loudness_alvo) | 'pico' | None.
        stems=True devolve também {nome_faixa: áudio}."""
        sr = self.sr
        t_ini = time.time()
        dur = self.duracao()
        n_total = int((dur + self.cauda + 2.0) * sr)
        mix = np.zeros((2, n_total))
        envio = np.zeros((2, n_total))
        ativos = [f for f in self.faixas if not f.mudo]
        if any(f.solo for f in ativos):
            ativos = [f for f in ativos if f.solo]
        saidas = {}
        for i, f in enumerate(self.faixas):
            if f not in ativos:
                continue
            rng = np.random.default_rng([self.semente, i])
            t0 = time.time()
            y = f.renderizar(n_total, rng)
            if verbose:
                print(f"  {f.nome:16s} {f.instrumento.id:14s} {len(f.notas):5d} notas  {time.time() - t0:6.2f} s")
            mix += y
            envio += y * f.envio_reverb(n_total)
            saidas[f.nome] = y
        if self.sala and np.any(envio):
            molhado = FX.reverb(envio, sr, self.sala)[:, :n_total]
            mix += self.nivel_reverb * molhado
            saidas["_reverb"] = self.nivel_reverb * molhado
        for nome, ps in self.master:
            mix = FX.aplicar(nome, mix, sr, **ps)[:, :n_total]
        # corta o silêncio do fim (abaixo de -70 dB) e faz um fade curto
        nivel = np.max(np.abs(mix), axis=0)
        acima = np.nonzero(nivel > db_para_lin(-70) * max(pico(mix), 1e-9))[0]
        fim = int(min(n_total, (acima[-1] if acima.size else 0) + 0.3 * sr))
        mix = fade(mix[:, :max(fim, int(0.1 * sr))], sr, 1.0, 200.0)
        ganho = 1.0
        if normalizar == "lufs" and self.loudness_alvo is not None and pico(mix) > 0:
            # v1.0: leva ao loudness alvo deixando o limitador segurar no máximo `limite_db` dos picos
            # (instrumentos dedilhados e percussão têm picos ~20 dB acima da média)
            ganho_db = self.loudness_alvo - lufs_integrado(mix, sr)
            excesso = 20 * np.log10(pico(mix)) + ganho_db - self.teto_db
            if excesso > self.limite_db:
                ganho_db -= excesso - self.limite_db
            ganho = float(db_para_lin(ganho_db))
            mix = mix * ganho
        elif normalizar == "pico":
            antes = pico(mix)
            mix = normalizar_pico(mix, self.teto_db)
            ganho = pico(mix) / antes if antes else 1.0
        if pico(mix) > db_para_lin(self.teto_db) * 1.001:
            mix = FX.limitador(mix, sr, self.teto_db)
        self.estatisticas = {"duracao_s": mix.shape[1] / sr, "tempo_render_s": time.time() - t_ini,
                             "pico_db": 20 * np.log10(max(pico(mix), 1e-9)),
                             "lufs": lufs_integrado(mix, sr) if mix.shape[1] > sr // 2 else None}
        if stems:
            return mix, {k: v[:, :mix.shape[1]] * ganho for k, v in saidas.items()}
        return mix

    # ------------------------------------------------------------------ exportar

    def exportar(self, caminho, bits: int = 24, mono: bool = False, normalizar: str | None = "lufs",
                 verbose: bool = True, audio: np.ndarray | None = None) -> Path:
        """Salva .wav / .flac / .ogg (Vorbis, serve direto no Minecraft) / .npy."""
        caminho = Path(caminho)
        y = self.renderizar(normalizar, verbose=verbose) if audio is None else audio
        salvar_audio(caminho, y, self.sr, bits=bits, mono=mono)
        if verbose:
            e = self.estatisticas
            lufs = f"{e['lufs']:.1f} LUFS" if e.get("lufs") is not None else ""
            print(f"✔ {caminho}  {e.get('duracao_s', 0):.1f} s  pico {e.get('pico_db', 0):.1f} dBFS  {lufs}  "
                  f"(render {e.get('tempo_render_s', 0):.1f} s)")
        return caminho

    def exportar_stems(self, pasta, bits: int = 24) -> list[Path]:
        """Uma faixa por arquivo (mesmo ganho do mix) + o reverb separado. Bom para mixar fora."""
        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        mix, stems = self.renderizar(stems=True)
        out = [salvar_audio(pasta / "mix.wav", mix, self.sr, bits)]
        for nome, y in stems.items():
            out.append(salvar_audio(pasta / f"{nome}.wav", y, self.sr, bits))
        return out

    def exportar_midi(self, caminho):
        from .midi import exportar_midi
        return exportar_midi(self, caminho)

    def tocar(self):
        """Toca na caixa de som (precisa de sounddevice: pip install sounddevice)."""
        try:
            import sounddevice as sd
        except ImportError as e:
            raise RuntimeError("instale o extra: pip install sounddevice") from e
        y = self.renderizar()
        sd.play(y.T, self.sr)
        sd.wait()

    # ------------------------------------------------------------------ salvar/carregar

    def para_dict(self) -> dict:
        d = {"titulo": self.titulo, "autor": self.autor, "tempo": self.tempo.bpm_inicial,
             "andamentos": [list(e) for e in self.tempo.eventos], "compasso": self.compasso, "tom": self.tom_texto,
             "la4": self.afinacao.la4, "temperamento": self.afinacao.temperamento, "sr": self.sr,
             "semente": self.semente, "reverb": self.sala, "nivel_reverb": self.nivel_reverb,
             "loudness": self.loudness_alvo, "master": [[n, p] for n, p in self.master], "faixas": []}
        for f in self.faixas:
            inst = f.instrumento
            params = {k: v for k, v in inst.p.items() if inst.PARAMETROS.get(k, (None,))[0] != v}
            d["faixas"].append({
                "nome": f.nome, "instrumento": inst.id, "params": params, "volume_db": f.volume_db, "pan": f.pan,
                "largura": f.largura, "reverb": f.reverb, "mudo": f.mudo, "solo": f.solo,
                "humanizar": f.human, "efeitos": [[n, p] for n, p in f.efeitos],
                "automacoes": [[a.parametro, a.pontos, a.forma] for a in f.automacoes],
                "notas": [_nota_para_dict(n) for n in f.notas]})
        return d

    def salvar(self, caminho):
        Path(caminho).write_text(json.dumps(self.para_dict(), ensure_ascii=False, indent=1), encoding="utf-8")

    @classmethod
    def de_dict(cls, d: dict) -> "Musica":
        m = cls(d.get("titulo", "Sem título"), d.get("tempo", 90), d.get("compasso", "4/4"), d.get("tom", "1=C"),
                d.get("la4", 440.0), d.get("temperamento", "igual"), None, d.get("sr", 48000), d.get("semente", 0),
                d.get("reverb", "palacio_tang"), d.get("nivel_reverb", 1.0), d.get("oitava", 4), d.get("autor", ""))
        for b, v, r in d.get("andamentos", []):
            m.andamento(b, v, r)
        if "loudness" in d:
            m.loudness_alvo = d["loudness"]
        for n, p in d.get("master", []):
            m.efeito_master(n, **p)
        for fd in d.get("faixas", []):
            f = m.faixa(fd["nome"], fd["instrumento"], volume_db=fd.get("volume_db", 0.0), pan=fd.get("pan", 0.0),
                        largura=fd.get("largura", 1.0), reverb=fd.get("reverb", 0.25), mudo=fd.get("mudo", False),
                        solo=fd.get("solo", False), **fd.get("params", {}))
            if fd.get("humanizar"):
                f.humanizar(**fd["humanizar"])
            for n, p in fd.get("efeitos", []):
                f.efeito(n, **p)
            for par, pontos, forma in fd.get("automacoes", []):
                f.automacao(par, pontos, forma)
            for nd in fd.get("notas", []):
                f.notas.append(_nota_de_dict(nd))
            if fd.get("jianpu"):
                f.jianpu(fd["jianpu"], fd.get("inicio_jianpu", 0.0), fd.get("tom"))
            f.cursor = f.fim
        return m

    @classmethod
    def carregar(cls, caminho) -> "Musica":
        """.json (formato do motor), .jp/.txt (简谱 com cabeçalho) ou .mid/.midi."""
        caminho = Path(caminho)
        suf = caminho.suffix.lower()
        if suf == ".json":
            return cls.de_dict(json.loads(caminho.read_text(encoding="utf-8")))
        if suf in (".mid", ".midi"):
            from .midi import importar_midi
            return importar_midi(caminho)
        from .jianpu import ler_arquivo_jianpu
        return ler_arquivo_jianpu(caminho.read_text(encoding="utf-8"), cls)


def _nota_para_dict(n: Nota) -> dict:
    d = {"t": n.inicio, "dur": n.duracao, "altura": n.altura, "vel": round(n.vel, 4)}
    if n.tecnicas:
        d["tecnica"] = [[k, v] for k, v in n.tecnicas]
    for k in ("corda", "pan"):
        if getattr(n, k) is not None:
            d[k] = getattr(n, k)
    if n.legato:
        d["legato"] = True
    if n.params:
        d["params"] = n.params
    if n.curva is not None:
        d["curva"] = {"pontos": n.curva.pontos, "vibratos": [v.__dict__ for v in n.curva.vibratos],
                      "deriva": n.curva.deriva}
    return d


def _nota_de_dict(d: dict) -> Nota:
    curva = None
    if d.get("curva"):
        from .curvas import Vibrato
        c = d["curva"]
        curva = CurvaAltura([tuple(p) for p in c.get("pontos", [(0, 0, "degrau")])],
                            [Vibrato(**v) for v in c.get("vibratos", [])], c.get("deriva", 0.0))
    vel = d.get("vel", 0.6)
    if isinstance(vel, str):
        vel = DINAMICAS[vel]
    return Nota(d["t"], d.get("dur", 1.0), d.get("altura"), vel, d.get("tecnica"), d.get("corda"),
                d.get("legato", False), curva, d.get("pan"), d.get("params", {}))


def salvar_audio(caminho, y: np.ndarray, sr: int, bits: int = 24, mono: bool = False) -> Path:
    import soundfile as sf
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    y = np.atleast_2d(y)
    if mono:
        y = y.mean(axis=0, keepdims=True)
    dados = y.T.astype(np.float32)
    suf = caminho.suffix.lower()
    if suf == ".npy":
        np.save(caminho, y)
        return caminho
    if suf == ".ogg":
        sf.write(caminho, dados, sr, format="OGG", subtype="VORBIS")
    elif suf == ".flac":
        sf.write(caminho, dados, sr, format="FLAC", subtype="PCM_24" if bits >= 24 else "PCM_16")
    else:
        sub = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}[bits]
        sf.write(caminho, dados, sr, subtype=sub)
    return caminho
