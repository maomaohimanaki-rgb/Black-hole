"""08 — controles avançados: curvas de afinação à mão, automação, humanização, efeitos, stems."""
from _caminho import SAIDA

import huayin as hy

m = hy.Musica("Controles", tempo=80, tom="1=G", reverb="teatro_opera", semente=42)

# --- erhu com curva de afinação desenhada à mão (cents relativos à nota) -------------------------
erhu = m.faixa("erhu", "erhu", vibrato=0)          # desliga o vibrato automático
c = hy.CurvaAltura()
c.inicio_em(-300).para(0.25, 0, "suave")           # entra de uma terça menor abaixo
c.vibrato(inicio=0.5, taxa=6.5, profundidade=30, forma="simetrico", ataque=0.4)
c.para(2.6, 0, "degrau").para(3.0, -500, "suave")  # cai no fim
erhu.nota("D5", 0, 4, 0.7, curva=c)

# --- dizi com dinâmica automatizada e efeitos de inserção ------------------------------------------
dizi = m.faixa("dizi", "bangdi", pan=0.35, reverb=0.4)
dizi.jianpu("!p 5 6 1' 2' | !< 3' 2' 1' 6 | !ff 5 - - - |", 4, oitava=5)
dizi.automacao("pan", [(4, 0.6), (16, -0.2)])      # atravessa o palco
dizi.efeito("eq", bandas=[("passa_alta", 300, 0.7, 0), ("pico", 3500, 1.0, 2.0)])
dizi.efeito("eco", tempo=0.375, realimentacao=0.3, mistura=0.15)

# --- naipe de 4 erhus em uníssono (chorus) com humanização -------------------------------------------
naipe = m.faixa("naipe", "erhu", volume_db=-4, pan=-0.3, largura=1.4)
naipe.jianpu("1' - 7 6 | 5 - - - |", 8, oitava=4)
naipe.efeito("chorus", prof_ms=4, taxa=0.6, mistura=0.5)
naipe.humanizar(tempo_ms=12, vel=0.08, cents=4)

# --- percussão da ópera ----------------------------------------------------------------------------
bg = m.faixa("bangu", "bangu", pan=0.1)
for k in range(8):
    bg.nota(None, 4 + k * 0.5, 0.5, 0.6 if k % 2 else 0.85)
m.faixa("xiaoluo", "xiaoluo", pan=0.4).nota(None, 8, 1, 0.8)
m.faixa("daluo", "daluo", pan=-0.4).nota(None, 12, 2, 0.9)

# --- master ----------------------------------------------------------------------------------------
m.efeito_master("compressor", limiar_db=-20, razao=2.0)
m.loudness_alvo = -14
m.exportar(SAIDA / "08_controles.wav")
m.exportar_stems(SAIDA / "08_stems")
