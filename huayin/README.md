# 华音 Huayin — motor de instrumentos clássicos chineses

Motor em Python que **sintetiza instrumentos chineses por modelagem física**: nada de samples. Cada
nota sai de uma simulação do que acontece no instrumento de verdade — a corda de seda vibrando, o arco
de crina grudando e escorregando, o jato de ar batendo na borda do bambu, a membrana do dizi zumbindo,
o gongo de bronze mudando de altura depois do golpe.

São **41 instrumentos + 7 variantes**, com **119 técnicas diferentes** — 726 combinações instrumento × técnica — (轮指, 推拉, 吟猱, 泛音, 滑音,
花舌, 刮奏, 当心画…), afinações históricas (三分损益, justa, igual de 朱载堉), leitor de **简谱**, MIDI,
mixer, reverbs de espaços (palácio Tang, templo, gruta de Dunhuang) e exportação WAV/FLAC/**OGG** (direto
para o Minecraft).

> É uma aproximação física, não uma gravação. O que foi medido, o que foi estimado e onde estão os
> limites está em [`docs/FIDELIDADE.md`](docs/FIDELIDADE.md).

---

## Sumário

1. [Instalação](#1-instalação)
2. [Começo rápido](#2-começo-rápido)
3. [Instrumentos](#3-instrumentos)
4. [Escrevendo música](#4-escrevendo-música)
5. [Técnicas](#5-técnicas)
6. [Afinação, tom e escalas](#6-afinação-tom-e-escalas)
7. [Mixer, efeitos e master](#7-mixer-efeitos-e-master)
8. [Arquivos: 简谱 (.jp), JSON, MIDI, áudio](#8-arquivos)
9. [Linha de comando](#9-linha-de-comando)
10. [Referência rápida da API](#10-referência-rápida-da-api)
11. [Desempenho](#11-desempenho)
12. [Estrutura do código](#12-estrutura-do-código)
13. [Problemas comuns](#13-problemas-comuns)

Outros documentos:
- [`docs/TUTORIAL.md`](docs/TUTORIAL.md) — passo a passo, do primeiro som a **criar instrumento, técnica, corpo, material, afinação e efeito novos**.
- [`docs/PARTITURA.md`](docs/PARTITURA.md) — a notação 简谱 em texto e o formato JSON completos.
- [`docs/INSTRUMENTOS.md`](docs/INSTRUMENTOS.md) — ficha de cada instrumento: parâmetros e técnicas (gerada pelo motor).
- [`docs/FIDELIDADE.md`](docs/FIDELIDADE.md) — a pesquisa: física de cada modelo, fontes e limites.

---

## 1. Instalação

Precisa de Python 3.10+.

```bash
cd huayin
pip install -r requirements.txt              # numpy, scipy, numba, soundfile, mido
# Linux com Python do sistema:
pip install --break-system-packages -r requirements.txt
# opcional: tocar direto na caixa de som e desenhar gráficos
pip install -r requirements-opcional.txt     # sounddevice, matplotlib
```

Para usar de qualquer pasta: `pip install -e .` (aí `import huayin` e o comando `huayin` funcionam em
todo lugar). Sem instalar, rode de dentro da pasta `huayin/` (`python3 -m huayin ...`).

Testar se está tudo certo:

```bash
python3 -m unittest discover -s tests -t tests     # 39 testes, ~15 s
python3 -m huayin demo -o demos                    # gera demos/huayin_demo.wav (长安夜)
```

> **numba** compila os laços de amostra das cordas, do arco, das flautas e do reverb. Sem ele o motor
> continua funcionando, só que dezenas de vezes mais lento. A primeira execução compila e guarda em
> cache (demora ~10 s uma vez só).

---

## 2. Começo rápido

```python
import huayin as hy

m = hy.Musica("Primeira", tempo=72, tom="1=D")       # andamento e tom (1 = ré)
pipa = m.faixa("pipa", "pipa_tang")                   # uma faixa = um músico

pipa.nota("D3", t=0, dur=1, vel=0.8, tecnica="sao")  # varre as 4 cordas com a palheta
pipa.jianpu("5 6 1' 6 | 5. 3/ 2 3 | 5{yaobo} - - - |", inicio=1)
pipa.nota("D3", t=13, dur=3, vel=1.0, tecnica="huaxian")   # o golpe final do 琵琶行

m.exportar("primeira.wav")                            # ou .ogg / .flac
```

Uma nota só, para experimentar parâmetros:

```python
audio = hy.nota_unica("erhu", "A4", dur=2, vel=0.7, tec="huarou")
hy.salvar_audio("erhu.wav", audio, 48000)
```

Exemplos prontos em [`exemplos/`](exemplos) (rode `python3 exemplos/01_primeira_nota.py`; a saída vai
para `exemplos/saida/`):

| arquivo | o que mostra |
|---|---|
| `01_primeira_nota.py` | nota, trêmulo, bend, harmônico, acorde batido |
| `02_pipa_tang.py` | o pipa Tang tocando os versos do 琵琶行, em lá = 430 Hz |
| `03_guqin.py` | os três sons do guqin, 徽, 吟猱, 上下, 滚拂, com xiao |
| `04_orquestra_jianpu.py` | 茉莉花 para erhu, dizi, guzheng e ruan a partir de um `.jp` |
| `05_instrumento_novo.py` | cria o 五弦琵琶 (pipa de 5 cordas) com corpo e técnica novos |
| `06_afinacoes_historicas.py` | a mesma frase em temperamento igual, 三分损益 e justa |
| `07_minecraft_ogg.py` | sons .ogg mono para o addon |
| `08_api_avancada.py` | curva de afinação à mão, automação, chorus, humanização, stems |

---

## 3. Instrumentos

`python3 -m huayin listar` mostra todos; `python3 -m huayin info guqin` mostra a ficha completa.

| família | instrumentos (`id`) |
|---|---|
| **cordas dedilhadas** 弹拨 | `pipa` 琵琶 · `pipa_tang` 曲项琵琶 (Tang) · `guqin` 古琴 · `guzheng` 古筝 · `konghou` 箜篌 (harpa Tang) · `se` 瑟 · `ruan` 中阮 · `liuqin` 柳琴 · `yueqin` 月琴 · `sanxian` 三弦 · `yangqin` 扬琴 (percutido) |
| **cordas friccionadas** 拉弦 | `erhu` 二胡 · `gaohu` 高胡 · `zhonghu` 中胡 · `banhu` 板胡 · `jinghu` 京胡 |
| **sopros** 吹管 | `dizi` 笛子 · `xiao` 箫 · `xun` 埙 · `suona` 唢呐 · `guanzi` 管子 |
| **palheta livre** 簧管 | `sheng` 笙 · `hulusi` 葫芦丝 · `bawu` 巴乌 |
| **sinos e pedras** | `bianzhong` 编钟 (dois tons por sino) · `bianqing` 编磬 · `yunluo` 云锣 · `pengling` 碰铃 · `qing` 磬 |
| **gongos e pratos** | `daluo` 大锣 (altura cai) · `xiaoluo` 小锣 (altura sobe) · `chaoluo` 抄锣 · `jingbo` 京钹 · `naobo` 铙钹 · `xiaobo` 小钹 |
| **tambores e madeiras** | `tanggu` 堂鼓 · `dagu` 大鼓 · `bangu` 板鼓 · `muyu` 木鱼 · `bangzi` 梆子 · `paiban` 拍板 |
| **variantes** | `pipa_seda` · `guzheng_seda` · `yanzhu_konghou` · `daruan` · `xiaoruan` · `bangdi` · `bili` 觱篥 (Tang) |

Todo instrumento aceita parâmetros na criação da faixa, por exemplo:

```python
m.faixa("qin", "guqin", afinacao="manjiao", material="aco_nylon", t60_escala=1.3)
m.faixa("zheng", "guzheng", afinacao="G", simpatia=0.2, largura=0.8)
m.faixa("erhu", "erhu", vibrato=0, ruido_crina=0.05, forca=0.15)
m.faixa("dizi", "dizi", membrana=0.6, f_membrana=3600)       # mais zumbido do 笛膜
m.faixa("pipaT", "pipa_tang", afinacao="pingdiao", batida=0.6)
m.faixa("hulusi", "hulusi", bordao="D4")                      # tubo de bordão ligado
```

Parâmetro errado dá erro com sugestão (`materail` → "Quis dizer: material?"). A lista completa de
parâmetros de cada instrumento está em [`docs/INSTRUMENTOS.md`](docs/INSTRUMENTOS.md).

**Parâmetros que quase todos têm:** `ganho`, `humanizar` (0–1), `mistura_corpo` (0 = sem caixa de
ressonância). Cordas: `material`, `posicao` (ponto do dedilhado), `dureza` (dedo × unha × palheta),
`t60_escala` (sustentação), `abafar` (`nota` | `soar`), `simpatia`, `largura`, `afinacao`. Arco/sopro:
`ataque`, `soltura`, `portamento`, `vibrato`, `vibrato_taxa`, `brilho`, `ruido`. Percussão: `dureza`,
`borda`, `afinacao` (Hz), `abafar`.

---

## 4. Escrevendo música

### Musica e Faixa

```python
m = hy.Musica(
    titulo="Noite em Chang'an", tempo=72, compasso="4/4", tom="1=D",
    la4=440.0,                 # 442 nas orquestras chinesas, 430 no gagaku
    temperamento="igual",      # igual | zhu_zaiyu | sanfen_sunyi | justa | personalizada
    sr=48000, semente=0,       # a semente torna tudo reproduzível (humanização, ruídos)
    reverb="palacio_tang", nivel_reverb=1.0,
)
f = m.faixa("nome", "instrumento", volume_db=0, pan=0.0, largura=1.0, reverb=0.25,
            mudo=False, solo=False, **parametros_do_instrumento)
```

O tempo é contado em **tempos** (beats: semínima = 1). `m.compasso_em(5)` dá o tempo do compasso 5.

### Notas

```python
f.nota(altura, t=None, dur=1.0, vel=0.6, tecnica=None, corda=None, legato=False, curva=None, pan=None, params={})
```

- **altura:** `"A4"`, `"C#5"`, `"Bb3"`, `"sol3"`, `"A4+15"` (15 cents acima), `69` (MIDI), `440.0` (Hz),
  `None` (percussão sem altura).
- **t:** em tempos; `None` = logo depois da última nota (cursor da faixa).
- **vel:** 0–1, ou `"pp"`…`"fff"`, ou 1–127 (estilo MIDI).
- **tecnica:** `"lun"`, `"tui:cents=300"`, `"gou+nao"` (várias com `+`), lista ou dicionário — §5.
- **corda:** força a corda (0 = a mais grave).
- **legato:** liga na nota anterior sem novo ataque (slide na corda, mesma arcada, mesmo sopro).
- **curva:** `CurvaAltura` desenhada à mão (§10).
- **params:** extras por nota, ex. `params={"hui": 7.6}` no guqin (nota apertada no 七徽六).

Atalhos:

```python
f.sequencia("A4 B4 D5 - E5", dur=0.5)          # '-' = pausa
f.acorde(["D3", "A3", "D4"], t=8, dur=2, arpejo=0.05)
f.pausa(2)                                      # avança o cursor
f.jianpu("1 2 3 5 | 6 - - - |", inicio=0, tom="1=G", oitava=4)   # §8 e docs/PARTITURA.md
```

### Andamento

```python
m.andamento(16, 96)               # no tempo 16 muda para 96 bpm
m.andamento(32, 60, rampa=True)   # do evento anterior até o tempo 32 desacelera aos poucos (rit.)
```

No 简谱: `@tempo=96`, e `@rit … @tempo=60` para uma rampa. Ótimo para o 散板 (início livre) → 快板.

### Humanização

```python
f.humanizar(tempo_ms=8, vel=0.06, cents=2)   # desvios reproduzíveis (dependem da semente)
```

Além disso, cada instrumento já varia ponto de dedilhado, força e microafinação (`humanizar=0.5`).

---

## 5. Técnicas

Cada técnica tem um nome curto em pinyin e **aceita também o nome em chinês e em português**:
`"lun"`, `"轮指"` e `"lunzhi"` são a mesma coisa; `"tui"`, `"推"` e `"bend"` também.

```python
f.nota("A3", 0, 2, tecnica="lun")                        # simples
f.nota("A3", 2, 2, tecnica="lun:velocidade=20,tipo=meio")  # com parâmetros
f.nota("A3", 4, 2, tecnica="tui:300")                    # primeiro parâmetro sem nome
f.nota("A3", 6, 2, tecnica="tiao+yin")                   # duas técnicas, aplicadas em ordem
f.nota("A3", 8, 2, tecnica={"tui": {"cents": 200}, "yin": {}})
```

No 简谱: `5{lun}`, `3{tui:cents=300}{yin}`.

`hy.tecnicas("guqin")` lista as técnicas com descrição; `python3 -m huayin info guqin` mostra a ficha.
Destaques:

| instrumento | técnicas |
|---|---|
| pipa | 弹 tan · 挑 tiao · 轮指 lun (5 dedos, cada um com força própria) · 摇指 yaozhi · 扫 sao · 拂 fu · 扫拂 saofu · 分 fen · 推/拉 tui · 推复 bend_volta · 吟/揉 vibrato (só sobe, como no real) · 泛音 fanyin · 绞弦 jiaoxian (cordas cruzadas = caixa) · 煞音 shayin · 拍 pai · 提 ti · 打 hammer · 带 puxada · 滑 deslizar |
| pipa Tang | 抹 mo (palheta para baixo, forte) · 挑 tiao (para cima, fraca) · 拢 long · 捻 nian · 扫拨 sao · 回拨 fu · 摇拨 yaobo · 撮 cuo · **当心画 huaxian** ("seda rasgando") |
| guqin | 勾 抹 挑 剔 打 摘 擘 托 (dedos/direções diferentes) · 撮 cuo · 轮 lun · 锁 suo · 滚拂 gunfu · 散 san · 泛 fanyin (com `hui=`) · 吟 yin · 猱 nao · 绰 chuo · 注 zhu · 上/下 deslizar · 进复 · 退复 · 往来 · 撞 · 掐起 · 罨 |
| guzheng | 托 抹 勾 · 摇指 yaozhi · 扫摇 · 刮奏 guazou · 花指 huazhi · 撮 · 揉 rou · 颤 chan · 上滑音 · 下滑音 · 回滑音 · 点按 · 按音 automático |
| yangqin | 单竹 · 轮竹 lunzhu · 颤竹 · 齐竹 · 滑竹 · 弹轮 (pizz) · 止音 |
| erhu e família | 压揉 · 滚揉 · 滑揉 · 滑音 · 回滑音 · 颤音 trinado · 打音 · 拨弦 pizz · 击弓 · 泛音 · 顿弓 · 跳弓 · 快弓 · 连弓 · 颤弓 · 抛弓 · **马嘶 mati** (relincho do 赛马) · 近码 · 远码 |
| dizi, xiao, xun, suona, guanzi | 吐音 tuyin (单/双/三) · 花舌 huashe · 气震音 · 颤音 · 打音 · 叠音 · 赠音 · 历音 · 滑音 · 泛音 · suona: 压音 yayin · 鸟鸣 niaoming |
| sheng, hulusi, bawu | 和音 hesheng · 吐音 · 花舌 · 颤音 · 打音 · bend |
| bianzhong | 正鼓 zheng (centro) · **侧鼓 ce** (lateral: o segundo tom, uma terça acima) · 撞钟 tronco |
| percussão | centro · borda · abafado · baqueta macia/dura · rufo (com `cresc=0.3-1.0`) · flam · tambores: 鼓边 aro · pratos: 闷 men · gongos: sem_glide |

Técnicas que **ligam na nota anterior** (sem novo ataque): `hammer` 打, `puxada` 带, `deslizar` 上/下/滑
(cordas) e `legato`, `portamento`, `liangong` (arco/sopro). Também dá para usar `legato=True` na nota, ou
parênteses no 简谱: `(1 2 3)`.

---

## 6. Afinação, tom e escalas

```python
hy.Musica(tom="1=D", la4=442, temperamento="sanfen_sunyi")
```

| temperamento | o que é |
|---|---|
| `igual` / `zhu_zaiyu` | 12 partes iguais. 朱载堉 (Zhu Zaiyu) calculou isso em 1584 (新法密率), antes da Europa. |
| `sanfen_sunyi` | 三分损益: notas geradas por quintas puras a partir do 黄钟 (pitagórico chinês). O ciclo não fecha: o 仲吕 fica 23,5 cents alto. |
| `justa` | 纯律: terças e sextas puras (5:4, 5:3), as dos harmônicos do guqin. |
| `personalizada` | `Afinacao(temperamento="personalizada", tabela=[12 razões])` |

O temperamento é construído a partir da tônica do tom (`1=D` → ré) ou de `tonica_temperamento`. As cordas
dos instrumentos seguem o temperamento da música.

Escalas (`hy.ESCALAS`): `pentatonica` (五声), `yayue` (雅乐, com 变徵 e 变宫), `qingyue` (清乐 = maior),
`yanyue` (燕乐 Tang, com 清角 e 闰). `hy.escala_midi("D", "pentatonica", de="D3", ate="D5")` lista as
notas; `huayin.afinacao.final_do_modo("D", "羽")` dá o repouso de cada modo (宫 商 角 徵 羽).

Afinações de instrumento: `guqin` (`zhengdiao`, `manjiao`, `ruibin`, `mangong`, `qingshang`),
`guzheng` (pentatônica em D, C, G, F, A, Bb, E), `pipa_tang` (`yiyue` 壹越调, `pingdiao` 平调,
`huangzhong`, `shuangdiao`, `moderna`), `pipa` (`moderna`, `baixa`, `nanyin`), ou qualquer lista:
`afinacao=["C2", "D2", "F2", "G2", "A2", "C3", "D3"]`.

---

## 7. Mixer, efeitos e master

```python
f = m.faixa("dizi", "dizi", volume_db=-3, pan=0.3, largura=1.0, reverb=0.3)   # reverb = envio (0–1)
f.efeito("eq", bandas=[("passa_alta", 250, 0.7, 0), ("pico", 3000, 1.0, 2.5)])
f.efeito("compressor", limiar_db=-18, razao=3)
f.efeito("eco", tempo=0.375, realimentacao=0.3, mistura=0.2)
f.efeito("chorus", prof_ms=3, taxa=0.7, mistura=0.4)    # vira um naipe em uníssono
f.efeito("distancia", metros=12)                        # afasta: menos volume e menos agudo
f.automacao("volume_db", [(0, -30), (8, 0)])            # fade in em 8 tempos
f.automacao("pan", [(0, -1), (16, 1)], forma="suave")   # atravessa o palco
f.automacao("reverb", [(0, 0.1), (16, 0.8)])

m.sala = "templo"            # reverb do bus: sala | palacio_tang | templo | gruta_dunhuang | patio |
m.nivel_reverb = 0.8         #   jardim | teatro_opera | caverna  (ou um hy.efeitos.Sala próprio)
m.efeito_master("eq", bandas=[("prateleira_alta", 8000, 0.7, 1.5)])
m.loudness_alvo = -16        # LUFS (BS.1770); None = sem normalizar
m.teto_db = -1.0             # pico máximo
m.limite_db = 6.0            # quanto o limitador pode segurar para chegar no loudness
```

Efeitos: `eq`, `compressor`, `limitador`, `saturacao`, `eco`, `chorus`, `distancia`, `reverb`, `ar`.
Tipos de banda do EQ: `passa_baixa`, `passa_alta`, `passa_banda`, `rejeita`, `pico`,
`prateleira_baixa`, `prateleira_alta`. Todos os efeitos também funcionam fora da música:
`hy.efeitos.reverb(audio, 48000, "gruta_dunhuang")`.

---

## 8. Arquivos

| ação | código |
|---|---|
| exportar áudio | `m.exportar("x.wav", bits=24)` · `.flac` · `.ogg` (Vorbis) · `mono=True` · `normalizar="lufs" \| "pico" \| None` |
| faixas separadas | `m.exportar_stems("pasta")` (mesmo ganho do mix + o reverb à parte) |
| só o array | `audio = m.renderizar()` → numpy `(2, N)`; `m.renderizar(stems=True)` → `(mix, {faixa: audio})` |
| salvar o projeto | `m.salvar("musica.json")` / `hy.Musica.carregar("musica.json")` |
| 简谱 | `hy.Musica.carregar("musica.jp")` — cabeçalho + blocos `[faixa nome: instrumento]` |
| MIDI | `m.exportar_midi("x.mid")` / `hy.Musica.carregar("x.mid")` |
| tocar | `m.tocar()` (precisa de `sounddevice`) |

Um `.jp` (formato completo em [`docs/PARTITURA.md`](docs/PARTITURA.md)):

```
titulo: 茉莉花
tempo: 66
tom: 1=F
reverb: jardim

[faixa melodia: erhu]
volume_db: -1
3 3/ 5/ 6/ 1'/ 1'/ 6/ | (5 5/ 6/) 5{huarou} - |

[faixa cama: guzheng]
oitava: 3
1{huazhi} - 5 - | 1 - 5 - |
```

Na importação MIDI, o programa General MIDI escolhe o instrumento (Koto → guzheng, Fiddle → erhu,
Shanai → suona, Shamisen → sanxian…), o canal 10 vira percussão chinesa, pitch bend vira curva de
afinação e CC1 liga vibrato. Para forçar: `huayin.composicao.midi.importar_midi("x.mid", instrumentos={0: "pipa"})`.

### Para o Minecraft (Dooms Day)

```python
m.loudness_alvo = -18
m.exportar("RP/sounds/.../sgx_algo.ogg", mono=True)   # mono = posicional (3D)
```

No addon, quem escreve em `RP/` são os geradores de `tools/` (regra do projeto). Use o motor para gerar
os `.ogg` numa pasta de trabalho e deixe o gerador copiar/registrar. Veja `exemplos/07_minecraft_ogg.py`.

---

## 9. Linha de comando

```bash
python3 -m huayin listar [--familia sopro]
python3 -m huayin info pipa_tang
python3 -m huayin nota guqin C2 --tecnica "bo+nao" --dur 4 -o qin.wav
python3 -m huayin jianpu erhu "3 5 6 1' | 6{huarou} - - - |" --tom 1=D -o erhu.wav
python3 -m huayin render exemplos/partituras/molihua.jp -o molihua.ogg --midi molihua.mid --stems stems/
python3 -m huayin demo -o demos                  # a peça 长安夜
python3 -m huayin demo --catalogo -o catalogo    # um .wav por instrumento com TODAS as técnicas
python3 -m huayin demo --catalogo --instrumento suona -o catalogo
python3 -m huayin doc -o docs/INSTRUMENTOS.md    # regenera a referência
```

---

## 10. Referência rápida da API

```python
import huayin as hy

hy.Musica(...)                      # a peça
m.faixa(nome, instrumento, ...)     # → Faixa
f.nota / f.sequencia / f.acorde / f.jianpu / f.pausa
f.efeito / f.automacao / f.humanizar
m.andamento / m.compasso_em / m.efeito_master
m.renderizar / m.exportar / m.exportar_stems / m.exportar_midi / m.salvar / Musica.carregar / m.tocar

hy.listar_instrumentos(familia=None)  hy.tecnicas(id)  hy.ajuda(id)  hy.nota_unica(id, altura, dur, vel, tec)
hy.criar(id, sr, **params)            # instância de instrumento
hy.Afinacao  hy.Tom  hy.nota_para_midi  hy.midi_para_nome  hy.escala_midi  hy.ESCALAS  hy.TEMPERAMENTOS
hy.CurvaAltura  hy.Automacao  hy.Nota  hy.DINAMICAS
hy.efeitos  hy.SALAS  hy.CORPOS  hy.Corpo  hy.MATERIAIS  hy.Material
hy.registrar  hy.tecnica  hy.variante  hy.Instrumento   # para criar instrumentos (docs/TUTORIAL.md)
hy.salvar_audio(caminho, audio, sr, bits=24, mono=False)
```

**CurvaAltura** — afinação ao longo da nota, em cents relativos à nota escrita:

```python
c = hy.CurvaAltura()
c.inicio_em(-200)                    # começa um tom abaixo
c.para(0.15, 0, "suave")             # chega na nota em 0,15 s  (formas: linear | suave | degrau | rapido)
c.vibrato(inicio=0.3, fim=None, taxa=5.5, profundidade=25, forma="simetrico",   # acima | abaixo
          ataque=0.2, decaimento=0.0, aceleracao=0.0, jitter=0.08)
c.deriva = 3                         # instabilidade lenta aleatória (cents)
f.nota("A4", 0, 2, curva=c)
```

---

## 11. Desempenho

Medido neste container (1 núcleo, numba ligado): a peça demo de 44 s com 11 faixas renderiza em ~15 s;
`茉莉花` (47 s, 4 faixas, ~110 notas) em ~12 s. Uma nota de corda de 1,5 s custa ~20 ms.
O que mais pesa: trêmulos longos (cada golpe é uma simulação), muitas faixas com cordas soltas
soando (`abafar="soar"`) e o reverb (proporcional à duração). Para rascunhos use `sr=24000` ou `32000`.

---

## 12. Estrutura do código

```
huayin/
  requirements.txt  requirements-opcional.txt  pyproject.toml
  huayin/
    dsp/          util (conversões, ruído, envelopes, LUFS) · filtros (biquads, modos) · kernels (numba)
    fisica/       corda (guia de onda) · arco · sopro (jato, palhetas, membrana) · modal · corpo
    afinacao/     notas, temperamentos, Tom, escalas e modos
    composicao/   nota · curvas · tempo · musica (Musica/Faixa/mixer/exportação) · jianpu · midi
    instrumentos/ base (registro, técnicas) · dedilhadas_base · continuo_base · pipa · guqin ·
                  guzheng · alaudes · yangqin · arcos · sopros · percussao
    efeitos/      reverb FDN, EQ, dinâmica, eco, chorus…
    cli.py  demos.py
  exemplos/  docs/  tests/
```

---

## 13. Problemas comuns

| sintoma | causa / solução |
|---|---|
| muito lento | numba não instalado (`hy.TEM_NUMBA` é `False`) → `pip install numba` |
| aviso "notas abaixo de ré4 … flauta" | o modelo de jato pula de modo abaixo de ~290 Hz; use `xun` ou suba a oitava |
| técnica desconhecida | o erro sugere o nome certo; `hy.tecnicas("instrumento")` lista todas |
| nota "estranha" no guzheng/konghou | nota fora das cordas: o guzheng aperta até 3 semitons (按音); o konghou Tang não dobra. Mude `afinacao` |
| nota fora da extensão | o motor toca mesmo assim, mas a física fica fora da faixa calibrada (veja `extensao` no `info`) |
| clipping | não acontece no master (limitador); dentro de uma faixa, baixe `volume_db` ou `ganho` |
| OGG não grava | o `libsndfile` do sistema é antigo; atualize `soundfile` (`pip install -U soundfile`) |
