"""06 — a mesma melodia em três afinações: igual (朱载堉), 三分损益 (pitagórica) e justa.

Ouça as terças (3 do 简谱): no 三分损益 ficam largas e brilhantes, na justa ficam puras e calmas.
"""
from _caminho import SAIDA

import huayin as hy

melodia = "1 3 5 3 | 1+3+5 - - - |"
for temp in ("igual", "sanfen_sunyi", "justa"):
    m = hy.Musica(f"afinação {temp}", tempo=70, tom="1=D", temperamento=temp, reverb="sala")
    f = m.faixa("zheng", "guzheng")
    f.jianpu(melodia, 0, oitava=4)
    m.exportar(SAIDA / f"06_{temp}.wav")
