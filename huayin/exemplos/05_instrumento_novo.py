"""05 — criando um instrumento novo: o 五弦琵琶 (pipa de 5 cordas e pescoço reto da corte Tang).

O único exemplar antigo que sobreviveu está no Shōsōin (Nara, Japão), doado no séc. VIII.
Este arquivo é o exemplo completo do tutorial (docs/TUTORIAL.md §5).
"""
from _caminho import SAIDA

import huayin as hy
from huayin.fisica.corpo import CORPOS, Corpo
from huayin.instrumentos.pipa import PipaTang

# 1) um corpo novo (opcional): caixa um pouco menor que a do pipa Tang de 4 cordas
CORPOS["wuxian"] = Corpo("wuxian", [
    (170, 0.11, 0.7), (290, 0.08, 1.0), (440, 0.07, 0.85), (650, 0.055, 0.7),
    (950, 0.045, 0.6), (1400, 0.035, 0.45), (2100, 0.025, 0.35)], direto=0.3, passa_alta=50)


# 2) o instrumento: herda tudo do pipa Tang (palheta, seda, 4 trastes, técnicas) e muda o resto
@hy.registrar
class Wuxian(PipaTang):
    id = "wuxian_pipa"
    nome = "Pipa de cinco cordas (Tang)"
    nome_cn = "五弦琵琶"
    pinyin = "wǔxián pípa"
    descricao = "Pipa de pescoço reto e 5 cordas, de origem indiana, tocado com palheta na corte Tang."
    extensao = ("C2", "C4")
    AFINACOES = {"padrao": ["C2", "G2", "C3", "D3", "G3"]}   # reconstrução livre
    AFINACAO_PADRAO = "padrao"
    CORPO_PADRAO = "wuxian"
    PARAMETROS = {"largura": (0.18, "abertura estéreo")}

    # 3) uma técnica nova: 'chuva' — o trêmulo rufando na corda mais grave
    @hy.tecnica("chuva", "急雨", descricao="trêmulo de palheta forte na corda grave (大弦嘈嘈如急雨)",
                params={"velocidade": "golpes/s (padrão 13)"})
    def _t_chuva(self, golpes, nota, rng, velocidade=13.0):
        for g in golpes:
            g.corda = 0
            g.f0 = self.f_cordas[0]
        return self._t_yaobo(golpes, nota, rng, velocidade)


# 4) usar como qualquer outro instrumento
m = hy.Musica("Cinco cordas", tempo=72, tom="1=C", reverb="palacio_tang")
w = m.faixa("wuxian", "wuxian_pipa")
w.nota("C2", 0, 3, 0.85, "chuva")
w.jianpu("5 6 1' 2' | 3' 2' 1' 6 | 5 - - - |", 3, oitava=2)
w.nota("C3", 15, 3, 1.0, "huaxian")
print(hy.ajuda("wuxian_pipa")[:400], "...")
m.exportar(SAIDA / "05_instrumento_novo.wav")
