"""Demonstrações: catálogo de técnicas por instrumento e uma peça curta original (长安夜)."""
from __future__ import annotations

from pathlib import Path

from .afinacao import midi_para_nome, nota_para_midi
from .composicao.musica import Musica
from .instrumentos import REGISTRO, VARIANTES, criar

# técnicas que precisam de uma nota antes (ligam na anterior)
_LIGADURAS = {"hammer", "puxada", "deslizar", "legato", "portamento", "liangong"}
_SEM_ALTURA = {"daluo", "xiaoluo", "chaoluo", "jingbo", "naobo", "xiaobo", "tanggu", "dagu", "bangu", "muyu",
               "bangzi", "paiban", "pengling", "qing"}


def _meio(inst) -> str:
    lo, hi = (nota_para_midi(x) for x in inst.extensao)
    m = int(round(lo + 0.4 * (hi - lo)))
    # cai numa nota da pentatônica de ré (soa "chinesa" em qualquer instrumento)
    while (m - 2) % 12 not in (0, 2, 4, 7, 9):
        m += 1
    return midi_para_nome(m)


def demo_catalogo(pasta, sr=48000, so=None):
    """Um .wav por instrumento: a nota pura e depois cada técnica, separadas por silêncio."""
    pasta = Path(pasta)
    ids = [so] if so else list(REGISTRO) + list(VARIANTES)
    for iid in ids:
        inst = criar(iid, sr)
        m = Musica(f"catálogo {iid}", tempo=60, tom="1=D", sr=sr, reverb="sala", nivel_reverb=0.6)
        f = m.faixa(iid, iid)
        alt = None if iid in _SEM_ALTURA else _meio(inst)
        t = 0.0
        f.nota(alt, t, 1.5, 0.7)
        t += 2.5
        for nome in inst.TECNICAS:
            if nome in _LIGADURAS:
                alt2 = midi_para_nome(nota_para_midi(alt) - 2) if alt else None
                f.nota(alt2, t, 0.8, 0.7)
                f.nota(alt, t + 0.8, 1.2, 0.7, nome)
            else:
                f.nota(alt, t, 1.8, 0.7, nome)
            t += 3.0
        saida = pasta / f"{iid}.wav"
        m.exportar(saida, verbose=False)
        print(f"✔ {saida}  ({len(inst.TECNICAS)} técnicas: {', '.join(inst.TECNICAS)})")


def peca_changan(sr=48000) -> Musica:
    """长安夜 — Noite em Chang'an (original, ~55 s): 散板 com guqin e xiao, depois a corte Tang."""
    m = Musica("长安夜 Noite em Chang'an", tempo=56, tom="1=D", sr=sr, reverb="palacio_tang", nivel_reverb=0.9,
               autor="huayin demo")
    # ---------------- 散板: tigela do templo, harmônicos do guqin, xiao ao longe
    qing = m.faixa("qing", "qing", volume_db=-10, pan=0.4, reverb=0.5)
    qing.nota("D4", 0, 6, 0.5)
    qin = m.faixa("guqin", "guqin", volume_db=-1, pan=-0.25, reverb=0.35)
    qin.nota("A4", 0.5, 2, 0.55, "fanyin")
    qin.nota("D5", 2.0, 2, 0.5, "fanyin")
    qin.nota("A3", 3.5, 3, 0.6, "gou+nao")
    qin.nota("B3", 5.5, 1.5, 0.5, "deslizar")
    qin.nota("D2", 7.5, 3, 0.75, "bo")
    qin.nota("D3", 7.5, 3, 0.5, "cuo")
    xiao = m.faixa("xiao", "xiao", volume_db=-5, pan=0.3, reverb=0.45)
    xiao.jianpu("0 0 0 0 | 0 0 5 - | 6 - 5/ 3/ 2 | 3 - - - |", 0.0, oitava=4)
    # ---------------- corte Tang: andamento sobe aos poucos
    m.andamento(12, 56)
    m.andamento(16, 84, rampa=True)
    ini = 16
    pipa = m.faixa("pipa Tang", "pipa_tang", volume_db=-2, pan=-0.35, reverb=0.25)
    pipa.nota("D3", ini, 1, 0.85, "sao")
    pipa.jianpu("!mf 5 6 1' 6 | 5. 3/ 2 3 | 5 3 2 1 | 2{yaobo} - - - |"
                "3 5 6 1' | 2' 1' 6 5 | 6 5 3 2 | 1{nian} - - - |", ini + 1, oitava=3)
    pipa.nota("D3", ini + 33, 2, 0.95, "huaxian")
    erhu = m.faixa("erhu", "erhu", volume_db=-6, pan=0.3, reverb=0.3)
    erhu.jianpu("0 0 0 0 | 0 0 0 0 | !mp 3 - 5 6 | 5 - - - |"
                "(1' - 6 5) | 3 - 2 3 | !mf 5 - 3 2 | (1 - 2 -) |", ini + 1, oitava=4)
    dizi = m.faixa("dizi", "dizi", volume_db=-9, pan=0.15, reverb=0.3)
    dizi.jianpu("0 0 0 0 | 0 0 0 0 | 0 0 0 0 | 0 0 0 0 |"
                "!mf [6]5 - 6 1' | 2'{vibrato} - 1' 6 | 5 6 [2']1' 6 | 5{huashe} - - - |", ini + 1, oitava=5)
    sheng = m.faixa("sheng", "sheng", volume_db=-14, pan=-0.1, reverb=0.4)
    t = ini + 1
    for a, d in [("D5", 8), ("A4", 4), ("B4", 4), ("D5", 8), ("A4", 4), ("D5", 4)]:
        sheng.nota(a, t, d, 0.45, "hesheng")
        t += d
    zhong = m.faixa("bianzhong", "bianzhong", volume_db=-6, pan=0.0, reverb=0.5)
    for b, a in [(ini + 1, "D3"), (ini + 9, "A3"), (ini + 17, "D3"), (ini + 25, "A2"), (ini + 33, "D2")]:
        zhong.nota(a, b, 4, 0.8)
    tang = m.faixa("tanggu", "tanggu", volume_db=-8, pan=0.2, reverb=0.25)
    for c in range(8):
        b = ini + 1 + 4 * c
        tang.nota(None, b, 1, 0.75)
        tang.nota(None, b + 2.5, 0.5, 0.5)
    tang.nota(None, ini + 31, 2, 0.6, "rufo:cresc=0.3-1.0")
    ban = m.faixa("paiban", "paiban", volume_db=-12, pan=-0.2, reverb=0.25)
    for c in range(8):
        ban.nota(None, ini + 1 + 4 * c, 1, 0.6)
    gongo = m.faixa("daluo", "daluo", volume_db=-6, pan=0.1, reverb=0.4)
    gongo.nota(None, ini + 33, 4, 0.9)
    return m


def demo_peca(saida, sr=48000):
    m = peca_changan(sr)
    m.exportar(saida)
    return m


def comparar_seda_aco(saida, sr=48000):
    """A mesma frase no pipa Tang com seda e com aço: útil para ouvir o efeito do material."""
    m = Musica("seda × aço", tempo=80, tom="1=D", sr=sr)
    a = m.faixa("seda", "pipa_tang", material="seda_fina")
    b = m.faixa("aco", "pipa_tang", material="aco_nylon")
    frase = "5 6 1' 6 | 5. 3/ 2 3 | 5 - - - |"
    a.jianpu(frase, 0, oitava=3)
    b.jianpu(frase, 14, oitava=3)
    m.exportar(saida)
    return m
