"""Eventos musicais: a Nota que o compositor escreve e a NotaR (resolvida) que o instrumento toca."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .curvas import CurvaAltura

DINAMICAS = {"ppp": 0.12, "pp": 0.22, "p": 0.35, "mp": 0.48, "mf": 0.6, "f": 0.75, "ff": 0.88, "fff": 0.97}


def normalizar_tecnicas(tecnica) -> list[tuple[str, dict]]:
    """Aceita: None | 'lun' | 'lun:velocidade=16,dedos=5' | ['tui', 'yin'] | {'tui': {'cents': 200}}
    | [('tui', {'cents': 200})]. Devolve [(nome, params)]."""
    if tecnica is None or tecnica == "":
        return []
    if isinstance(tecnica, dict):
        return [(k, dict(v or {})) for k, v in tecnica.items()]
    if isinstance(tecnica, str):
        return [_parse_tecnica(t) for t in re.split(r"[+;]", tecnica) if t.strip()]
    out = []
    for t in tecnica:
        if isinstance(t, str):
            out.append(_parse_tecnica(t))
        elif isinstance(t, (tuple, list)) and len(t) == 2:
            out.append((str(t[0]), dict(t[1] or {})))
        elif isinstance(t, dict):
            out += normalizar_tecnicas(t)
        else:
            raise ValueError(f"técnica inválida: {t!r}")
    return out


def _valor(v: str):
    v = v.strip()
    for conv in (int, float):
        try:
            return conv(v)
        except ValueError:
            pass
    if v.lower() in ("sim", "true", "verdadeiro"):
        return True
    if v.lower() in ("nao", "não", "false", "falso"):
        return False
    return v


def _parse_tecnica(s: str) -> tuple[str, dict]:
    s = s.strip()
    if ":" not in s:
        return s, {}
    nome, resto = s.split(":", 1)
    params = {}
    for par in resto.split(","):
        if not par.strip():
            continue
        if "=" in par:
            k, v = par.split("=", 1)
            params[k.strip()] = _valor(v)
        else:
            # atalho: 'tui:200' vira o primeiro parâmetro posicional
            params["_"] = _valor(par)
    return nome.strip(), params


@dataclass
class Nota:
    """Uma nota como o compositor pensa: em TEMPOS (beats), com altura simbólica.

    altura  : 'A4', 'C#5', 69 (MIDI), 440.0 (Hz), 'hz:440' ou None (percussão sem altura)
    vel     : 0–1 (ou nome de dinâmica: 'p', 'mf', 'ff'...)
    tecnicas: lista [(nome, params)] — ver normalizar_tecnicas
    corda   : força a corda (0 = mais grave). None = o instrumento escolhe
    legato  : liga com a nota anterior (sem novo ataque: slide/hammer na corda, mesma arcada,
              mesmo sopro)
    curva   : CurvaAltura extra definida à mão (somada às das técnicas)
    params  : parâmetros extras do instrumento só para esta nota
    """
    inicio: float
    duracao: float
    altura: Any = None
    vel: float = 0.6
    tecnicas: list = field(default_factory=list)
    corda: int | None = None
    legato: bool = False
    curva: CurvaAltura | None = None
    pan: float | None = None
    params: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.vel, str):
            self.vel = DINAMICAS[self.vel]
        if self.vel > 1.0:  # aceita 0–127 estilo MIDI
            self.vel = self.vel / 127.0
        self.tecnicas = normalizar_tecnicas(self.tecnicas)

    @property
    def fim(self) -> float:
        return self.inicio + self.duracao


@dataclass
class NotaR:
    """Nota resolvida em segundos e Hz, pronta para o instrumento."""
    t0: float
    dur: float
    f0: float | None
    midi: float | None
    vel: float
    tecnicas: list
    corda: int | None = None
    legato: bool = False
    curva: CurvaAltura | None = None
    pan: float | None = None
    params: dict = field(default_factory=dict)
    indice: int = 0

    @property
    def t1(self) -> float:
        return self.t0 + self.dur

    def tem(self, *nomes) -> bool:
        return any(t[0] in nomes for t in self.tecnicas)
