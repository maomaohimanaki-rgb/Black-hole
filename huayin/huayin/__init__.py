"""华音 Huayin — motor de síntese física de instrumentos clássicos chineses.

Uso rápido:

    import huayin as hy
    m = hy.Musica("Primeira", tempo=72, tom="1=D")
    pipa = m.faixa("pipa", "pipa_tang")
    pipa.jianpu("1 2 3 5 | 6{lun} - - - |")
    m.exportar("primeira.wav")

Veja README.md (manual) e docs/TUTORIAL.md.
"""
from __future__ import annotations

__version__ = "1.0.0"

from . import efeitos  # noqa: F401
from .afinacao import ESCALAS, TEMPERAMENTOS, Afinacao, Tom, escala_midi, midi_para_nome, nota_para_midi  # noqa: F401
from .composicao.curvas import Automacao, CurvaAltura, Vibrato  # noqa: F401
from .composicao.musica import Faixa, Musica, salvar_audio  # noqa: F401
from .composicao.nota import DINAMICAS, Nota  # noqa: F401
from .dsp.kernels import TEM_NUMBA  # noqa: F401
from .efeitos import SALAS  # noqa: F401
from .fisica.corda import MATERIAIS, Material  # noqa: F401
from .fisica.corpo import CORPOS, Corpo  # noqa: F401
from .instrumentos import REGISTRO, VARIANTES, Instrumento, criar, registrar, tecnica, variante  # noqa: F401
from .instrumentos import listar as _listar


def listar_instrumentos(familia: str | None = None) -> list[dict]:
    """Lista os instrumentos (e variantes) registrados. familia: filtra por texto ('sopro', 'corda'...)."""
    out = _listar()
    if familia:
        out = [i for i in out if familia.lower() in i["familia"].lower()]
    return out


def tecnicas(instrumento: str) -> dict:
    """{nome: descrição} das técnicas de um instrumento."""
    inst = criar(instrumento)
    return {k: v.descricao for k, v in inst.TECNICAS.items()}


def ajuda(instrumento: str) -> str:
    """Ficha completa (markdown) de um instrumento: parâmetros e técnicas."""
    inst = criar(instrumento)
    return type(inst).descrever()


def nota_unica(instrumento: str, altura="A4", dur: float = 2.0, vel: float = 0.7, tecnica=None,
               sr: int = 48000, reverb: str | None = None, **params):
    """Renderiza uma nota só e devolve o áudio estéreo (útil para testar e ajustar parâmetros)."""
    m = Musica("nota", tempo=60, sr=sr, reverb=reverb)
    f = m.faixa("f", instrumento, **params)
    f.nota(altura, 0, dur, vel, tecnica)
    return m.renderizar(normalizar="pico")
