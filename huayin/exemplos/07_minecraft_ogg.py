"""07 — sons para o addon (Dooms Day): .ogg mono, curtos, normalizados.

O Minecraft Bedrock lê Vorbis direto. Mono = som posicional (3D); estéreo = som de tela (2D).
Depois é só copiar para RP/sounds/... e registrar em sound_definitions.json (no addon, isso é feito
pelos geradores em tools/, nunca à mão).
"""
from _caminho import SAIDA

import huayin as hy

sons = {
    "sgx_zhong_grave": ("bianzhong", "D2", "tronco", 4.0),   # sino grave para o horizonte de eventos
    "sgx_qing_templo": ("qing", None, None, 6.0),            # tigela: ressonância longuíssima
    "sgx_luo_queda": ("daluo", None, None, 3.0),             # gongo que cai de altura (o puxão)
    "sgx_pipa_rasgo": ("pipa_tang", "D3", "huaxian", 2.5),   # seda rasgando (a espaguetificação?)
}
for nome, (inst, alt, tec, dur) in sons.items():
    m = hy.Musica(nome, tempo=60, sr=48000, reverb="caverna", nivel_reverb=0.6)
    m.faixa("f", inst).nota(alt, 0, dur, 0.9, tec)
    m.loudness_alvo = -18
    m.exportar(SAIDA / f"{nome}.ogg", mono=True)
