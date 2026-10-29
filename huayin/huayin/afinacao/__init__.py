"""Afinação: nomes de nota, temperamentos históricos chineses, modos e 简谱 (jianpu).

Temperamentos:
  * igual         — 12-TET. Zhu Zaiyu 朱载堉 calculou o temperamento igual com 25 dígitos em
                    1584 (新法密率), antes da Europa. É o padrão.
  * sanfen_sunyi  — 三分损益法: gera as notas por quintas 3:2 (perde um terço) e quartas 4:3
                    (ganha um terço) a partir de 黄钟. É a afinação pitagórica chinesa (Guanzi, Lüshi
                    Chunqiu). Quintas puras, terças largas, "coma" no fim do ciclo.
  * justa         — 纯律: terças e sextas puras (5:4, 5:3). Muito usada pelo guqin, cujos
                    泛音 (harmônicos nas 徽) dão naturalmente intervalos justos.
  * personalizada — tabela de 12 desvios em cents (dicionário ou lista).

Referência: lá4 = 440 Hz por padrão (orquestras chinesas costumam usar 442; o gagaku japonês,
herdeiro da música da corte Tang, usa 430). O 黄钟 (huangzhong, a tônica dos 12 律) vale C por
padrão; a altura absoluta do 黄钟 variou muito entre dinastias.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

NOMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NOMES_PT = {"DO": 0, "DÓ": 0, "RE": 2, "RÉ": 2, "MI": 4, "FA": 5, "FÁ": 5, "SOL": 7, "LA": 9, "LÁ": 9,
            "SI": 11}

# 十二律 — os doze tubos-padrão, a partir de 黄钟
SHIER_LU = ["黄钟", "大吕", "太簇", "夹钟", "姑洗", "仲吕", "蕤宾", "林钟", "夷则", "南吕", "无射", "应钟"]
SHIER_LU_PINYIN = ["huangzhong", "dalü", "taicu", "jiazhong", "guxian", "zhonglü", "ruibin", "linzhong",
                   "yize", "nanlü", "wuyi", "yingzhong"]

# 五声 (cinco sons) e os sete graus — em semitons a partir do 宫
GRAUS = {
    "宫": 0, "gong": 0, "商": 2, "shang": 2, "角": 4, "jue": 4, "清角": 5, "qingjue": 5,
    "变徵": 6, "bianzhi": 6, "徵": 7, "zhi": 7, "羽": 9, "yu": 9, "闰": 10, "run": 10, "清羽": 10,
    "变宫": 11, "biangong": 11,
}

# Escalas (graus em semitons a partir do 宫). Os modos 宫/商/角/徵/羽 escolhem a nota final.
ESCALAS = {
    "pentatonica": [0, 2, 4, 7, 9],                 # 五声音阶
    "yayue": [0, 2, 4, 6, 7, 9, 11],                # 雅乐 (música ritual): com 变徵 (4#) e 变宫 (7)
    "qingyue": [0, 2, 4, 5, 7, 9, 11],              # 清乐 (= maior natural): com 清角 (4) e 变宫
    "yanyue": [0, 2, 4, 5, 7, 9, 10],               # 燕乐 (banquete Tang): com 清角 e 闰 (7b)
    "cromatica": list(range(12)),
}
MODOS = {"宫": 0, "gong": 0, "商": 1, "shang": 1, "角": 2, "jue": 2, "徵": 3, "zhi": 3, "羽": 4, "yu": 4}

def _sanfen_sunyi():
    """Ciclo de 三分损益: 黄钟 → ×2/3 (损) → ×4/3 (益) → ... 11 passos, dobrando à oitava."""
    razoes = {0: 1.0}
    r, semi = 1.0, 0
    for i in range(11):
        if i % 2 == 0:
            r *= 3 / 2   # 三分损一: comprimento × 2/3 → frequência × 3/2
            semi += 7
        else:
            r *= 3 / 4   # 三分益一: comprimento × 4/3 → frequência × 3/4
            semi -= 5
        semi %= 12
        while r >= 2:
            r /= 2
        while r < 1:
            r *= 2
        razoes[semi] = r
    return [razoes[k] for k in range(12)]


TEMPERAMENTOS = {
    "igual": [2 ** (k / 12) for k in range(12)],
    "zhu_zaiyu": [2 ** (k / 12) for k in range(12)],
    "sanfen_sunyi": _sanfen_sunyi(),
    "justa": [1, 16 / 15, 9 / 8, 6 / 5, 5 / 4, 4 / 3, 45 / 32, 3 / 2, 8 / 5, 5 / 3, 9 / 5, 15 / 8],
}


@dataclass
class Afinacao:
    """Converte qualquer notação de altura em Hz.

    la4       : referência (Hz)
    temperamento : chave de TEMPERAMENTOS ou 'personalizada'
    tonica    : nota a partir da qual o temperamento não-igual é construído (geralmente o 宫 da peça)
    cents     : desvios extras por classe de nota (12 valores) somados a tudo
    """
    la4: float = 440.0
    temperamento: str = "igual"
    tonica: str | int = "C"
    cents: list = field(default_factory=lambda: [0.0] * 12)
    tabela: list | None = None  # 12 razões para 'personalizada'

    def __post_init__(self):
        if self.temperamento not in TEMPERAMENTOS and self.temperamento != "personalizada":
            raise ValueError(f"temperamento desconhecido: {self.temperamento}. "
                             f"Opções: {', '.join(list(TEMPERAMENTOS) + ['personalizada'])}")
        self._tonica_pc = int(nota_para_midi(self.tonica + "4") if isinstance(self.tonica, str)
                           else int(self.tonica)) % 12

    def razoes(self):
        if self.temperamento == "personalizada":
            if not self.tabela or len(self.tabela) != 12:
                raise ValueError("temperamento personalizado precisa de 'tabela' com 12 razões")
            return list(self.tabela)
        return TEMPERAMENTOS[self.temperamento]

    def hz_midi(self, midi: float) -> float:
        """MIDI (pode ser fracionário: 60.5 = dó + 50 cents) → Hz no temperamento."""
        m = float(midi)
        base = int(np.floor(m))
        frac = m - base
        pc = (base - self._tonica_pc) % 12
        # tônica de referência na mesma oitava, afinada em 12-TET a partir do lá
        midi_ton = base - pc
        f_ton = self.la4 * 2 ** ((midi_ton - 69) / 12)
        f = f_ton * self.razoes()[pc]
        f *= 2 ** ((self.cents[base % 12] + 100 * frac) / 1200)
        return float(f)

    def hz(self, altura) -> float:
        """Aceita: 'A4', 'C#5', 'Bb3', 'sol3', 'do#4', 'A4+15' (cents), 440.0 (Hz se > 127 ou
        string 'hz:440'), 69 (MIDI int), ou objeto com .midi."""
        if isinstance(altura, (int, np.integer)):
            return self.hz_midi(int(altura))
        if isinstance(altura, float):
            return float(altura) if altura > 127 else self.hz_midi(altura)
        if isinstance(altura, str):
            s = altura.strip()
            if s.lower().startswith("hz:"):
                return float(s[3:])
            return self.hz_midi(nota_para_midi(s))
        raise TypeError(f"altura não reconhecida: {altura!r}")


_RE_NOTA = re.compile(r"^\s*([A-Ga-g]|do|dó|re|ré|mi|fa|fá|sol|la|lá|si)([#♯b♭x]*)(-?\d+)([+-]\d+(?:\.\d+)?)?\s*$",
                      re.IGNORECASE)


def nota_para_midi(s: str) -> float:
    """'A4' → 69, 'C#5' → 73, 'Bb3' → 58, 'sol3' → 55, 'A4+20' → 69.2."""
    m = _RE_NOTA.match(s)
    if not m:
        raise ValueError(f"nota inválida: {s!r} (exemplos: A4, C#5, Bb3, sol3, A4+20)")
    nome, acid, oit, cents = m.groups()
    up = nome.upper()
    pc = NOMES[up] if up in NOMES else NOMES_PT[up]
    for a in acid:
        pc += {"#": 1, "♯": 1, "x": 2, "b": -1, "♭": -1}[a]
    midi = 12 * (int(oit) + 1) + pc
    return midi + (float(cents) / 100 if cents else 0.0)


def midi_para_nome(m: float) -> str:
    nomes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    k = int(round(m))
    return f"{nomes[k % 12]}{k // 12 - 1}"


@dataclass
class Tom:
    """Tom à chinesa: '1=D' significa que o grau 1 do 简谱 (o 宫) é ré.

    escala: pentatonica | yayue | qingyue | yanyue | cromatica (só afeta grau_para_midi com
    graus fora da escala e as funções de geração); o 简谱 sempre aceita os 7 graus + acidentes.
    oitava: oitava do grau 1 sem pontos.
    """
    tonica: str = "C"
    oitava: int = 4
    escala: str = "qingyue"

    @classmethod
    def de_texto(cls, s: str, oitava: int = 4, escala: str = "qingyue") -> "Tom":
        s = s.strip().replace(" ", "")
        if s.startswith("1="):
            s = s[2:]
        s = s.replace("调", "")
        return cls(s, oitava, escala)

    def midi_do_grau(self, grau: int, acidente: int = 0, oitavas: int = 0) -> int:
        """Grau 1–7 do 简谱 (maior: 1 2 3 4 5 6 7 = 宫 商 角 清角 徵 羽 变宫)."""
        base = nota_para_midi(f"{self.tonica}{self.oitava}")
        semis = [0, 2, 4, 5, 7, 9, 11][grau - 1]
        return int(base + semis + acidente + 12 * oitavas)


def escala_midi(tonica: str, escala: str = "pentatonica", modo: str = "宫", de: str = "C3",
                ate: str = "C6") -> list[int]:
    """Lista as notas MIDI de uma escala/modo entre duas alturas (útil para gerar melodias)."""
    graus = ESCALAS[escala]
    t = nota_para_midi(tonica + "0") % 12
    lo, hi = nota_para_midi(de), nota_para_midi(ate)
    # o modo (宫/商/角/徵/羽) não muda o conjunto de notas, só o repouso: veja final_do_modo
    return [m for m in range(int(lo), int(hi) + 1) if (m - t) % 12 in graus]


def final_do_modo(tonica: str, modo: str, oitava: int = 4) -> int:
    """Nota de repouso do modo (宫调式 termina no 宫, 羽调式 no 羽, etc.)."""
    grau = {"宫": 0, "gong": 0, "商": 2, "shang": 2, "角": 4, "jue": 4, "徵": 7, "zhi": 7,
            "羽": 9, "yu": 9}[modo]
    return int(nota_para_midi(f"{tonica}{oitava}") + grau)
