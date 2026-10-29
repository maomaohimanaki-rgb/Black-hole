"""Importar e exportar MIDI (mido).

Importação: cada canal vira uma faixa. O programa General MIDI escolhe o instrumento chinês mais
parecido (ex.: 107 Koto → guzheng, 110 Fiddle → erhu, 111 Shanai → suona). Pitch bend vira curva
de afinação; CC1 (modulation) vira vibrato; CC64 (pedal) deixa as cordas soarem.
Exportação: notas, andamentos e programa de cada faixa (micro-afinações e técnicas se perdem).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

# General MIDI (0-based) → instrumento do motor
GM_PARA_HUAYIN = {
    range(0, 8): "yangqin", range(8, 16): "bianzhong", range(16, 24): "sheng", range(24, 32): "pipa",
    range(32, 40): "ruan", range(40, 48): "erhu", range(48, 56): "erhu", range(56, 64): "suona",
    range(64, 72): "guanzi", range(72, 80): "dizi", range(80, 104): "sheng", range(104, 105): "sanxian",
    range(105, 106): "sanxian", range(106, 107): "pipa", range(107, 108): "guzheng", range(108, 109): "yunluo",
    range(109, 110): "hulusi", range(110, 111): "erhu", range(111, 112): "suona", range(112, 113): "pengling",
    range(113, 114): "yunluo", range(114, 115): "muyu", range(115, 116): "muyu", range(116, 117): "tanggu",
    range(117, 119): "tanggu", range(119, 128): "chaoluo",
}
_ESPECIFICOS = {15: "yangqin", 14: "bianzhong", 9: "bianzhong", 13: "bianqing", 73: "dizi", 75: "xiao", 79: "xun",
                24: "pipa", 46: "konghou", 105: "pipa", 106: "sanxian"}
HUAYIN_PARA_GM = {"pipa": 105, "pipa_tang": 105, "guqin": 107, "guzheng": 107, "konghou": 46, "se": 107,
                  "ruan": 24, "liuqin": 105, "yueqin": 105, "sanxian": 106, "yangqin": 15, "erhu": 110,
                  "gaohu": 110, "zhonghu": 110, "banhu": 110, "jinghu": 110, "dizi": 73, "xiao": 75, "xun": 79,
                  "suona": 111, "guanzi": 68, "sheng": 21, "hulusi": 109, "bawu": 72, "bianzhong": 14,
                  "bianqing": 13, "yunluo": 113, "pengling": 112, "qing": 14, "daluo": 119, "xiaoluo": 119,
                  "chaoluo": 119, "jingbo": 119, "naobo": 119, "xiaobo": 119, "tanggu": 116, "dagu": 116,
                  "bangu": 115, "muyu": 115, "bangzi": 115, "paiban": 115}
# bateria GM (canal 10) → percussão chinesa
GM_BATERIA = {35: "dagu", 36: "dagu", 38: "bangu", 40: "bangu", 37: "bangzi", 39: "paiban", 41: "tanggu", 43: "tanggu",
              45: "tanggu", 47: "tanggu", 48: "tanggu", 50: "tanggu", 49: "naobo", 57: "naobo", 51: "jingbo",
              52: "chaoluo", 55: "xiaobo", 59: "jingbo", 53: "pengling", 76: "muyu", 77: "muyu", 81: "pengling"}


def instrumento_gm(programa: int) -> str:
    if programa in _ESPECIFICOS:
        return _ESPECIFICOS[programa]
    for r, nome in GM_PARA_HUAYIN.items():
        if programa in r:
            return nome
    return "pipa"


def importar_midi(caminho, sr: int = 48000, instrumentos: dict | None = None):
    """instrumentos: {canal: 'id'} para forçar o instrumento de cada canal (0–15)."""
    import mido

    from .curvas import CurvaAltura
    from .musica import Musica
    from .nota import Nota

    mid = mido.MidiFile(str(caminho))
    tpb = mid.ticks_per_beat
    eventos = []
    for tr in mid.tracks:
        t = 0
        for msg in tr:
            t += msg.time
            eventos.append((t, msg))
    eventos.sort(key=lambda e: e[0])
    m = Musica(Path(caminho).stem, 120.0, sr=sr)
    primeiro_tempo = True
    abertas: dict = {}
    notas: dict = {}
    programa = {c: 0 for c in range(16)}
    bend = {c: [] for c in range(16)}
    mod = {c: 0 for c in range(16)}
    for tick, msg in eventos:
        beat = tick / tpb
        if msg.type == "set_tempo":
            bpm = mido.tempo2bpm(msg.tempo)
            if primeiro_tempo and beat == 0:
                m.tempo.bpm_inicial = bpm
            else:
                m.andamento(beat, bpm)
            primeiro_tempo = False
        elif msg.type == "program_change":
            programa[msg.channel] = msg.program
        elif msg.type == "pitchwheel":
            bend[msg.channel].append((beat, msg.pitch / 8192 * 200))  # ±2 semitons
        elif msg.type == "control_change" and msg.control == 1:
            mod[msg.channel] = msg.value
        elif msg.type == "note_on" and msg.velocity > 0:
            abertas[(msg.channel, msg.note)] = (beat, msg.velocity, mod[msg.channel])
        elif msg.type in ("note_off", "note_on"):
            k = (msg.channel, msg.note)
            if k in abertas:
                b0, v, md = abertas.pop(k)
                notas.setdefault(msg.channel, []).append((b0, beat - b0, msg.note, v, md))
    for canal, lista in sorted(notas.items()):
        if canal == 9:
            por_inst: dict = {}
            for b0, d, nota, v, _ in lista:
                por_inst.setdefault(GM_BATERIA.get(nota, "tanggu"), []).append((b0, d, v))
            for inst, ls in por_inst.items():
                f = m.faixa(f"perc_{inst}", inst)
                for b0, d, v in ls:
                    f.notas.append(Nota(b0, max(d, 0.1), None, v / 127))
            continue
        inst = (instrumentos or {}).get(canal) or instrumento_gm(programa[canal])
        f = m.faixa(f"canal{canal + 1}_{inst}", inst)
        for b0, d, nota, v, md in lista:
            curva = None
            bs = [(b, c) for b, c in bend[canal] if b0 <= b < b0 + d]
            if bs:
                seg = m.tempo.segundos
                curva = CurvaAltura([(0.0, _bend_em(bend[canal], b0), "degrau")])
                for b, c in bs:
                    curva.para(seg(b) - seg(b0), c, "linear")
            elif _bend_em(bend[canal], b0):
                curva = CurvaAltura([(0.0, _bend_em(bend[canal], b0), "degrau")])
            n = Nota(b0, max(d, 0.02), int(nota), v / 127, curva=curva)
            if md > 10 and "vibrato" in f.instrumento.TECNICAS:
                n.tecnicas.append(("vibrato", {}))
            f.notas.append(n)
        f.cursor = f.fim
    return m


def _bend_em(lista, beat):
    v = 0.0
    for b, c in lista:
        if b <= beat:
            v = c
        else:
            break
    return v


def _latin1(texto: str) -> str:
    """Nomes de faixa MIDI são latin-1: tira os caracteres chineses (o resto fica)."""
    limpo = "".join(c for c in texto if ord(c) < 256).strip()
    return " ".join(limpo.split()) or "huayin"


def exportar_midi(musica, caminho):
    import mido

    tpb = 480
    mid = mido.MidiFile(ticks_per_beat=tpb)
    meta = mido.MidiTrack()
    mid.tracks.append(meta)
    meta.append(mido.MetaMessage("track_name", name=_latin1(musica.titulo), time=0))
    eventos = [(0.0, musica.tempo.bpm_inicial)] + [(b, v) for b, v, _ in musica.tempo.eventos]
    t_ant = 0
    for b, v in sorted(eventos):
        tick = int(round(b * tpb))
        meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(v), time=tick - t_ant))
        t_ant = tick
    canal = 0
    for f in musica.faixas:
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=_latin1(f"{f.nome} ({f.instrumento.id})"), time=0))
        percussao = f.instrumento.familia.startswith("percussão")
        ch = 9 if percussao and not any(n.altura is not None for n in f.notas) else canal
        if ch != 9:
            base_id = f.instrumento.id.split("_")[0] if f.instrumento.id not in HUAYIN_PARA_GM else f.instrumento.id
            tr.append(mido.Message("program_change", channel=ch, program=HUAYIN_PARA_GM.get(base_id, 105), time=0))
            canal = (canal + 1) % 16
            if canal == 9:
                canal = 10
        evs = []
        for n in f.notas:
            if n.altura is None:
                nota_midi = 41
            else:
                hz = musica.afinacao.hz(n.altura)
                nota_midi = int(np.clip(round(69 + 12 * np.log2(hz / musica.afinacao.la4)), 0, 127))
            v = int(np.clip(round(n.vel * 127), 1, 127))
            evs.append((int(round(n.inicio * tpb)), 1, mido.Message("note_on", channel=ch, note=nota_midi, velocity=v)))
            evs.append((int(round(n.fim * tpb)), 0, mido.Message("note_off", channel=ch, note=nota_midi, velocity=0)))
        evs.sort(key=lambda e: (e[0], e[1]))
        t_ant = 0
        for tick, _, msg in evs:
            msg.time = tick - t_ant
            t_ant = tick
            tr.append(msg)
    mid.save(str(caminho))
    return Path(caminho)
