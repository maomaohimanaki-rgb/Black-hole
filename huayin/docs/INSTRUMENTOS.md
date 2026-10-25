# Referência de instrumentos (gerado por `python -m huayin doc`)

Não edite à mão: rode `python -m huayin doc -o docs/INSTRUMENTOS.md` depois de mudar um instrumento.

# cordas dedilhadas 弹拨

## Pipa 琵琶 (pípa) — `pipa`

Alaúde em forma de pera com 4 cordas, 6 相 e 24–25 品 (trastes altos: a corda não toca o braço, então apertar mais forte sobe a nota). Tocado com unhas postiças 义甲 nos cinco dedos. Som brilhante, ataque seco, trêmulo 轮指 contínuo.

*Chegou da Ásia Central pela Rota da Seda; a forma moderna (vertical, dedos) firmou-se nas dinastias Ming e Qing. Peças: 十面埋伏 (Emboscada de todos os lados), 春江花月夜.*

- Família: cordas dedilhadas 弹拨
- Extensão: A2–D6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'aco_nylon'` | aço com náilon (moderno); 'seda' para o som antigo |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.11` | ponto de dedilhado |
| `dureza` | `0.85` | unhas postiças 义甲 (duras) |
| `largura` | `0.15` | abertura estéreo |
| `simpatia` | `0.06` | ressonância simpática das cordas soltas (0–0.3) |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.2` | abafamento |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.66` | comprimento vibrante (m) |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `tiao` | 挑 polegar | — | polegar para dentro: um pouco mais escuro e suave que o 弹 |
| `lun` | 轮指 lunzhi 轮 | `velocidade` (golpes por segundo (padrão 16)), `tipo` (longo (5 dedos) | meio (3) | curto (2)) | trêmulo dos cinco dedos (小→无→中→食 para fora, 大 para dentro) |
| `yaozhi` | 摇指 gun 滚 | `velocidade` (golpes por segundo (padrão 18)) | um dedo indo e voltando muito rápido (弹挑 contínuo) |
| `sao` | 扫 | `intervalo` (s entre cordas (padrão 0.012)), `cordas` (ex.: '0 1 2 3'), `acorde` (semitons extras, ex.: '7 12') | indicador varre as 4 cordas para fora (acorde batido) |
| `fu` | 拂 | `intervalo` (s), `cordas` (lista), `acorde` (semitons) | varre as cordas para dentro (do agudo ao grave) |
| `saofu` | 扫拂 | `velocidade` (batidas por segundo (padrão 10)), `acorde` (semitons) | 扫 e 拂 alternados em sequência rápida (rufar de acordes) |
| `fen` | 分 | `intervalo` (semitons da segunda nota (padrão: corda vizinha solta)) | indicador e polegar ao mesmo tempo em duas cordas vizinhas |
| `jiaoxian` | 绞弦 | `forca` (0–1) | cruza as duas cordas graves e bate: chiado de caixa (tambores do 十面埋伏) |
| `shayin` | 煞音 | — | belisca a corda junto ao traste: nota surda e percussiva |
| `pai` | 拍 | — | bate a mão no tampo (percussão, sem nota) |
| `ti` | 提 | — | puxa a corda para cima e solta: estalo contra os trastes |

## Pipa da dinastia Tang 曲项琵琶 (qūxiàng pípa) — `pipa_tang`

Reconstrução do pipa de pescoço curvo da corte Tang: 4 cordas de SEDA, só 4 trastes (相) — solto, +2, +3, +4 e +5 semitons por corda —, tocado na horizontal com uma PALHETA de madeira grande (拨子) que bate no protetor de couro (捍拨) a cada golpe para baixo. Golpe para baixo forte, para cima fraco (como no gakubiwa japonês, descendente direto).

*白居易, 琵琶行 (816): 「大弦嘈嘈如急雨，小弦切切如私语」 — a corda grave rufa como chuva repentina, a aguda sussurra; 「轻拢慢捻抹复挑」 — leve 拢, lento 捻, 抹 e de novo 挑; 「曲终收拨当心画，四弦一声如裂帛」 — no fim, a palheta risca o centro: quatro cordas, um som de seda rasgando. O 五弦琵琶 de Shōsōin (Nara) e as partituras de Dunhuang (P.3808, 933 d.C.) são as fontes materiais.*

- Família: cordas dedilhadas 弹拨
- Extensão: D2–B3
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'seda_fina'` | seda (o som antigo); 'aco_nylon' para comparar |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.16` | a palheta bate mais longe da ponte |
| `dureza` | `1.0` | palheta de madeira |
| `largura` | `0.12` | abertura estéreo |
| `simpatia` | `0.08` | ressonância simpática |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.25` | abafamento |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.12` | a palheta raspa a seda |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.75` | comprimento vibrante (m) |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |
| `batida` | `0.35` | quanto a palheta bate no protetor de couro 捍拨 nos golpes para baixo |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `mo` | 抹 baixo 下拨 kakubachi | — | palheta para baixo: o golpe forte (抹) |
| `tiao` | 挑 cima 上拨 kaeshibachi | — | palheta para cima: fraco, sem batida no couro |
| `long` | 拢 | `cents` (padrão 45) | (interpretação) mão esquerda empurra a corda de leve: sobe ~1/4 de tom e volta |
| `nian` | 捻 | `taxa` (Hz (padrão 3.5)), `prof` (cents (padrão 40)) | (interpretação) mão esquerda esfrega a corda: vibrato lento e largo |
| `sao` | 扫 扫拨 | `intervalo` (s entre cordas (padrão 0.009)), `acorde` (semitons extras) | palheta varre as 4 cordas para baixo, batendo no couro |
| `fu` | 拂 回拨 | `intervalo` (s), `acorde` (semitons) | palheta volta para cima pelas 4 cordas (mais fraco) |
| `huaxian` | 当心画 划弦 裂帛 | — | o golpe final do 琵琶行: a palheta risca as 4 cordas no centro com toda a força — 'seda rasgando' |
| `yaobo` | 摇拨 lun 轮 | `velocidade` (golpes por segundo (padrão 12)) | trêmulo de palheta (para baixo/para cima alternados) |
| `cuo` | 撮 | — | duas cordas de uma vez (a da nota e a vizinha grave) |

## Guqin 古琴 (gǔqín) — `guqin`

Cítara de 7 cordas de seda sobre uma caixa longa de paulównia, sem trastes nem pontes móveis. Três sons: 散音 (corda solta, 'terra'), 按音 (apertada, 'homem') e 泛音 (harmônico nos 徽, 'céu'). A arte está na mão esquerda: deslizes 上/下, vibratos 吟/猱 e o ruído do dedo na seda, tudo sobre o som que já está morrendo.

*Instrumento dos letrados há ~3000 anos (Confúcio, 嵇康). Patrimônio da UNESCO (2003). 流水 (Água corrente) foi ao espaço no disco de ouro da Voyager (1977).*

- Família: cordas dedilhadas 弹拨
- Extensão: C2–D6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'seda'` | seda (tradicional) | aco_nylon (cordas modernas de metal-náilon) |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.09` | a mão direita toca perto do 岳山 |
| `dureza` | `0.35` | polpa do dedo + um pouco de unha |
| `largura` | `0.3` | abertura estéreo |
| `simpatia` | `0.07` | ressonância simpática |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.35` | abafamento |
| `abafar` | `'soar'` | no guqin as notas soam até a corda ser tocada de novo |
| `modulacao_tensao` | `9.0` | a seda frouxa sobe bastante no ataque forte |
| `ruido_ataque` | `0.025` | ruído do contato |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `1.12` | comprimento vibrante (m) |
| `portamento` | `0.18` | duração padrão de 上/下 (s) |
| `ganho` | `1.0` | ganho de saída |
| `amortecimento_apertada` | `0.55` | o dedo da mão esquerda absorve energia: notas 按 duram menos |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛 泛音 harmonico | `hui` (徽 (1–13); sem hui escolhe pela altura), `n` (harmônico direto) | 泛音 no 徽: dedo encostado de leve na corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `gou` | 勾 | — | dedo médio para dentro (polpa): o toque mais comum, redondo |
| `mo` | 抹 | — | indicador para dentro (polpa) |
| `tiao` | 挑 | — | indicador para fora (unha): mais claro |
| `ti` | 剔 | — | médio para fora (unha) |
| `da` | 打 | — | anelar para dentro: mais fraco |
| `zhai` | 摘 | — | anelar para fora |
| `bo` | 擘 | — | polegar para fora: forte e cheio, usado nas cordas graves |
| `tuo` | 托 | — | polegar para dentro |
| `cuo` | 撮 | `intervalo` (semitons abaixo da nota (padrão 12)) | duas cordas juntas (oitava por padrão) |
| `lun` | 轮 | `velocidade` (golpes por segundo (padrão 12)) | anelar, médio e indicador para fora em sequência rápida: 3 notas iguais |
| `suo` | 锁 | `velocidade` (golpes por segundo (padrão 9)) | 'tranca': três notas repetidas (抹挑抹) em ritmo rápido-lento |
| `gunfu` | 滚拂 gun 滚 fu 拂 | `direcao` (desce | sobe | desce_sobe), `velocidade` (cordas por segundo (padrão 22)) | glissando pelas 7 cordas (滚 do agudo ao grave, 拂 do grave ao agudo, ou os dois) |
| `san` | 散 solta | — | força corda solta (散音): escolhe a corda com essa altura |
| `yin` | 吟 | `prof` (cents (padrão 18)), `taxa` (Hz (padrão 5)), `tipo` (细 | 长 | 定) | vibrato pequeno e rápido em volta da nota (细吟 / 长吟) |
| `nao` | 猱 | `prof` (cents (padrão 60)), `taxa` (Hz (padrão 3.2)) | vibrato largo e mais lento, que vai fechando (o dedo rola sobre a corda) |
| `jinfu` | 进复 | `cents` (padrão 200), `tempo` (s) | desliza um passo acima e volta |
| `tuifu` | 退复 | `cents` (padrão 200), `tempo` (s) | desliza um passo abaixo e volta |
| `wanglai` | 往来 | `cents` (padrão 200), `vezes` (padrão 2), `tempo` (s por ida) | vai e volta entre a nota e a de cima várias vezes (balanço) |
| `zhuang` | 撞 | `cents` (padrão 200) | toque rápido para cima e volta (um 'soluço' na nota) |
| `qiaqi` | 掐起 | — | a mão esquerda belisca a corda ao sair: soa a corda solta sem a direita |
| `yan` | 罨 | — | o polegar esquerdo bate na corda (hammer-on sem nota anterior): som surdo |

## Guzheng 古筝 (gǔzhēng) — `guzheng`

Cítara de 21 cordas sobre pontes móveis (雁柱, 'pés de ganso'), afinada em pentatônica. A mão direita dedilha com unhas postiças à direita das pontes; a esquerda APERTA a corda à esquerda da ponte para fazer as notas que faltam (按音), vibratos 揉 e deslizes.

*Mais de 2000 anos (dinastia Qin). Ancestral do koto japonês, do gayageum coreano e do đàn tranh vietnamita. Peças: 高山流水, 渔舟唱晚 (Barco de pesca cantando ao entardecer).*

- Família: cordas dedilhadas 弹拨
- Extensão: D2–D6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `'D'` | tom da pentatônica (D, C, G, F, A, Bb, E) ou lista de 21 notas |
| `material` | `'aco_nylon'` | aço com náilon (moderno) | seda (zheng antigo) |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.13` | ponto de dedilhado |
| `dureza` | `0.9` | unhas postiças 义甲 |
| `largura` | `0.65` | abertura estéreo (graves à esquerda, agudos à direita) |
| `simpatia` | `0.12` | o zheng 'canta' por simpatia |
| `t60_escala` | `1.1` | sustentação |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'soar'` | as cordas soam até serem tocadas de novo |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `1.0` | comprimento vibrante médio (m) |
| `portamento` | `0.14` | duração padrão dos deslizes (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `guazou` | 刮奏 glissando gua | `ate` (nota final (ex.: 'D5')), `tempo` (duração do glissando (s)), `direcao` (sobe | desce (quando 'ate' não é dado)), `cordas` (nº de cordas (padrão 8)) | glissando pelas cordas (só as notas da escala) |
| `huazhi` | 花指 | `cordas` (quantas cordas antes (padrão 5)), `tempo` (s (padrão 0.15)), `de` (cima | baixo) | glissando curto e rápido que desemboca na nota (ornamento típico do zheng) |
| `cuo` | 撮 oitava | `intervalo` (semitons abaixo (padrão 12)) | duas cordas ao mesmo tempo (oitava abaixo por padrão) |
| `tuo` | 托 | — | polegar para fora: o toque principal, cheio |
| `mo` | 抹 | — | indicador para dentro |
| `gou` | 勾 | — | médio para dentro: um pouco mais escuro |
| `yaozhi` | 摇指 yao | `velocidade` (golpes por segundo (padrão 15)) | trêmulo rápido do polegar (vai e volta) — o 'canto' contínuo do zheng |
| `saoyao` | 扫摇 | `velocidade` (padrão 12), `baixo` (semitons abaixo (padrão 12)) | baixo no polegar + trêmulo na melodia (alternado) |
| `rou` | 揉 vibrato | `prof` (cents (padrão 30, 大揉 ~60)), `taxa` (Hz (padrão 5.5)), `atraso` (s) | vibrato apertando a corda (só sobe: apertar não abaixa) |
| `chan` | 颤 | `prof` (cents (padrão 18)) | tremor rápido e estreito da mão esquerda |
| `shanghua` | 上滑音 huaan 滑按 | `tempo` (s (padrão 0.2)), `atraso` (s) | dedilha a corda solta e aperta até a nota (sobe) |
| `xiahua` | 下滑音 回滑 | `cents` (padrão 200), `tempo` (s) | dedilha já apertada (um tom acima) e solta até a nota (desce) |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe apertando e volta (ornamento cantado) |
| `dianan` | 点按 | — | aperta e solta rapidinho logo depois do ataque |

## Konghou (harpa Tang) 箜篌 (kōnghóu) — `konghou`

Harpa angular vertical (竖箜篌) da corte Tang, de origem persa/assíria: cordas de seda numa moldura em L, sem pontes nem pedais. Reconstrução: 23 cordas diatônicas, sem bend.

*Desapareceu depois da dinastia Ming; conhecido por pinturas de Dunhuang, pelo exemplar de Shōsōin e pelo poema 李凭箜篌引 de 李贺. O 雁柱箜篌 moderno (com pontes) é uma recriação do séc. XX.*

- Família: cordas dedilhadas 弹拨
- Extensão: C3–G6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `'D'` | tom da escala diatônica das cordas |
| `material` | `'seda_fina'` | seda |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.3` | harpas são tocadas perto do meio da corda: som redondo |
| `dureza` | `0.4` | polpa dos dedos (harpa) |
| `largura` | `0.45` | abertura estéreo |
| `simpatia` | `0.1` | ressonância simpática |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'soar'` | as cordas soam livres |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.7` | comprimento vibrante da corda solta (m) — usado no ruído de deslize |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `guazou` | 刮奏 glissando gua | `ate` (nota final (ex.: 'D5')), `tempo` (duração do glissando (s)), `direcao` (sobe | desce (quando 'ate' não é dado)), `cordas` (nº de cordas (padrão 8)) | glissando pelas cordas (só as notas da escala) |
| `huazhi` | 花指 | `cordas` (quantas cordas antes (padrão 5)), `tempo` (s (padrão 0.15)), `de` (cima | baixo) | glissando curto e rápido que desemboca na nota (ornamento típico do zheng) |
| `cuo` | 撮 oitava | `intervalo` (semitons abaixo (padrão 12)) | duas cordas ao mesmo tempo (oitava abaixo por padrão) |
| `pai` | 拍 abafar_mao | — | a palma abafa as cordas (corte seco) |

## Se 瑟 (sè) — `se`

Cítara ritual de 25 cordas de seda com pontes, da música 雅乐 dos Zhou aos Han. Grave, escura, de sustentação longa; tocada com os dedos sem unhas.

*Um 瑟 de 2500 anos foi achado no túmulo do Marquês Yi de Zeng, junto com o 编钟.*

- Família: cordas dedilhadas 弹拨
- Extensão: A1–E5
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `'D'` | tom da pentatônica |
| `material` | `'seda'` | seda |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.16` | ponto |
| `dureza` | `0.3` | polpa |
| `largura` | `0.55` | estéreo |
| `simpatia` | `0.12` | simpatia |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'soar'` | soa livre |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `1.1` | m |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `guazou` | 刮奏 glissando gua | `ate` (nota final (ex.: 'D5')), `tempo` (duração do glissando (s)), `direcao` (sobe | desce (quando 'ate' não é dado)), `cordas` (nº de cordas (padrão 8)) | glissando pelas cordas (só as notas da escala) |
| `huazhi` | 花指 | `cordas` (quantas cordas antes (padrão 5)), `tempo` (s (padrão 0.15)), `de` (cima | baixo) | glissando curto e rápido que desemboca na nota (ornamento típico do zheng) |
| `cuo` | 撮 oitava | `intervalo` (semitons abaixo (padrão 12)) | duas cordas ao mesmo tempo (oitava abaixo por padrão) |

## Zhongruan 中阮 (zhōngruǎn) — `ruan`

Alaúde de caixa redonda com 4 cordas e 24 trastes, tocado com palheta. Som quente, de 'violão chinês', com graves redondos da caixa com duas bocas.

*Chamado 秦琵琶 na dinastia Han; o nome vem de 阮咸, um dos Sete Sábios do Bosque de Bambu. Um ruan de Tang está em Shōsōin.*

- Família: cordas dedilhadas 弹拨
- Extensão: G2–D5
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'aco_nylon'` | material |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.18` | ponto |
| `dureza` | `0.8` | palheta |
| `largura` | `0.15` | estéreo |
| `simpatia` | `0.06` | ressonância simpática das cordas soltas (0–0.3) |
| `t60_escala` | `1.1` | sustentação |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.6` | m |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `baixo` | 下拨 tan 弹 | — | palheta para baixo (forte) |
| `cima` | 上拨 tiao 挑 | — | palheta para cima (um pouco mais fraca) |
| `yaozhi` | 摇指 lun 轮 tremolo | `velocidade` (golpes por segundo (padrão 14)) | trêmulo de palheta (o 'sustain' dos alaúdes chineses) |
| `sao` | 扫 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para baixo |
| `fu` | 拂 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para cima |

## Liuqin 柳琴 (liǔqín) — `liuqin`

Pequeno alaúde em pera ('folha de salgueiro'), 4 cordas de aço, palheta: o soprano brilhante dos dedilhados.

*Nasceu no folclore de Shandong/Jiangsu como acompanhamento da ópera 柳琴戏.*

- Família: cordas dedilhadas 弹拨
- Extensão: G3–G6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'aco'` | cordas de aço |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.12` | ponto |
| `dureza` | `0.95` | palheta |
| `largura` | `0.1` | estéreo |
| `simpatia` | `0.06` | ressonância simpática das cordas soltas (0–0.3) |
| `t60_escala` | `1.0` | multiplica a sustentação (0.5 = corda abafada/velha) |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.38` | m |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `baixo` | 下拨 tan 弹 | — | palheta para baixo (forte) |
| `cima` | 上拨 tiao 挑 | — | palheta para cima (um pouco mais fraca) |
| `yaozhi` | 摇指 lun 轮 tremolo | `velocidade` (golpes por segundo (padrão 14)) | trêmulo de palheta (o 'sustain' dos alaúdes chineses) |
| `sao` | 扫 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para baixo |
| `fu` | 拂 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para cima |

## Yueqin 月琴 (yuèqín) — `yueqin`

'Viola da lua': caixa redonda chata, braço curtíssimo, 2 cursos de cordas duplas. Na ópera de Pequim acompanha o 京胡 com um som seco e metálico.

- Família: cordas dedilhadas 弹拨
- Extensão: A3–E6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'aco'` | aço |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.15` | ponto |
| `dureza` | `0.95` | palheta |
| `largura` | `0.1` | estéreo |
| `simpatia` | `0.06` | ressonância simpática das cordas soltas (0–0.3) |
| `t60_escala` | `0.6` | caixa chata: notas curtas |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.35` | m |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `baixo` | 下拨 tan 弹 | — | palheta para baixo (forte) |
| `cima` | 上拨 tiao 挑 | — | palheta para cima (um pouco mais fraca) |
| `yaozhi` | 摇指 lun 轮 tremolo | `velocidade` (golpes por segundo (padrão 14)) | trêmulo de palheta (o 'sustain' dos alaúdes chineses) |
| `sao` | 扫 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para baixo |
| `fu` | 拂 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para cima |

## Sanxian 三弦 (sānxián) — `sanxian`

Alaúde de 3 cordas sem trastes, braço longo e caixa pequena coberta de pele de cobra: ataque de banjo, médios nasais e deslizes livres. Ancestral do shamisen japonês.

*Popular desde a dinastia Yuan; acompanha 评弹 de Suzhou, 大鼓 do norte e a ópera.*

- Família: cordas dedilhadas 弹拨
- Extensão: G2–G5
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'tripa'` | seda/tripa grossa |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.08` | toca bem perto da ponte, sobre a pele |
| `dureza` | `0.9` | palheta/unha |
| `largura` | `0.1` | estéreo |
| `simpatia` | `0.06` | ressonância simpática das cordas soltas (0–0.3) |
| `t60_escala` | `0.75` | a pele absorve energia |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'nota'` | nota = abafa no fim da nota | soar = deixa soar até repetir a corda |
| `modulacao_tensao` | `6.0` | cents que um dedilhado forte sobe no ataque (física da tensão) |
| `ruido_ataque` | `0.04` | ruído do contato da unha/palheta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.95` | m |
| `portamento` | `0.1` | deslizes |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `baixo` | 下拨 tan 弹 | — | palheta para baixo (forte) |
| `cima` | 上拨 tiao 挑 | — | palheta para cima (um pouco mais fraca) |
| `yaozhi` | 摇指 lun 轮 tremolo | `velocidade` (golpes por segundo (padrão 14)) | trêmulo de palheta (o 'sustain' dos alaúdes chineses) |
| `sao` | 扫 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para baixo |
| `fu` | 拂 | `intervalo` (s), `acorde` (semitons) | varre todas as cordas para cima |
| `pele` | sawari chiado | `quanto` (0–1 (padrão 0.3)) | a corda encosta de leve e chia (zumbido de pele/ponte) |

## Yangqin 扬琴 (yángqín) — `yangqin`

Saltério trapezoidal de cordas de aço em cursos de 2 a 5 cordas por nota, percutido com duas baquetas finas de bambu com ponta de borracha. Sem abafadores: as notas soam juntas num halo metálico. O trêmulo 轮竹 é a voz característica.

*Veio da Pérsia (santur) pelo mar, no fim da dinastia Ming; o modelo 402 moderno é cromático com ~4,5 oitavas.*

- Família: cordas dedilhadas 弹拨
- Extensão: G2–A6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `''` | nome da afinação ou lista de notas das cordas (grave → agudo) |
| `material` | `'aco'` | aço |
| `corpo` | `''` | corpo ressonante (ver fisica/corpo.py); vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = corda crua, 1 = corpo completo |
| `posicao` | `0.12` | ponto de golpe |
| `dureza` | `0.7` | 0 = ponta de borracha macia, 1 = bambu nu |
| `largura` | `0.55` | estéreo (graves à esquerda) |
| `simpatia` | `0.1` | ressonância simpática |
| `t60_escala` | `0.8` | sustentação |
| `t60_soltura` | `0.15` | quanto a nota demora a morrer quando o dedo abafa (s) |
| `abafar` | `'soar'` | sem abafadores: as cordas soam livres |
| `modulacao_tensao` | `3.0` | subida no ataque |
| `ruido_ataque` | `0.08` | estalo da baqueta |
| `humanizar` | `0.5` | variação aleatória de ponto, força e afinação (0 = robô) |
| `comprimento` | `0.7` | comprimento vibrante da corda solta (m) — usado no ruído de deslize |
| `portamento` | `0.12` | duração padrão dos slides (s) |
| `ganho` | `1.0` | ganho de saída |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `tan` | 弹 dedilhar | — | dedilhado simples (padrão) |
| `hammer` | da 打 ligado | — | liga à nota anterior batendo o dedo (sem dedilhar) |
| `puxada` | dai 带 pull_off | — | liga à nota anterior puxando o dedo (sem dedilhar) |
| `deslizar` | hua 滑 shang 上 xia 下 slide | `tempo` (duração do deslize (s)) | desliza da nota anterior até esta sem novo ataque (上 sobe, 下 desce) |
| `abafado` | muted 闷 | `quanto` (0–1 (padrão 0.8)) | corda abafada pela mão: som curto e surdo |
| `fanyin` | 泛音 harmonico | `n` (número do harmônico (2 = oitava, 3 = 12ª...). Sem n: escolhe pela altura) | harmônico natural: dedo encostado no nó da corda |
| `vibrato` | yin 吟 rou 揉 | `taxa` (Hz (padrão 5.5)), `prof` (cents (padrão 25)), `atraso` (s antes de começar), `forma` (acima | simetrico | abaixo) | vibrato da mão esquerda |
| `bend` | tui 推 la 拉 | `cents` (quanto sobe (padrão 200)), `tempo` (duração da subida (s)), `atraso` (s antes) | empurra/puxa a corda depois do ataque e sobe a afinação |
| `bend_volta` | tuifu 推复 lafu 拉复 | `cents` (padrão 200), `tempo` (s de cada movimento), `atraso` (s) | sobe e volta (推复/拉复) |
| `pre_bend` | huiyin 回音 | `cents` (padrão 200), `tempo` (s) | começa já esticada e desce até a nota |
| `slide_in` | chuo 绰 | `cents` (de quanto abaixo (padrão 150)), `tempo` (s) | entra na nota deslizando de baixo (绰) |
| `slide_down_in` | zhu 注 | `cents` (de quanto acima (padrão 150)), `tempo` (s) | entra na nota deslizando de cima (注) |
| `glissando_saida` | xiahua 下滑 | `cents` (padrão 300), `tempo` (s) | no fim da nota desliza para baixo (cai) |
| `acento` | > 重音 | `quanto` (0–1) | ataque mais forte e brilhante |
| `posicao` | ponto | `valor` (fração 0.03–0.5) | muda o ponto do dedilhado (perto da ponte = metálico) |
| `soar` | let_ring 延音 | — | deixa a nota soar até a corda ser tocada de novo |
| `arpejo` | 琶音 | `notas` (intervalos em semitons separados por espaço, ex.: '0 7 12'), `intervalo` (s entre cordas) | acorde arpejado: toca a nota em várias cordas em sequência |
| `tremolo` | tremolo_simples | `velocidade` (golpes por segundo (padrão 14)) | repetição rápida e regular da nota |
| `dan` | 单竹 | — | golpe simples (padrão) |
| `lunzhu` | 轮竹 lun tremolo | `velocidade` (golpes por segundo (padrão 16)) | trêmulo alternando as duas baquetas |
| `chanzhu` | 颤竹 | `velocidade` (golpes/s (padrão 20)) | uma baqueta quicando: trêmulo que perde força |
| `qizhu` | 齐竹 oitava | `intervalo` (semitons abaixo (padrão 12)) | as duas baquetas juntas (oitava abaixo) |
| `huazhu` | 滑竹 glissando | `semitons` (padrão 12), `tempo` (s) | arrasta a baqueta pelas cordas |
| `tanlun` | 弹轮 pizzicato 拨弦 | — | dedilha a corda com a ponta da baqueta/dedo (pizzicato) |
| `zhiyin` | 止音 abafar | `depois` (s até abafar (padrão: duração da nota)) | a mão abafa o curso logo depois do golpe |

# cordas friccionadas 拉弦

## Erhu 二胡 (èrhú) — `erhu`

Violino de 2 cordas sem espelho: o dedo aperta a corda no ar, então a afinação é contínua e o deslize 滑音 é a alma do instrumento. A crina passa ENTRE as cordas; o ressonador hexagonal coberto de pele de píton dá o timbre nasal, quase vocal.

*Os 胡琴 vieram do norte (povos 'hu') na dinastia Tang/Song. 阿炳 (Abing) e 刘天华 tornaram o erhu solista: 二泉映月 (A lua refletida na segunda fonte), 赛马 (Corrida de cavalos).*

- Família: cordas friccionadas 拉弦
- Extensão: D4–A6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.07` | ataque do começo de frase (s) |
| `soltura` | `0.1` | soltura (s) |
| `portamento` | `0.09` | deslize das ligaduras (s) — o erhu não tem espelho: desliza muito |
| `brilho` | `0.5` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `22.0` | 揉弦 automático em notas longas (cents; 0 desliga) |
| `vibrato_taxa` | `6.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `afinacao` | `''` | notas das duas cordas (interna, externa); vazio = padrão |
| `forca` | `0.0` | pressão extra do arco (-0.3 a +0.3) |
| `ruido_crina` | `0.025` | grão da crina e do breu |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `yarou` | 压揉 | `prof` (cents (padrão 30)), `taxa` (Hz (padrão 6)) | vibrato de pressão: o dedo aperta e solta (afinação só sobe) |
| `gunrou` | 滚揉 | `prof` (cents (padrão 25)), `taxa` (Hz (padrão 6.5)) | vibrato rolando a ponta do dedo (em volta da nota) |
| `huarou` | 滑揉 | `prof` (cents (padrão 70)), `taxa` (Hz (padrão 4.5)) | vibrato deslizando o dedo: largo e expressivo |
| `sem_vibrato` | 直音 liso | — | nota lisa, sem vibrato automático |
| `pizz` | boxian 拨弦 pizzicato | — | dedilha a corda com o dedo |
| `jigong` | 击弓 col_legno | — | bate a vara do arco na corda (percussivo) |
| `fanyin` | 泛音 harmonico | — | harmônico: dedo encostado de leve, som de flauta |
| `dungong` | 顿弓 | — | arcada curta e acentuada que para o arco na corda |
| `tiaogong` | 跳弓 spiccato | — | o arco quica: nota curtíssima |
| `kuaigong` | 快弓 | — | arcadas rápidas destacadas (cada nota troca o arco) |
| `liangong` | 连弓 mesmo_arco | — | várias notas no mesmo arco (ligadas sem deslize) |
| `changong` | 颤弓 tremolo_arco | `velocidade` (trocas por segundo (padrão 14)) | trêmulo de arco (trocas rapidíssimas) |
| `paogong` | 抛弓 ricochete | `quiques` (padrão 6) | joga o arco: quiques que vão ficando mais rápidos e fracos |
| `mati` | 马嘶 relincho | — | relincho de cavalo (赛马): sobe deslizando, trina e despenca |
| `jinma` | 近码 perto_ponte | — | arco perto da ponte: som vítreo, cheio de harmônicos |
| `yuanma` | 远码 longe_ponte | — | arco longe da ponte: som doce e velado |
| `corda_interna` | 内弦 | — | toca na corda interna (mais grave e quente) |

## Gaohu 高胡 (gāohú) — `gaohu`

Erhu soprano da música cantonesa 广东音乐, tocado com o ressonador entre os joelhos: brilhante e doce.

- Família: cordas friccionadas 拉弦
- Extensão: G4–D7
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.07` | ataque do começo de frase (s) |
| `soltura` | `0.1` | soltura (s) |
| `portamento` | `0.09` | deslize das ligaduras (s) — o erhu não tem espelho: desliza muito |
| `brilho` | `0.5` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `22.0` | 揉弦 automático em notas longas (cents; 0 desliga) |
| `vibrato_taxa` | `6.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `afinacao` | `''` | notas das duas cordas (interna, externa); vazio = padrão |
| `forca` | `0.0` | pressão extra do arco (-0.3 a +0.3) |
| `ruido_crina` | `0.025` | grão da crina e do breu |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `yarou` | 压揉 | `prof` (cents (padrão 30)), `taxa` (Hz (padrão 6)) | vibrato de pressão: o dedo aperta e solta (afinação só sobe) |
| `gunrou` | 滚揉 | `prof` (cents (padrão 25)), `taxa` (Hz (padrão 6.5)) | vibrato rolando a ponta do dedo (em volta da nota) |
| `huarou` | 滑揉 | `prof` (cents (padrão 70)), `taxa` (Hz (padrão 4.5)) | vibrato deslizando o dedo: largo e expressivo |
| `sem_vibrato` | 直音 liso | — | nota lisa, sem vibrato automático |
| `pizz` | boxian 拨弦 pizzicato | — | dedilha a corda com o dedo |
| `jigong` | 击弓 col_legno | — | bate a vara do arco na corda (percussivo) |
| `fanyin` | 泛音 harmonico | — | harmônico: dedo encostado de leve, som de flauta |
| `dungong` | 顿弓 | — | arcada curta e acentuada que para o arco na corda |
| `tiaogong` | 跳弓 spiccato | — | o arco quica: nota curtíssima |
| `kuaigong` | 快弓 | — | arcadas rápidas destacadas (cada nota troca o arco) |
| `liangong` | 连弓 mesmo_arco | — | várias notas no mesmo arco (ligadas sem deslize) |
| `changong` | 颤弓 tremolo_arco | `velocidade` (trocas por segundo (padrão 14)) | trêmulo de arco (trocas rapidíssimas) |
| `paogong` | 抛弓 ricochete | `quiques` (padrão 6) | joga o arco: quiques que vão ficando mais rápidos e fracos |
| `mati` | 马嘶 relincho | — | relincho de cavalo (赛马): sobe deslizando, trina e despenca |
| `jinma` | 近码 perto_ponte | — | arco perto da ponte: som vítreo, cheio de harmônicos |
| `yuanma` | 远码 longe_ponte | — | arco longe da ponte: som doce e velado |
| `corda_interna` | 内弦 | — | toca na corda interna (mais grave e quente) |

## Zhonghu 中胡 (zhōnghú) — `zhonghu`

Erhu contralto (uma quinta abaixo): o 'viola' da orquestra chinesa.

- Família: cordas friccionadas 拉弦
- Extensão: G3–D6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.07` | ataque do começo de frase (s) |
| `soltura` | `0.1` | soltura (s) |
| `portamento` | `0.09` | deslize das ligaduras (s) — o erhu não tem espelho: desliza muito |
| `brilho` | `0.5` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `22.0` | 揉弦 automático em notas longas (cents; 0 desliga) |
| `vibrato_taxa` | `6.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `afinacao` | `''` | notas das duas cordas (interna, externa); vazio = padrão |
| `forca` | `0.0` | pressão extra do arco (-0.3 a +0.3) |
| `ruido_crina` | `0.025` | grão da crina e do breu |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `yarou` | 压揉 | `prof` (cents (padrão 30)), `taxa` (Hz (padrão 6)) | vibrato de pressão: o dedo aperta e solta (afinação só sobe) |
| `gunrou` | 滚揉 | `prof` (cents (padrão 25)), `taxa` (Hz (padrão 6.5)) | vibrato rolando a ponta do dedo (em volta da nota) |
| `huarou` | 滑揉 | `prof` (cents (padrão 70)), `taxa` (Hz (padrão 4.5)) | vibrato deslizando o dedo: largo e expressivo |
| `sem_vibrato` | 直音 liso | — | nota lisa, sem vibrato automático |
| `pizz` | boxian 拨弦 pizzicato | — | dedilha a corda com o dedo |
| `jigong` | 击弓 col_legno | — | bate a vara do arco na corda (percussivo) |
| `fanyin` | 泛音 harmonico | — | harmônico: dedo encostado de leve, som de flauta |
| `dungong` | 顿弓 | — | arcada curta e acentuada que para o arco na corda |
| `tiaogong` | 跳弓 spiccato | — | o arco quica: nota curtíssima |
| `kuaigong` | 快弓 | — | arcadas rápidas destacadas (cada nota troca o arco) |
| `liangong` | 连弓 mesmo_arco | — | várias notas no mesmo arco (ligadas sem deslize) |
| `changong` | 颤弓 tremolo_arco | `velocidade` (trocas por segundo (padrão 14)) | trêmulo de arco (trocas rapidíssimas) |
| `paogong` | 抛弓 ricochete | `quiques` (padrão 6) | joga o arco: quiques que vão ficando mais rápidos e fracos |
| `mati` | 马嘶 relincho | — | relincho de cavalo (赛马): sobe deslizando, trina e despenca |
| `jinma` | 近码 perto_ponte | — | arco perto da ponte: som vítreo, cheio de harmônicos |
| `yuanma` | 远码 longe_ponte | — | arco longe da ponte: som doce e velado |
| `corda_interna` | 内弦 | — | toca na corda interna (mais grave e quente) |

## Banhu 板胡 (bǎnhú) — `banhu`

Fiddle com casca de coco e TAMPO DE MADEIRA fino em vez de pele: agudo, estridente e alegre, das óperas 秦腔 e 梆子 do norte.

- Família: cordas friccionadas 拉弦
- Extensão: D4–D7
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.07` | ataque do começo de frase (s) |
| `soltura` | `0.1` | soltura (s) |
| `portamento` | `0.09` | deslize das ligaduras (s) — o erhu não tem espelho: desliza muito |
| `brilho` | `0.7` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `28.0` | vibrato |
| `vibrato_taxa` | `6.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `afinacao` | `''` | notas das duas cordas (interna, externa); vazio = padrão |
| `forca` | `0.0` | pressão extra do arco (-0.3 a +0.3) |
| `ruido_crina` | `0.035` | crina |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `yarou` | 压揉 | `prof` (cents (padrão 30)), `taxa` (Hz (padrão 6)) | vibrato de pressão: o dedo aperta e solta (afinação só sobe) |
| `gunrou` | 滚揉 | `prof` (cents (padrão 25)), `taxa` (Hz (padrão 6.5)) | vibrato rolando a ponta do dedo (em volta da nota) |
| `huarou` | 滑揉 | `prof` (cents (padrão 70)), `taxa` (Hz (padrão 4.5)) | vibrato deslizando o dedo: largo e expressivo |
| `sem_vibrato` | 直音 liso | — | nota lisa, sem vibrato automático |
| `pizz` | boxian 拨弦 pizzicato | — | dedilha a corda com o dedo |
| `jigong` | 击弓 col_legno | — | bate a vara do arco na corda (percussivo) |
| `fanyin` | 泛音 harmonico | — | harmônico: dedo encostado de leve, som de flauta |
| `dungong` | 顿弓 | — | arcada curta e acentuada que para o arco na corda |
| `tiaogong` | 跳弓 spiccato | — | o arco quica: nota curtíssima |
| `kuaigong` | 快弓 | — | arcadas rápidas destacadas (cada nota troca o arco) |
| `liangong` | 连弓 mesmo_arco | — | várias notas no mesmo arco (ligadas sem deslize) |
| `changong` | 颤弓 tremolo_arco | `velocidade` (trocas por segundo (padrão 14)) | trêmulo de arco (trocas rapidíssimas) |
| `paogong` | 抛弓 ricochete | `quiques` (padrão 6) | joga o arco: quiques que vão ficando mais rápidos e fracos |
| `mati` | 马嘶 relincho | — | relincho de cavalo (赛马): sobe deslizando, trina e despenca |
| `jinma` | 近码 perto_ponte | — | arco perto da ponte: som vítreo, cheio de harmônicos |
| `yuanma` | 远码 longe_ponte | — | arco longe da ponte: som doce e velado |
| `corda_interna` | 内弦 | — | toca na corda interna (mais grave e quente) |

## Jinghu 京胡 (jīnghú) — `jinghu`

O fiddle da ópera de Pequim: corpo de bambu com pele de cobra, cordas de seda, muito agudo e penetrante. Conduz a melodia junto com a voz.

- Família: cordas friccionadas 拉弦
- Extensão: A4–A6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.07` | ataque do começo de frase (s) |
| `soltura` | `0.1` | soltura (s) |
| `portamento` | `0.05` | deslizes curtos e rápidos |
| `brilho` | `0.85` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `15.0` | vibrato quase reto |
| `vibrato_taxa` | `6.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `afinacao` | `''` | notas das duas cordas (interna, externa); vazio = padrão |
| `forca` | `0.0` | pressão extra do arco (-0.3 a +0.3) |
| `ruido_crina` | `0.04` | crina |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `yarou` | 压揉 | `prof` (cents (padrão 30)), `taxa` (Hz (padrão 6)) | vibrato de pressão: o dedo aperta e solta (afinação só sobe) |
| `gunrou` | 滚揉 | `prof` (cents (padrão 25)), `taxa` (Hz (padrão 6.5)) | vibrato rolando a ponta do dedo (em volta da nota) |
| `huarou` | 滑揉 | `prof` (cents (padrão 70)), `taxa` (Hz (padrão 4.5)) | vibrato deslizando o dedo: largo e expressivo |
| `sem_vibrato` | 直音 liso | — | nota lisa, sem vibrato automático |
| `pizz` | boxian 拨弦 pizzicato | — | dedilha a corda com o dedo |
| `jigong` | 击弓 col_legno | — | bate a vara do arco na corda (percussivo) |
| `fanyin` | 泛音 harmonico | — | harmônico: dedo encostado de leve, som de flauta |
| `dungong` | 顿弓 | — | arcada curta e acentuada que para o arco na corda |
| `tiaogong` | 跳弓 spiccato | — | o arco quica: nota curtíssima |
| `kuaigong` | 快弓 | — | arcadas rápidas destacadas (cada nota troca o arco) |
| `liangong` | 连弓 mesmo_arco | — | várias notas no mesmo arco (ligadas sem deslize) |
| `changong` | 颤弓 tremolo_arco | `velocidade` (trocas por segundo (padrão 14)) | trêmulo de arco (trocas rapidíssimas) |
| `paogong` | 抛弓 ricochete | `quiques` (padrão 6) | joga o arco: quiques que vão ficando mais rápidos e fracos |
| `mati` | 马嘶 relincho | — | relincho de cavalo (赛马): sobe deslizando, trina e despenca |
| `jinma` | 近码 perto_ponte | — | arco perto da ponte: som vítreo, cheio de harmônicos |
| `yuanma` | 远码 longe_ponte | — | arco longe da ponte: som doce e velado |
| `corda_interna` | 内弦 | — | toca na corda interna (mais grave e quente) |

# sopros 吹管

## Dizi (qudi) 笛子 (dízi) — `dizi`

Flauta transversal de bambu com 6 furos e um furo extra coberto por uma membrana fina de junco (笛膜). A membrana vibra e dá o zumbido brilhante que é a assinatura do dizi. 曲笛 (qudi, do sul, doce, ópera Kunqu) é o padrão; use 'bangdi' para o agudo do norte.

*Flautas de osso de 9000 anos foram achadas em Jiahu (贾湖骨笛). O dizi com membrana aparece na dinastia Tang/Song. Peças: 鹧鸪飞, 姑苏行, 喜相逢.*

- Família: sopros 吹管
- Extensão: A4–E7
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.04` | ataque (s) |
| `soltura` | `0.09` | soltura (s) |
| `portamento` | `0.06` | deslize (s) — 滑音 cobrindo o furo aos poucos |
| `brilho` | `0.55` | cor |
| `ruido` | `1.0` | sopro |
| `vibrato` | `0.0` | vibrato automático (cents) |
| `vibrato_taxa` | `5.5` | Hz do vibrato automático |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `membrana` | `0.35` | 笛膜: quanto a membrana zumbe (0 = sem membrana) |
| `f_membrana` | `3200.0` | ressonância da membrana (Hz): tensão/rugas do 笛膜 |
| `razao_jato` | `0.32` | atraso do jato/tubo (avançado) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `tuyin` | 吐音 lingua | `tipo` (单 | 双 | 三), `velocidade` (golpes/s (padrão 8 / 12 / 12)) | golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo) |
| `huashe` | 花舌 flatterzunge frullato | `taxa` (Hz (padrão 26)), `prof` (0–1 (padrão 0.6)) | língua vibrando (rrrr): som rouco e agitado |
| `qizhenyin` | 气震音 vibrato_ar | `taxa` (Hz (padrão 5)), `prof` (0–1 (padrão 0.35)) | vibrato de sopro: o volume pulsa (e a afinação um pouco) |
| `zengyin` | 赠音 | `intervalo` (semitons (padrão 3)) | notinha rápida para cima no fim da nota (o 'suspiro' do dizi) |
| `liyin` | 历音 corrida | `notas` (quantas antes (padrão 5)), `tempo` (s (padrão 0.18)), `de` (baixo | cima) | corrida rápida de notas da escala que chega na nota |
| `fanyin` | 泛音 harmonico | — | harmônico soprado: mais puro e mais soproso |
| `forte_sopro` | 强吹 | — | sopro forçado: mais brilho e ruído |

## Xiao 箫 (xiāo) — `xiao`

Flauta vertical de bambu soprada pela ponta (como a shakuhachi, que descende dela): grave, velada, muito ar no som. Sem membrana. Parceira clássica do guqin (琴箫合奏).

- Família: sopros 吹管
- Extensão: D4–D6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.09` | ataque macio |
| `soltura` | `0.16` | soltura |
| `portamento` | `0.1` | deslize |
| `brilho` | `0.28` | escuro |
| `ruido` | `1.9` | muito ar |
| `vibrato` | `0.0` | vibrato automático (cents) |
| `vibrato_taxa` | `5.5` | Hz do vibrato automático |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |
| `membrana` | `0.0` | o xiao não tem membrana |
| `f_membrana` | `3200.0` | ressonância da membrana (Hz): tensão/rugas do 笛膜 |
| `razao_jato` | `0.32` | atraso do jato/tubo (avançado) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `tuyin` | 吐音 lingua | `tipo` (单 | 双 | 三), `velocidade` (golpes/s (padrão 8 / 12 / 12)) | golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo) |
| `huashe` | 花舌 flatterzunge frullato | `taxa` (Hz (padrão 26)), `prof` (0–1 (padrão 0.6)) | língua vibrando (rrrr): som rouco e agitado |
| `qizhenyin` | 气震音 vibrato_ar | `taxa` (Hz (padrão 5)), `prof` (0–1 (padrão 0.35)) | vibrato de sopro: o volume pulsa (e a afinação um pouco) |
| `zengyin` | 赠音 | `intervalo` (semitons (padrão 3)) | notinha rápida para cima no fim da nota (o 'suspiro' do dizi) |
| `liyin` | 历音 corrida | `notas` (quantas antes (padrão 5)), `tempo` (s (padrão 0.18)), `de` (baixo | cima) | corrida rápida de notas da escala que chega na nota |
| `fanyin` | 泛音 harmonico | — | harmônico soprado: mais puro e mais soproso |
| `forte_sopro` | 强吹 | — | sopro forçado: mais brilho e ruído |

## Xun 埙 (xūn) — `xun`

Flauta de vaso de cerâmica em forma de ovo (ocarina antiga): ressonador de Helmholtz, som quase sem harmônicos, oco e melancólico, com muito ar.

*Um dos instrumentos mais antigos da China: exemplares de ~7000 anos (cultura Yangshao).*

- Família: sopros 吹管
- Extensão: G3–C6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.08` | ataque |
| `soltura` | `0.15` | soltura |
| `portamento` | `0.08` | deslize |
| `brilho` | `0.5` | cor do som 0–1 |
| `ruido` | `1.0` | ar |
| `vibrato` | `0.0` | vibrato automático em notas longas (cents; 0 = desligado) |
| `vibrato_taxa` | `5.5` | Hz do vibrato automático |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `tuyin` | 吐音 lingua | `tipo` (单 | 双 | 三), `velocidade` (golpes/s (padrão 8 / 12 / 12)) | golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo) |
| `huashe` | 花舌 flatterzunge frullato | `taxa` (Hz (padrão 26)), `prof` (0–1 (padrão 0.6)) | língua vibrando (rrrr): som rouco e agitado |
| `qizhenyin` | 气震音 vibrato_ar | `taxa` (Hz (padrão 5)), `prof` (0–1 (padrão 0.35)) | vibrato de sopro: o volume pulsa (e a afinação um pouco) |
| `zengyin` | 赠音 | `intervalo` (semitons (padrão 3)) | notinha rápida para cima no fim da nota (o 'suspiro' do dizi) |
| `liyin` | 历音 corrida | `notas` (quantas antes (padrão 5)), `tempo` (s (padrão 0.18)), `de` (baixo | cima) | corrida rápida de notas da escala que chega na nota |
| `fanyin` | 泛音 harmonico | — | harmônico soprado: mais puro e mais soproso |
| `forte_sopro` | 强吹 | — | sopro forçado: mais brilho e ruído |

## Suona 唢呐 (suǒnà) — `suona`

Oboé de palheta dupla com tubo cônico de madeira e campana de cobre: o instrumento mais alto da China, de casamentos, funerais e festas. O músico controla a palheta com os lábios e faz deslizes enormes, imitações de pássaros e de voz.

*Chegou da Pérsia/Ásia Central (surnay) por volta da dinastia Jin/Yuan. Peça: 百鸟朝凤 (Cem pássaros saúdam a fênix).*

- Família: sopros 吹管
- Extensão: D4–A6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.03` | ataque |
| `soltura` | `0.07` | soltura |
| `portamento` | `0.12` | deslize de lábio |
| `brilho` | `0.65` | cor |
| `ruido` | `1.0` | sopro |
| `vibrato` | `18.0` | vibrato de lábio automático (cents) |
| `vibrato_taxa` | `6.5` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `tuyin` | 吐音 lingua | `tipo` (单 | 双 | 三), `velocidade` (golpes/s (padrão 8 / 12 / 12)) | golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo) |
| `huashe` | 花舌 flatterzunge frullato | `taxa` (Hz (padrão 26)), `prof` (0–1 (padrão 0.6)) | língua vibrando (rrrr): som rouco e agitado |
| `qizhenyin` | 气震音 vibrato_ar | `taxa` (Hz (padrão 5)), `prof` (0–1 (padrão 0.35)) | vibrato de sopro: o volume pulsa (e a afinação um pouco) |
| `zengyin` | 赠音 | `intervalo` (semitons (padrão 3)) | notinha rápida para cima no fim da nota (o 'suspiro' do dizi) |
| `liyin` | 历音 corrida | `notas` (quantas antes (padrão 5)), `tempo` (s (padrão 0.18)), `de` (baixo | cima) | corrida rápida de notas da escala que chega na nota |
| `fanyin` | 泛音 harmonico | — | harmônico soprado: mais puro e mais soproso |
| `forte_sopro` | 强吹 | — | sopro forçado: mais brilho e ruído |
| `yayin` | 压音 labio | `cents` (quanto cai (padrão 150)), `tempo` (s) | aperta a palheta com os lábios: a nota cai e volta |
| `niaoming` | 鸟鸣 passaro | — | canto de pássaro: trinados rápidos e deslizes agudos (百鸟朝凤) |

## Guanzi 管子 (guǎnzi) — `guanzi`

Tubo cilíndrico curto com palheta dupla larga: som rouco, lamentoso e cheio de deslizes. Na dinastia Tang era o 觱篥 (bili) da orquestra da corte; o hichiriki do gagaku descende dele.

- Família: sopros 吹管
- Extensão: G3–C6
- Polifônico: não (monofônico, frases contínuas)

| parâmetro | padrão | o que faz |
|---|---|---|
| `corpo` | `''` | corpo ressonante; vazio = o do instrumento |
| `mistura_corpo` | `1.0` | 0 = sem corpo, 1 = completo |
| `ataque` | `0.04` | ataque |
| `soltura` | `0.12` | tempo de soltura do fim de frase (s) |
| `portamento` | `0.14` | deslize |
| `brilho` | `0.45` | cor |
| `ruido` | `1.0` | multiplica o ruído de arco/sopro |
| `vibrato` | `25.0` | vibrato |
| `vibrato_taxa` | `5.0` | Hz |
| `humanizar` | `0.5` | pequenas instabilidades de afinação e volume |
| `pan` | `0.0` | posição no estéreo dentro da faixa |
| `ganho` | `1.0` | ganho de saída |
| `intervalo_frase` | `0.08` | silêncio (s) acima do qual começa uma frase nova (respira / levanta o arco) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `legato` | 连 ligado | — | liga à nota anterior (sem rearticular) |
| `staccato` | 顿 destacado | — | nota curta e separada |
| `acento` | > 重音 | — | ataque mais forte |
| `sforzando` | sfz 突强 | — | ataque muito forte que cai logo |
| `crescendo` | cresc 渐强 | `de` (mult. inicial (0.3)), `ate` (mult. final (1.3)) | cresce durante a nota |
| `diminuendo` | dim 渐弱 | `de` (1.2), `ate` (0.2) | diminui durante a nota |
| `vibrato` | 揉 rou 颤 | `taxa` (Hz (padrão 5.8)), `prof` (cents (padrão 25)), `atraso` (s), `forma` (simetrico | acima | abaixo) | vibrato de afinação |
| `trinado` | chanyin 颤音 trill | `intervalo` (semitons (padrão 2)), `taxa` (batidas/s (padrão 9)), `atraso` (s) | trinado com o dedo (alterna com a nota de cima) |
| `mordente` | dayin 打音 | `intervalo` (semitons (padrão 2; negativo = abaixo)), `tempo` (s (padrão 0.05)) | toque rápido na nota vizinha logo no ataque |
| `apojatura` | dieyin 叠音 倚音 | `intervalo` (semitons acima (padrão 2)), `tempo` (s (padrão 0.06)) | nota de passagem rápida de cima antes da nota |
| `slide_in` | shanghua 上滑音 绰 | `cents` (padrão 200), `tempo` (s (padrão 0.12)) | entra deslizando de baixo |
| `slide_down_in` | xiahua 下滑音 注 | `cents` (padrão 200), `tempo` (s) | entra deslizando de cima |
| `queda` | fall 下滑 | `cents` (padrão 300), `tempo` (s) | cai de afinação no fim da nota |
| `huihua` | 回滑音 | `cents` (padrão 200), `tempo` (s) | sobe e volta deslizando (ornamento vocal) |
| `portamento` | 滑 glide | `tempo` (duração do deslize (s, padrão 0.25)) | liga à anterior com deslize longo |
| `tuyin` | 吐音 lingua | `tipo` (单 | 双 | 三), `velocidade` (golpes/s (padrão 8 / 12 / 12)) | golpes de língua repetindo a nota (单吐 simples, 双吐 duplo, 三吐 triplo) |
| `huashe` | 花舌 flatterzunge frullato | `taxa` (Hz (padrão 26)), `prof` (0–1 (padrão 0.6)) | língua vibrando (rrrr): som rouco e agitado |
| `qizhenyin` | 气震音 vibrato_ar | `taxa` (Hz (padrão 5)), `prof` (0–1 (padrão 0.35)) | vibrato de sopro: o volume pulsa (e a afinação um pouco) |
| `zengyin` | 赠音 | `intervalo` (semitons (padrão 3)) | notinha rápida para cima no fim da nota (o 'suspiro' do dizi) |
| `liyin` | 历音 corrida | `notas` (quantas antes (padrão 5)), `tempo` (s (padrão 0.18)), `de` (baixo | cima) | corrida rápida de notas da escala que chega na nota |
| `fanyin` | 泛音 harmonico | — | harmônico soprado: mais puro e mais soproso |
| `forte_sopro` | 强吹 | — | sopro forçado: mais brilho e ruído |

# sopros de palheta livre 簧管

## Sheng 笙 (shēng) — `sheng`

Órgão de boca: 17 a 37 tubos de bambu numa cabaça, cada um com uma palheta livre de latão. Toca acordes (tradicionalmente quartas, quintas e oitavas) e soa tanto soprando quanto aspirando. Ancestral do acordeão e da harmônica.

*Há sheng em túmulos de 2400 anos (曾侯乙墓). Na corte Tang era central; o shō do gagaku descende dele.*

- Família: sopros de palheta livre 簧管
- Extensão: G3–A6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `abertura` | `0.32` | fenda |
| `ressonancia` | `0.65` | tubo |
| `impar` | `0.0` | puxa para harmônicos ímpares (som de clarinete) |
| `ruido` | `1.0` | sopro |
| `ataque` | `0.04` | ataque |
| `soltura` | `0.08` | soltura (s) |
| `bordao` | `''` | nota de bordão contínuo (hulusi: tubo extra); vazio = sem |
| `vibrato` | `0.0` | vibrato automático (cents) |
| `pan` | `0.0` | pan |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `hesheng` | 和音 harmonia | `intervalos` (semitons separados por espaço (padrão '-5 -12': quarta e oitava abaixo)) | acrescenta notas do acorde tradicional do sheng (quinta e oitava) |
| `tuyin` | 吐音 lingua | `velocidade` (golpes/s (padrão 8)) | golpes de língua repetindo a nota |
| `huashe` | 花舌 flatterzunge | `taxa` (Hz (26)) | língua vibrando (rrrr) |
| `chanyin` | 颤音 vibrato_ar | `taxa` (Hz (5)), `prof` (0–1 (0.3)) | vibrato de sopro (volume pulsando) |
| `dayin` | 打音 mordente | — | toque rápido na nota de cima no ataque |
| `bend` | 滑音 | `cents` (padrão -60), `tempo` (s) | palhetas livres dobram pouco: até ~meio tom com o sopro |

## Hulusi 葫芦丝 (húlúsī) — `hulusi`

Flauta de cabaça com palheta livre do povo Dai (Yunnan): som doce, de clarinete, com um tubo de bordão que fica soando junto.

- Família: sopros de palheta livre 簧管
- Extensão: F4–C6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `abertura` | `0.5` | fenda |
| `ressonancia` | `0.5` | tubo |
| `impar` | `0.35` | som de clarinete |
| `ruido` | `1.0` | sopro |
| `ataque` | `0.06` | ataque |
| `soltura` | `0.08` | soltura (s) |
| `bordao` | `''` | nota do tubo de bordão (ex.: 'C5'); vazio = desligado |
| `vibrato` | `12.0` | vibrato suave |
| `pan` | `0.0` | pan |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `hesheng` | 和音 harmonia | `intervalos` (semitons separados por espaço (padrão '-5 -12': quarta e oitava abaixo)) | acrescenta notas do acorde tradicional do sheng (quinta e oitava) |
| `tuyin` | 吐音 lingua | `velocidade` (golpes/s (padrão 8)) | golpes de língua repetindo a nota |
| `huashe` | 花舌 flatterzunge | `taxa` (Hz (26)) | língua vibrando (rrrr) |
| `chanyin` | 颤音 vibrato_ar | `taxa` (Hz (5)), `prof` (0–1 (0.3)) | vibrato de sopro (volume pulsando) |
| `dayin` | 打音 mordente | — | toque rápido na nota de cima no ataque |
| `bend` | 滑音 | `cents` (padrão -60), `tempo` (s) | palhetas livres dobram pouco: até ~meio tom com o sopro |

## Bawu 巴乌 (bāwū) — `bawu`

Flauta transversal de palheta livre do sudoeste (Yi, Miao, Hani): som soproso, doce e anasalado.

- Família: sopros de palheta livre 簧管
- Extensão: G4–C6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `abertura` | `0.45` | fenda |
| `ressonancia` | `0.45` | tubo |
| `impar` | `0.2` | ímpares |
| `ruido` | `2.2` | muito ar |
| `ataque` | `0.07` | ataque |
| `soltura` | `0.08` | soltura (s) |
| `bordao` | `''` | nota de bordão contínuo (hulusi: tubo extra); vazio = sem |
| `vibrato` | `10.0` | vibrato |
| `pan` | `0.0` | pan |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `hesheng` | 和音 harmonia | `intervalos` (semitons separados por espaço (padrão '-5 -12': quarta e oitava abaixo)) | acrescenta notas do acorde tradicional do sheng (quinta e oitava) |
| `tuyin` | 吐音 lingua | `velocidade` (golpes/s (padrão 8)) | golpes de língua repetindo a nota |
| `huashe` | 花舌 flatterzunge | `taxa` (Hz (26)) | língua vibrando (rrrr) |
| `chanyin` | 颤音 vibrato_ar | `taxa` (Hz (5)), `prof` (0–1 (0.3)) | vibrato de sopro (volume pulsando) |
| `dayin` | 打音 mordente | — | toque rápido na nota de cima no ataque |
| `bend` | 滑音 | `cents` (padrão -60), `tempo` (s) | palhetas livres dobram pouco: até ~meio tom com o sopro |

# percussão 打击乐

## Bianzhong (sinos do Marquês Yi) 编钟 (biānzhōng) — `bianzhong`

Conjunto de sinos de bronze de seção amendoada (não redonda): cada sino dá DOIS tons — o 正鼓音, batendo no centro da face, e o 侧鼓音, uma terça menor ou maior acima, batendo na lateral. As saliências 枚 na superfície amortecem o som, e os sinos param rápido o bastante para tocar melodia.

*O conjunto do túmulo do Marquês Yi de Zeng (曾侯乙, ~433 a.C., achado em 1978): 65 sinos, ~5 oitavas, com inscrições de afinação. Rossing mediu intervalos entre os dois tons de ~210 a ~490 cents, em volta de 300 (terça menor) e 400 (terça maior).*

- Família: percussão 打击乐
- Extensão: C2–D7
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.55` | malho de madeira em T |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.35` | graves à esquerda, agudos à direita |
| `ganho` | `1.0` | ganho |
| `terca` | `'alternada'` | intervalo do 侧鼓音: menor | maior | alternada (como no conjunto de Zeng) |
| `t60_base` | `3.2` | T60 (s) do sino em dó4; graves soam mais, agudos menos |
| `golpe` | `'zheng'` | zheng = 正鼓 (centro) | ce = 侧鼓 (lateral) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `zheng` | 正鼓 正鼓音 centro | — | bate no centro da face: soa o tom principal (正鼓音) |
| `ce` | 侧鼓 侧鼓音 lateral | — | bate na lateral: soa o segundo tom, uma terça acima (侧鼓音) |
| `tronco` | 撞钟 | — | sino grande batido com tronco de madeira: ataque grave e longo |

## Bianqing (pedras sonoras) 编磬 (biānqìng) — `bianqing`

Conjunto de lâminas de pedra calcária em forma de L penduradas numa moldura: som seco, cristalino e curto, com modos de barra livre (bem inarmônicos). Música ritual 雅乐 junto com o 编钟.

*O túmulo do Marquês Yi tinha 32 pedras afinadas. É o 'som da pedra' (石) da classificação 八音.*

- Família: percussão 打击乐
- Extensão: A3–A6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.85` | malho duro |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.3` | estéreo |
| `ganho` | `1.0` | ganho |
| `t60_base` | `1.6` | T60 em lá4 |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Yunluo (gongos de nuvem) 云锣 (yúnluó) — `yunluo`

Moldura com 10+ gonguinhos afinados de bronze: melodia brilhante, com leve subida de altura no ataque.

- Família: percussão 打击乐
- Extensão: D5–D7
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.7` | baqueta |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.3` | estéreo |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Pengling (sininhos de copo) 碰铃 (pènglíng) — `pengling`

Dois sininhos de copo de bronze presos por um cordão, batidos um no outro: agudo, longo, com batimento.

- Família: percussão 打击乐
- Extensão: C7–C7
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `1.0` | bronze contra bronze |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Qing (tigela de templo) 磬 (qìng) — `qing`

Tigela de bronze dos templos budistas (铜磬), batida com bastão: ressonância longuíssima com batimentos.

- Família: percussão 打击乐
- Extensão: C3–C6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.45` | bastão de madeira forrado |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |
| `t60_base` | `14.0` | T60 (s) |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Daluo (gongo grande da ópera) 大锣 (dàluó) — `daluo`

Gongo de bronze da ópera de Pequim, batido com malho forrado: a altura CAI depois do golpe (não linearidade geométrica do disco: quanto mais forte, mais cai). Marca entradas e momentos dramáticos.

- Família: percussão 打击乐
- Extensão: G2–G4
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.3` | malho forrado |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `sem_glide` | 平音 | — | golpe leve: quase sem glissando |

## Xiaoluo (gongo pequeno da ópera) 小锣 (xiǎoluó) — `xiaoluo`

Gongo pequeno da ópera, batido com uma plaquinha de madeira: a altura SOBE depois do golpe (centro plano mais fino: o disco amolece com a amplitude; Jossic et al., JASA 2018).

- Família: percussão 打击乐
- Extensão: C5–C6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.85` | plaquinha de madeira |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `sem_glide` | 平音 | — | golpe leve: quase sem glissando |

## Chaoluo (tam-tam) 抄锣 (chāoluó) — `chaoluo`

Gongo enorme sem altura definida: depois do golpe, a energia passa dos modos graves para os agudos e o som 'floresce' num chiado brilhante que cresce antes de morrer (caos não linear).

- Família: percussão 打击乐
- Extensão: A1–A1
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.25` | malho grande forrado |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `sem_glide` | 平音 | — | golpe leve: quase sem glissando |

## Jingbo (pratos da ópera) 京钹 (jīngbó) — `jingbo`

Par de pratos médios da ópera de Pequim, com cúpula grande: brilhante e curto.

- Família: percussão 打击乐
- Extensão: E4–E4
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.6` | baqueta macia (0) × dura (1) |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `men` | 闷 abafado_pratos | — | pratos apertados um no outro: 'tchic' curto |

## Naobo (pratos grandes) 铙钹 (náobó) — `naobo`

Pratos grandes de cúpula pequena (铙), dos templos e das procissões: longo e chiado.

- Família: percussão 打击乐
- Extensão: A3–A3
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.6` | baqueta macia (0) × dura (1) |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `men` | 闷 abafado_pratos | — | pratos apertados um no outro: 'tchic' curto |

## Xiaobo (pratos pequenos) 小钹 (xiǎobó) — `xiaobo`

Pratinhos agudos, brilhantes e curtos.

- Família: percussão 打击乐
- Extensão: F5–F5
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.6` | baqueta macia (0) × dura (1) |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `men` | 闷 abafado_pratos | — | pratos apertados um no outro: 'tchic' curto |

## Tanggu (tambor de salão) 堂鼓 (tánggǔ) — `tanggu`

Tambor de barril com duas peles de couro bovino pregadas, tocado com duas baquetas: grave e redondo.

- Família: percussão 打击乐
- Extensão: C2–C4
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.5` | baquetas de madeira |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `aro` | 鼓边 gubian rim | — | bate na borda de madeira do tambor |

## Dagu (tambor grande) 大鼓 (dàgǔ) — `dagu`

Tambor enorme de templo e de guerra: grave profundo que se sente no peito.

- Família: percussão 打击乐
- Extensão: A0–A2
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.3` | baquetas grossas |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `aro` | 鼓边 gubian rim | — | bate na borda de madeira do tambor |

## Bangu (tambor do mestre da ópera) 板鼓 (bǎngǔ) — `bangu`

Tamborzinho de uma pele só, muito esticada sobre um bloco grosso de madeira, tocado com duas varetas finas de bambu: estalo seco e agudo. O tocador do 板鼓 rege a orquestra da ópera.

- Família: percussão 打击乐
- Extensão: B4–B4
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.95` | varetas de bambu |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |
| `aro` | 鼓边 gubian rim | — | bate na borda de madeira do tambor |

## Muyu (peixe de madeira) 木鱼 (mùyú) — `muyu`

Bloco oco de madeira em forma de peixe, dos templos budistas (marca o ritmo das recitações): 'toc' com a cavidade ressoando. Tamanhos diferentes = alturas diferentes.

- Família: percussão 打击乐
- Extensão: C4–C6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `0.6` | baqueta de madeira com ponta |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Bangzi (bastões de madeira) 梆子 (bāngzi) — `bangzi`

Dois bastões de madeira dura batidos um no outro: estalo agudo e penetrante das óperas do norte.

- Família: percussão 打击乐
- Extensão: F#6–F#6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `1.0` | madeira dura |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

## Paiban (castanholas de tábuas) 拍板 (pāibǎn) — `paiban`

Tábuas de madeira dura amarradas que batem juntas ('板' da ópera, junto com o 板鼓): marca o tempo forte. Na corte Tang tinha 6 a 9 tábuas.

- Família: percussão 打击乐
- Extensão: C#6–C#6
- Polifônico: sim

| parâmetro | padrão | o que faz |
|---|---|---|
| `afinacao` | `0.0` | Hz do instrumento quando a nota não tem altura (0 = padrão do instrumento) |
| `dureza` | `1.0` | madeira |
| `borda` | `0.0` | ponto de golpe padrão: 0 = centro/face, 1 = borda/lateral |
| `t60_escala` | `1.0` | multiplica a sustentação |
| `abafar` | `'soar'` | soar = deixa soar até o fim natural | nota = abafa no fim da nota |
| `humanizar` | `0.5` | variação de força e ponto entre golpes |
| `pan` | `0.0` | pan |
| `largura` | `0.0` | espalha notas agudas/graves no estéreo (conjuntos afinados) |
| `ganho` | `1.0` | ganho |

| técnica | também aceita | parâmetros | o que faz |
|---|---|---|---|
| `centro` | 中心 | — | golpe no centro/face |
| `borda` | 边 lateral | — | golpe na borda/lateral: mais modos agudos |
| `abafado` | 闷 muted | `tempo` (s (padrão 0.08)) | abafa logo depois do golpe |
| `soar` | 延音 | — | deixa soar até o fim natural |
| `baqueta_macia` | 软槌 | — | baqueta macia: som redondo, menos ataque |
| `baqueta_dura` | 硬槌 | — | baqueta dura: ataque brilhante |
| `rufo` | 滚奏 roll tremolo | `velocidade` (golpes/s (padrão 18)), `cresc` (crescendo (ex.: 0.5 a 1.0) — 'de-ate') | rufo: golpes rápidos alternando as mãos |
| `flam` | 装饰 | `tempo` (s (0.025)) | dois golpes quase juntos (o primeiro mais fraco) |

# Variantes (presets)

| id | nome | base | parâmetros |
|---|---|---|---|
| `pipa_seda` | Pipa com cordas de seda | `pipa` | material='seda_fina', t60_soltura=0.18, ruido_ataque=0.06 |
| `guzheng_seda` | Guzheng com cordas de seda | `guzheng` | material='seda', dureza=0.6, t60_escala=0.9 |
| `yanzhu_konghou` | Konghou moderno 雁柱箜篌 | `konghou` | material='aco_nylon', dureza=0.55 |
| `daruan` | Daruan 大阮 | `ruan` | afinacao=['D2', 'A2', 'D3', 'A3'], comprimento=0.8, t60_escala=1.2 |
| `xiaoruan` | Xiaoruan 小阮 | `ruan` | afinacao=['D3', 'A3', 'D4', 'A4'], comprimento=0.45 |
| `bangdi` | Dizi bangdi 梆笛 | `dizi` | membrana=0.5, f_membrana=3800.0, brilho=0.7 |
| `bili` | Bili 觱篥 (Tang) | `guanzi` | brilho=0.35, vibrato=12.0 |
