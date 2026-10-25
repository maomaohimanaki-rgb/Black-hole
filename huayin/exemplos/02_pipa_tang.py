"""02 — o pipa da dinastia Tang tocando os versos do 琵琶行 (白居易, 816).

「大弦嘈嘈如急雨」 a corda grave rufa como chuva repentina   → trêmulo de palheta (摇拨) na corda grave
「小弦切切如私语」 a aguda sussurra                        → notas leves na corda aguda
「轻拢慢捻抹复挑」 leve 拢, lento 捻, 抹 e de novo 挑        → as técnicas long/nian/mo/tiao
「四弦一声如裂帛」 quatro cordas, um som de seda rasgando     → huaxian (当心画)
"""
from _caminho import SAIDA

import huayin as hy

# o gagaku japonês (herdeiro da música da corte Tang) afina em lá = 430 Hz
m = hy.Musica("琵琶行", tempo=66, tom="1=D", la4=430, reverb="palacio_tang")
p = m.faixa("pipa Tang", "pipa_tang", afinacao="yiyue")

p.nota("D2", 0, 3, 0.85, "yaobo:velocidade=11")                  # 大弦嘈嘈如急雨
p.jianpu("!p 6/ 5/ 6/ 1'/ 6 - | 5/ 3/ 5/ 6/ 5 - |", 3, oitava=3)    # 小弦切切如私语
p.nota("A2", 11, 1.5, 0.6, "long")                                # 轻拢
p.nota("B2", 12.5, 2, 0.6, "nian")                                # 慢捻
p.nota("D3", 14.5, 0.5, 0.75, "mo")                               # 抹
p.nota("E3", 15, 0.5, 0.55, "tiao")                               # 复挑
p.nota("D3", 15.5, 1.5, 0.75, "mo")
p.nota("D3", 18, 4, 1.0, "huaxian")                               # 四弦一声如裂帛

m.exportar(SAIDA / "02_pipa_tang.wav")
