"""Base de todos os instrumentos: parâmetros, registro de técnicas e de instrumentos.

Para criar um instrumento novo, veja docs/TUTORIAL.md §5. Em resumo:

    @registrar
    class MeuInstrumento(CordaDedilhadaBase):
        id = "meu"
        ...
        @tecnica("bater", "拍", descricao="bate no tampo")
        def _bater(self, golpes, nota, forca=0.5):
            ...
            return golpes
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field

import numpy as np

from ..dsp.util import pan_ganhos


@dataclass
class InfoTecnica:
    nome: str
    aliases: tuple
    descricao: str
    params: dict
    metodo: str


def tecnica(nome: str, *aliases: str, descricao: str = "", params: dict | None = None):
    """Marca um método como técnica. aliases: nomes em chinês, pinyin, português..."""
    def deco(f):
        f._tecnica = InfoTecnica(nome, tuple(aliases), descricao, params or {}, f.__name__)
        return f
    return deco


class Instrumento:
    id: str = "base"
    nome: str = "Instrumento"
    nome_cn: str = ""
    pinyin: str = ""
    familia: str = ""
    descricao: str = ""
    historia: str = ""
    extensao: tuple = ("C2", "C7")
    polifonico: bool = True
    # nome: (padrão, descrição)
    PARAMETROS: dict = {}
    TECNICAS: dict = {}
    ALIASES: dict = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        tecs, ali = {}, {}
        params = {}
        for base in reversed(cls.__mro__):
            params.update(base.__dict__.get("PARAMETROS", {}))
            for nome_attr, v in base.__dict__.items():
                info = getattr(v, "_tecnica", None)
                if info is not None:
                    tecs[info.nome] = info
        for info in tecs.values():
            ali[info.nome.lower()] = info.nome
            for a in info.aliases:
                ali[a.lower()] = info.nome
        cls.TECNICAS = tecs
        cls.ALIASES = ali
        cls.PARAMETROS = params

    def __init__(self, sr: int = 48000, **params):
        self.sr = int(sr)
        self.p = {k: v[0] for k, v in self.PARAMETROS.items()}
        for k, v in params.items():
            if k not in self.p:
                sug = difflib.get_close_matches(k, list(self.p), n=3)
                raise ValueError(f"[{self.id}] parâmetro desconhecido '{k}'."
                                 + (f" Quis dizer: {', '.join(sug)}?" if sug else "")
                                 + f" Disponíveis: {', '.join(sorted(self.p))}")
            self.p[k] = v
        self.configurar()

    def configurar(self):
        """Gancho chamado depois de ler os parâmetros (subclasses preparam afinação, cordas...)."""

    def preparar(self, afinacao):
        """Chamado pela faixa antes de renderizar: recebe a Afinacao da música (lá, temperamento)."""
        self.afinacao = afinacao

    # ------------------------------------------------------------------ técnicas

    def resolver_tecnica(self, nome: str) -> InfoTecnica:
        chave = self.ALIASES.get(nome.lower())
        if chave is None:
            sug = difflib.get_close_matches(nome.lower(), list(self.ALIASES), n=4)
            raise ValueError(f"[{self.id}] técnica desconhecida '{nome}'."
                             + (f" Quis dizer: {', '.join(sug)}?" if sug else "")
                             + f" Técnicas: {', '.join(sorted(self.TECNICAS))}")
        return self.TECNICAS[chave]

    def aplicar_tecnicas(self, alvo, nota, rng):
        """Passa 'alvo' (lista de golpes ou segmento) por cada técnica da nota, em ordem."""
        for nome, params in nota.tecnicas:
            info = self.resolver_tecnica(nome)
            params = dict(params)
            if "_" in params:  # parâmetro posicional ('tui:200')
                pos = params.pop("_")
                primeiro = next(iter(info.params), None)
                if primeiro is None:
                    raise ValueError(f"[{self.id}] '{info.nome}' não tem parâmetros")
                params[primeiro] = pos
            desconhecidos = set(params) - set(info.params)
            if desconhecidos:
                raise ValueError(f"[{self.id}] técnica '{info.nome}' não aceita {sorted(desconhecidos)}. "
                                 f"Aceita: {sorted(info.params) or 'nada'}")
            alvo = getattr(self, info.metodo)(alvo, nota, rng, **params)
        return alvo

    # ------------------------------------------------------------------ render

    def renderizar(self, notas: list, n_total: int, rng: np.random.Generator) -> np.ndarray:
        """Recebe NotaR ordenadas e devolve estéreo (2, n_total)."""
        raise NotImplementedError

    def _colocar(self, buf: np.ndarray, y: np.ndarray, t0: float, pan: float = 0.0):
        """Soma o mono y em buf (2, N) a partir de t0 (s) com pan de potência constante."""
        i0 = int(round(t0 * self.sr))
        if i0 >= buf.shape[1] or y.size == 0:
            return
        if i0 < 0:
            y = y[-i0:]
            i0 = 0
        n = min(y.shape[0], buf.shape[1] - i0)
        gl, gr = pan_ganhos(pan)
        buf[0, i0:i0 + n] += gl * y[:n]
        buf[1, i0:i0 + n] += gr * y[:n]

    # ------------------------------------------------------------------ documentação

    @classmethod
    def descrever(cls) -> str:
        linhas = [f"## {cls.nome} {cls.nome_cn} ({cls.pinyin}) — `{cls.id}`", "", cls.descricao, ""]
        if cls.historia:
            linhas += [f"*{cls.historia}*", ""]
        linhas += [f"- Família: {cls.familia}", f"- Extensão: {cls.extensao[0]}–{cls.extensao[1]}",
                   f"- Polifônico: {'sim' if cls.polifonico else 'não (monofônico, frases contínuas)'}", ""]
        if cls.PARAMETROS:
            linhas += ["| parâmetro | padrão | o que faz |", "|---|---|---|"]
            for k, (v, d) in cls.PARAMETROS.items():
                linhas.append(f"| `{k}` | `{v!r}` | {d} |")
            linhas.append("")
        if cls.TECNICAS:
            linhas += ["| técnica | também aceita | parâmetros | o que faz |", "|---|---|---|---|"]
            for info in cls.TECNICAS.values():
                ps = ", ".join(f"`{k}` ({d})" for k, d in info.params.items()) or "—"
                linhas.append(f"| `{info.nome}` | {' '.join(info.aliases)} | {ps} | {info.descricao} |")
            linhas.append("")
        return "\n".join(linhas)


# ---------------------------------------------------------------------- registro

REGISTRO: dict = {}
VARIANTES: dict = {}


def registrar(cls):
    REGISTRO[cls.id] = cls
    return cls


def variante(id_: str, base_id: str, nome: str, descricao: str = "", **params):
    """Preset: um instrumento existente com parâmetros diferentes (ex.: 'pipa_seda')."""
    VARIANTES[id_] = (base_id, nome, descricao, params)


def criar(id_: str, sr: int = 48000, **params) -> Instrumento:
    if id_ in REGISTRO:
        return REGISTRO[id_](sr, **params)
    if id_ in VARIANTES:
        base_id, _, _, ps = VARIANTES[id_]
        inst = REGISTRO[base_id](sr, **{**ps, **params})
        inst.id = id_
        return inst
    todos = list(REGISTRO) + list(VARIANTES)
    sug = difflib.get_close_matches(id_, todos, n=3)
    raise ValueError(f"instrumento desconhecido '{id_}'." + (f" Quis dizer: {', '.join(sug)}?" if sug else "")
                     + " Use huayin.listar_instrumentos().")


def listar() -> list[dict]:
    out = []
    for k, c in REGISTRO.items():
        out.append({"id": k, "nome": c.nome, "nome_cn": c.nome_cn, "familia": c.familia,
                    "extensao": c.extensao, "tecnicas": len(c.TECNICAS)})
    for k, (b, nome, desc, _) in VARIANTES.items():
        c = REGISTRO[b]
        out.append({"id": k, "nome": nome, "nome_cn": c.nome_cn, "familia": c.familia,
                    "extensao": c.extensao, "tecnicas": len(c.TECNICAS), "variante_de": b})
    return out


@dataclass
class Golpe:
    """Uma excitação física de uma corda (o que as técnicas de cordas dedilhadas produzem)."""
    t0: float
    dur: float
    corda: int
    f0: float
    vel: float
    curva: object
    posicao: float = 0.12
    dureza: float = 0.6
    harmonico: int = 0
    ruido_ataque: float = 0.03
    contato: float = 0.0
    t60_escala: float = 1.0
    t60_soltura: float = 0.12
    pan: float = 0.0
    deslize: bool = False
    camadas: list = field(default_factory=list)   # [(tipo, params)] sons extras (batida, clique...)
    sem_corte: bool = False                       # não é abafado pelo próximo golpe na mesma corda
    mudo: bool = False                            # só as camadas soam (ex.: 拍 bater no tampo)
    martelo: bool | None = None                   # None = o padrão do instrumento (percutida/pinçada)
    reexcitacoes: list = field(default_factory=list)  # [(t_rel, vel)] golpes extras sem abafar
