"""04 — orquestra lida de um arquivo 简谱 (.jp): 茉莉花 (Jasmim), canção tradicional."""
from pathlib import Path

from _caminho import SAIDA

import huayin as hy

m = hy.Musica.carregar(Path(__file__).parent / "partituras" / "molihua.jp")
m.exportar(SAIDA / "04_molihua.wav")
m.exportar_midi(SAIDA / "04_molihua.mid")       # para abrir num editor de partitura/DAW
m.salvar(SAIDA / "04_molihua.json")             # formato completo do motor (editável)
