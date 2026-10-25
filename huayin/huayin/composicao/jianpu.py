"""Leitor de 简谱 (jianpu, notação numérica chinesa) em texto simples.

Resumo (detalhes e exemplos em docs/PARTITURA.md):

    1 2 3 4 5 6 7     graus da escala (1 = tônica do tom, ex.: 1=D)
    0                 pausa
    X                 golpe sem altura (percussão)
    1' 1''            oitava acima (pontos em cima)          1, 1,,   oitava abaixo
    #4  b7            sustenido / bemol
    5/  5//           colcheia / semicolcheia (cada / divide por 2)
    5.  5..           pontuada / duplamente pontuada
    5 -  - -          cada traço soma um tempo à nota anterior
    5~ 5              liga (soma a duração)
    1+3+5             acorde
    [56]1             apojaturas (notas de enfeite rápidas antes do 1)
    5{lun} 3{tui:200} técnica (com parâmetros: {nome:p=v,p2=v})
    ( 1 2 3 )         ligadura/legato (as notas de dentro não rearticulam)
    <3 1 2 3 >        quiáltera: 3 notas no tempo de 2 (<5 ... > = 5 no tempo de 4)
    !p !mf !ff        dinâmica   !< ... !f  crescendo até a próxima dinâmica   !> diminuendo
    |  ||             barras (só para leitura; '||' confere nada)
    @tempo=72         diretivas: @tempo=BPM  @rit (daqui até o próximo @tempo muda aos poucos) @tom=1=G
                      @oitava=5  @vel=0.7  @tecnica=lun  @corda=2  @dur=0.5 (duração base)
    % comentário      até o fim da linha (também //)
"""
from __future__ import annotations

import re

from ..afinacao import Tom
from .nota import DINAMICAS, Nota, normalizar_tecnicas

_RE_NOTA = re.compile(
    r"^(?P<grace>\[[^\]]*\])?"
    r"(?P<acid>[#b]*)"
    r"(?P<grau>[0-7Xx])"
    r"(?P<oit>[',]*)"
    r"(?P<dur>[/.]*)"
    r"(?P<tie>~?)"
    r"(?P<tec>(\{[^}]*\})*)$"
)


def _tokens(texto: str) -> list[str]:
    linhas = []
    for linha in texto.splitlines():
        linha = re.split(r"%|//", linha, maxsplit=1)[0]
        linhas.append(linha)
    s = " ".join(linhas)
    # separa parênteses e barras grudados (mas não dentro de {...} ou [...])
    out, buf, prof = [], "", 0
    for ch in s:
        if ch in "{[":
            prof += 1
        elif ch in "}]":
            prof -= 1
        if prof == 0 and ch in "()|":
            if buf.strip():
                out.append(buf.strip())
            out.append(ch)
            buf = ""
        elif prof == 0 and ch.isspace():
            if buf.strip():
                out.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf.strip())
    # junta '||' e trata '<3' grudado
    final = []
    for t in out:
        if t == "|" and final and final[-1] == "|":
            continue
        final.append(t)
    return final


def _parse_tecnicas(txt: str) -> list:
    out = []
    for m in re.finditer(r"\{([^}]*)\}", txt or ""):
        out += normalizar_tecnicas(m.group(1))
    return out


def _altura(tom: Tom, acid: str, grau: str, oit: str):
    if grau in "Xx":
        return None
    g = int(grau)
    a = acid.count("#") - acid.count("b")
    o = oit.count("'") - oit.count(",")
    return tom.midi_do_grau(g, a, o)


def ler_jianpu(texto: str, inicio: float = 0.0, tom: Tom | None = None, vel=None, tecnica=None,
               dur_base: float = 1.0):
    """Devolve (notas, tempo_final, diretivas). Tempos em beats (semínima = 1)."""
    tom = tom or Tom()
    t = float(inicio)
    vel_atual = DINAMICAS["mf"] if vel is None else (DINAMICAS[vel] if isinstance(vel, str) else float(vel))
    tec_padrao = normalizar_tecnicas(tecnica) if tecnica else []
    corda = None
    notas: list[Nota] = []
    ultima: Nota | None = None
    ligar_proxima = False
    em_legato = False
    primeira_do_legato = False
    quialtera = []  # pilha de fatores
    rampa = None    # (indice_da_nota_inicial, vel_inicial, sentido)
    diretivas = {"andamento": []}
    rit_pendente = None

    def fator():
        f = 1.0
        for q in quialtera:
            f *= q
        return f

    for tok in _tokens(texto):
        if tok in ("|",):
            continue
        if tok == "(":
            em_legato, primeira_do_legato = True, True
            continue
        if tok == ")":
            em_legato = False
            continue
        if tok.startswith("<") and tok[1:].isdigit():
            n = int(tok[1:])
            m = {2: 3, 3: 2, 4: 3, 5: 4, 6: 4, 7: 4, 9: 8}.get(n, max(1, n - 1))
            quialtera.append(m / n)
            continue
        if tok == ">":
            if quialtera:
                quialtera.pop()
            continue
        if tok.startswith("!"):
            d = tok[1:]
            if d in ("<", ">"):
                rampa = (len(notas), vel_atual, d)
                continue
            if d not in DINAMICAS:
                raise ValueError(f"dinâmica desconhecida: {tok} (use {', '.join('!' + k for k in DINAMICAS)})")
            novo = DINAMICAS[d]
            if rampa is not None:
                i0, v0, _ = rampa
                trecho = notas[i0:]
                for k, n in enumerate(trecho):
                    u = (k + 1) / (len(trecho) + 1)
                    n.vel = v0 + (novo - v0) * u
                rampa = None
            vel_atual = novo
            continue
        if tok.startswith("@"):
            k, _, v = tok[1:].partition("=")
            k = k.lower()
            if k == "tempo":
                if rit_pendente is not None:
                    diretivas["andamento"].append((t, float(v), True))
                    rit_pendente = None
                else:
                    diretivas["andamento"].append((t, float(v), False))
            elif k in ("rit", "accel", "rampa"):
                # ancora o andamento atual aqui; o próximo @tempo chega nele gradualmente
                diretivas["andamento"].append((t, None, False))
                rit_pendente = True
            elif k == "tom":
                tom = Tom.de_texto(v, tom.oitava, tom.escala)
            elif k == "oitava":
                tom = Tom(tom.tonica, int(v), tom.escala)
            elif k == "vel":
                vel_atual = DINAMICAS[v] if v in DINAMICAS else float(v)
            elif k == "tecnica":
                tec_padrao = normalizar_tecnicas(v) if v else []
            elif k == "corda":
                corda = None if v in ("", "auto") else int(v)
            elif k == "dur":
                dur_base = float(v)
            else:
                raise ValueError(f"diretiva desconhecida: {tok}")
            continue
        if tok == "-":
            if ultima is None:
                raise ValueError("traço '-' sem nota antes")
            ultima.duracao += dur_base * fator()
            t += dur_base * fator()
            continue
        if "+" in tok and not tok.startswith("{"):
            partes = tok.split("+")
            ms = [_RE_NOTA.match(p) for p in partes]
            if not all(ms):
                raise ValueError(f"acorde inválido: {tok}")
            d = _duracao(ms[0].group("dur"), dur_base) * fator()
            tecs = _parse_tecnicas(ms[-1].group("tec")) or tec_padrao
            for m in ms:
                notas.append(Nota(t, d, _altura(tom, m.group("acid"), m.group("grau"), m.group("oit")), vel_atual,
                                  list(tecs), corda))
            ultima = notas[-1]
            t += d
            continue
        m = _RE_NOTA.match(tok)
        if not m:
            raise ValueError(f"não entendi '{tok}' no 简谱 (veja docs/PARTITURA.md)")
        d = _duracao(m.group("dur"), dur_base) * fator()
        if m.group("grau") == "0":
            t += d
            ultima = None
            continue
        alt = _altura(tom, m.group("acid"), m.group("grau"), m.group("oit"))
        tecs = _parse_tecnicas(m.group("tec")) or list(tec_padrao)
        # apojaturas: roubam um pouquinho do começo da nota
        if m.group("grace"):
            graces = re.findall(r"[#b]*[1-7][',]*", m.group("grace")[1:-1])
            dg = min(0.12, d * 0.25)
            t_g = t - dg * len(graces)  # 倚音: as notas de enfeite vêm antes do tempo
            for gtok in graces:
                gm = _RE_NOTA.match(gtok)
                notas.append(Nota(max(t_g, 0.0), dg, _altura(tom, gm.group("acid"), gm.group("grau"), gm.group("oit")),
                                  vel_atual * 0.8, [], corda))
                t_g += dg
        if ligar_proxima and ultima is not None and ultima.altura == alt:
            ultima.duracao += d
        else:
            n = Nota(t, d, alt, vel_atual, tecs, corda, legato=(em_legato and not primeira_do_legato))
            notas.append(n)
            ultima = n
            primeira_do_legato = False
        ligar_proxima = bool(m.group("tie"))
        t += d
    return notas, t, diretivas


def _duracao(s: str, base: float) -> float:
    d = base / (2 ** s.count("/"))
    pontos = s.count(".")
    if pontos:
        d *= 2 - 0.5 ** pontos
    return d


def ler_arquivo_jianpu(texto: str, cls_musica):
    """Arquivo .jp: cabeçalho 'chave: valor' e blocos de faixa.

        titulo: Jasmim
        tempo: 72
        tom: 1=D
        reverb: palacio_tang

        [faixa erhu: erhu]   (nome: instrumento)
        volume_db: -2
        pan: -0.2
        3 3/ 5/ 6/ 1'/ 1'/ 6/ | 5 5/ 6/ 5 - |
    """
    cab, faixas, atual = {}, [], None
    for linha in texto.splitlines():
        lc = re.split(r"%|//", linha, maxsplit=1)[0].rstrip()
        m = re.match(r"^\s*\[faixa\s+([^:\]]+)(?::\s*([^\]]+))?\]\s*$", lc)
        if m:
            atual = {"nome": m.group(1).strip(), "instrumento": (m.group(2) or m.group(1)).strip(), "kv": {},
                     "musica": []}
            faixas.append(atual)
            continue
        kv = re.match(r"^\s*([a-z_0-9]+)\s*:\s*(.+)$", lc)
        if kv and not re.match(r"^\s*[0-7X]", lc):
            (cab if atual is None else atual["kv"])[kv.group(1)] = kv.group(2).strip()
            continue
        if atual is not None and lc.strip():
            atual["musica"].append(lc)
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return v
    m = cls_musica(cab.get("titulo", "Sem título"), float(cab.get("tempo", 90)), cab.get("compasso", "4/4"),
                   cab.get("tom", "1=C"), float(cab.get("la4", 440)), cab.get("temperamento", "igual"), None,
                   int(cab.get("sr", 48000)), int(cab.get("semente", 0)), cab.get("reverb", "palacio_tang"),
                   float(cab.get("nivel_reverb", 1.0)), int(cab.get("oitava", 4)), cab.get("autor", ""))
    for f in faixas:
        kv = dict(f["kv"])
        mix = {k: float(kv.pop(k)) for k in ("volume_db", "pan", "largura", "reverb") if k in kv}
        tom_f = kv.pop("tom", None)
        oit = kv.pop("oitava", None)
        inicio = float(kv.pop("inicio", 0.0))
        hum = kv.pop("humanizar", None)
        params = {k: num(v) for k, v in kv.items()}
        fx = m.faixa(f["nome"], f["instrumento"], **mix, **params)
        if hum:
            fx.humanizar(*[float(x) for x in hum.split()])
        fx.jianpu("\n".join(f["musica"]), inicio, tom_f, int(oit) if oit else None)
    return m
