"""Linha de comando: python -m huayin <comando> ...   (ou só 'huayin' se instalado com pip)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_listar(a):
    import huayin as hy
    atual = None
    for i in sorted(hy.listar_instrumentos(a.familia), key=lambda x: (x["familia"], x["id"])):
        if i["familia"] != atual:
            atual = i["familia"]
            print(f"\n{atual}")
        var = f"  (variante de {i['variante_de']})" if i.get("variante_de") else ""
        print(f"  {i['id']:16s} {i['nome_cn']:6s} {i['nome']:40s} {i['extensao'][0]}–{i['extensao'][1]:5s} "
              f"{i['tecnicas']:3d} técnicas{var}")


def _cmd_info(a):
    import huayin as hy
    print(hy.ajuda(a.instrumento))


def _cmd_nota(a):
    import huayin as hy
    y = hy.nota_unica(a.instrumento, a.altura, a.dur, a.vel, a.tecnica, sr=a.sr, reverb=a.reverb)
    hy.salvar_audio(a.saida, y, a.sr)
    print(f"✔ {a.saida}")


def _cmd_jianpu(a):
    import huayin as hy
    m = hy.Musica("jianpu", tempo=a.tempo, tom=a.tom, sr=a.sr, reverb=a.reverb)
    f = m.faixa("f", a.instrumento)
    f.jianpu(a.texto)
    m.exportar(a.saida)


def _cmd_render(a):
    import huayin as hy
    m = hy.Musica.carregar(a.arquivo)
    if a.sr:
        m.sr = a.sr
        for f in m.faixas:
            f.instrumento.sr = a.sr
    saida = a.saida or str(Path(a.arquivo).with_suffix(".wav"))
    print(f"♪ {m.titulo} — {len(m.faixas)} faixas, {m.duracao():.1f} s")
    if a.stems:
        for p in m.exportar_stems(a.stems):
            print(f"  {p}")
    m.exportar(saida, bits=a.bits, mono=a.mono, normalizar=None if a.sem_normalizar else "lufs")
    if a.midi:
        print(f"✔ {m.exportar_midi(a.midi)}")


def _cmd_demo(a):
    from .demos import demo_catalogo, demo_peca
    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    if a.catalogo:
        demo_catalogo(pasta, sr=a.sr, so=a.instrumento)
    else:
        demo_peca(pasta / "huayin_demo.wav", sr=a.sr)


def _cmd_doc(a):
    import huayin as hy
    from .instrumentos import REGISTRO
    partes = ["# Referência de instrumentos (gerado por `python -m huayin doc`)", "",
              "Não edite à mão: rode `python -m huayin doc -o docs/INSTRUMENTOS.md` depois de mudar um instrumento.", ""]
    por_familia = {}
    for c in REGISTRO.values():
        por_familia.setdefault(c.familia, []).append(c)
    for fam, cs in por_familia.items():
        partes += [f"# {fam}", ""]
        for c in cs:
            partes.append(c.descrever())
    partes += ["# Variantes (presets)", "", "| id | nome | base | parâmetros |", "|---|---|---|---|"]
    for k, (b, nome, desc, ps) in hy.VARIANTES.items():
        partes.append(f"| `{k}` | {nome} | `{b}` | {', '.join(f'{x}={y!r}' for x, y in ps.items())} |")
    texto = "\n".join(partes) + "\n"
    if a.saida:
        Path(a.saida).write_text(texto, encoding="utf-8")
        print(f"✔ {a.saida}")
    else:
        print(texto)


def main(argv=None):
    p = argparse.ArgumentParser(prog="huayin", description="华音 Huayin — instrumentos clássicos chineses por síntese física")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("listar", help="lista os instrumentos")
    s.add_argument("--familia", default=None)
    s.set_defaults(f=_cmd_listar)

    s = sub.add_parser("info", help="ficha de um instrumento (parâmetros e técnicas)")
    s.add_argument("instrumento")
    s.set_defaults(f=_cmd_info)

    s = sub.add_parser("nota", help="renderiza uma nota")
    s.add_argument("instrumento")
    s.add_argument("altura", nargs="?", default="A4")
    s.add_argument("-o", "--saida", default="nota.wav")
    s.add_argument("--dur", type=float, default=2.0)
    s.add_argument("--vel", type=float, default=0.7)
    s.add_argument("--tecnica", default=None)
    s.add_argument("--reverb", default="sala")
    s.add_argument("--sr", type=int, default=48000)
    s.set_defaults(f=_cmd_nota)

    s = sub.add_parser("jianpu", help="toca um trecho de 简谱 num instrumento")
    s.add_argument("instrumento")
    s.add_argument("texto")
    s.add_argument("-o", "--saida", default="jianpu.wav")
    s.add_argument("--tempo", type=float, default=80)
    s.add_argument("--tom", default="1=D")
    s.add_argument("--reverb", default="palacio_tang")
    s.add_argument("--sr", type=int, default=48000)
    s.set_defaults(f=_cmd_jianpu)

    s = sub.add_parser("render", help="renderiza uma partitura (.json, .jp, .mid)")
    s.add_argument("arquivo")
    s.add_argument("-o", "--saida", default=None, help=".wav | .flac | .ogg")
    s.add_argument("--bits", type=int, default=24, choices=(16, 24, 32))
    s.add_argument("--mono", action="store_true")
    s.add_argument("--sr", type=int, default=None)
    s.add_argument("--stems", default=None, help="pasta para salvar cada faixa separada")
    s.add_argument("--midi", default=None, help="também exporta .mid")
    s.add_argument("--sem-normalizar", action="store_true")
    s.set_defaults(f=_cmd_render)

    s = sub.add_parser("demo", help="gera demonstrações")
    s.add_argument("-o", "--saida", default="demos")
    s.add_argument("--catalogo", action="store_true", help="um arquivo por instrumento com suas técnicas")
    s.add_argument("--instrumento", default=None, help="só este instrumento (com --catalogo)")
    s.add_argument("--sr", type=int, default=48000)
    s.set_defaults(f=_cmd_demo)

    s = sub.add_parser("doc", help="gera a referência de instrumentos em markdown")
    s.add_argument("-o", "--saida", default=None)
    s.set_defaults(f=_cmd_doc)

    a = p.parse_args(argv)
    try:
        a.f(a)
    except (ValueError, FileNotFoundError) as e:
        print(f"erro: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
