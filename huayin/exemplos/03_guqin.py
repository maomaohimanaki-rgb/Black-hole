"""03 — guqin: os três sons (散 terra, 按 homem, 泛 céu) e a mão esquerda.

Trecho original no estilo das peças de 琴 (não é transcrição de nenhuma peça).
"""
from _caminho import SAIDA

import huayin as hy

m = hy.Musica("Três sons", tempo=50, tom="1=F", reverb="templo", nivel_reverb=0.7)
q = m.faixa("guqin", "guqin")

# 泛音 (harmônicos) nos 徽: 7 = metade da corda (oitava), 9 = 2/3 (quinta acima da oitava)
q.nota("C3", 0, 1.5, 0.6, "fanyin:hui=7")     # harmônico da 1ª corda no 7º 徽 → C3
q.nota("G3", 1.5, 1.5, 0.6, "fanyin:hui=9")
q.nota("F4", 3, 2.5, 0.55, "fanyin")         # sem hui: o motor acha corda e 徽 pela altura
# 散音 + 按音 com a mão esquerda
q.nota("C2", 6, 3, 0.8, "bo")                 # polegar na corda grave solta
q.nota("A2", 9, 2, 0.7, "gou+yin")            # apertada com 吟 (vibrato pequeno)
q.nota("C3", 11, 1, 0.6, "deslizar")          # 上: desliza da anterior sem novo ataque
q.nota("A2", 12, 2, 0.6, "deslizar")          # 下: volta
q.nota("G2", 14, 3, 0.7, "tiao+nao")          # 猱: vibrato largo que vai fechando
q.nota("F2", 17, 2, 0.7, "jinfu")             # 进复: sobe um passo e volta
q.nota("F2", 19.5, 3, 0.7, "gunfu")           # 滚拂: glissando pelas 7 cordas

# o 箫 é o par tradicional do 琴 (琴箫合奏)
x = m.faixa("xiao", "xiao", volume_db=-6, pan=0.3)
x.jianpu("0 0 0 0 | 0 0 0 0 | 0 0 5 - | 6 - 5 3 | 2 - - - | 1 - - - |", 0, oitava=4)

m.exportar(SAIDA / "03_guqin.wav")
