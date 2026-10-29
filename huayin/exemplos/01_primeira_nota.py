"""01 — a primeira nota, e a mesma nota com técnicas diferentes."""
from _caminho import SAIDA

import huayin as hy

m = hy.Musica("Primeira nota", tempo=60, tom="1=D", reverb="sala")
pipa = m.faixa("pipa", "pipa")

pipa.nota("A3", t=0, dur=1.5, vel=0.7)                 # nota simples (弹)
pipa.nota("A3", t=2, dur=2, tecnica="lun")              # trêmulo dos cinco dedos (轮指)
pipa.nota("A3", t=4.5, dur=1.5, tecnica="tui:cents=200")  # empurra a corda: sobe um tom (推)
pipa.nota("A4", t=6.5, dur=1.5, tecnica="fanyin")       # harmônico (泛音)
pipa.nota("D3", t=8.5, dur=2, vel=0.9, tecnica="sao")   # varre as 4 cordas (扫)

m.exportar(SAIDA / "01_primeira_nota.wav")
