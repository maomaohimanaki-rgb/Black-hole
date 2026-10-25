# Tutorial do Huayin 华音

Do primeiro som até criar instrumentos novos. Cada passo tem código que roda; copie para um arquivo
dentro da pasta `huayin/` (ou instale com `pip install -e .`) e rode com `python3 arquivo.py`.

1. [Primeiro som](#1-primeiro-som)
2. [Uma melodia de verdade (简谱)](#2-uma-melodia-de-verdade)
3. [Técnicas e expressão](#3-técnicas-e-expressão)
4. [Uma pequena orquestra](#4-uma-pequena-orquestra)
5. [Criando um instrumento novo](#5-criando-um-instrumento-novo)
6. [Criando uma técnica nova](#6-criando-uma-técnica-nova)
7. [Corpo, material, afinação e sala novos](#7-corpo-material-afinação-e-sala-novos)
8. [Criando um efeito novo](#8-criando-um-efeito-novo)
9. [Ajustando um instrumento pelo ouvido (e pelo espectro)](#9-ajustando-pelo-ouvido)
10. [Como o motor funciona por dentro](#10-como-o-motor-funciona-por-dentro)

---

## 1. Primeiro som

```python
import huayin as hy

m = hy.Musica("Oi", tempo=60)
qin = m.faixa("qin", "guqin")
qin.nota("C2", t=0, dur=4, vel=0.8)
m.exportar("oi.wav")
```

O que aconteceu: o guqin escolheu a corda solta de dó (1ª corda), simulou o dedo puxando a seda, a
onda circulou na corda perdendo agudos como a seda perde, passou pela caixa de paulównia e entrou no
reverb `palacio_tang` (o padrão). Troque `"guqin"` por `"pipa"`, `"erhu"`, `"dizi"`, `"bianzhong"`…

Para ouvir uma nota sem montar música: `hy.nota_unica("erhu", "A4", 2.0, 0.7, "huarou")`.

---

## 2. Uma melodia de verdade

A forma mais rápida de escrever é o **简谱** (jianpu), a notação numérica que todo músico chinês lê:

```python
m = hy.Musica("Jasmim", tempo=66, tom="1=F")
erhu = m.faixa("erhu", "erhu")
erhu.jianpu("""
3 3/ 5/ 6/ 1'/ 1'/ 6/ | 5 5/ 6/ 5 - |
3 3/ 5/ 6/ 1'/ 1'/ 6/ | 5 5/ 6/ 5 - |
""")
m.exportar("jasmim.wav")
```

- `1`–`7` são os graus (`1=F` → 1 é fá), `0` é pausa.
- `/` corta a duração pela metade (`3/` = colcheia), `.` pontua, `-` soma um tempo.
- `'` sobe uma oitava, `,` desce.

Tudo sobre a notação: [`PARTITURA.md`](PARTITURA.md).

---

## 3. Técnicas e expressão

### 3.1 Técnicas na nota

```python
pipa = m.faixa("pipa", "pipa")
pipa.nota("A3", 0, 2, tecnica="lun")                # trêmulo 轮指
pipa.nota("A3", 2, 2, tecnica="tui:cents=300")      # sobe 300 cents empurrando a corda
pipa.nota("E4", 4, 2, tecnica="tiao+yin")           # polegar + vibrato
pipa.jianpu("5{lun} 6{tui:200} 1'{fanyin} 6{sao}", 6)
```

Os nomes valem em pinyin, chinês ou português (`"lun"`, `"轮指"`, `"lunzhi"`). Esqueceu?
`print(hy.tecnicas("pipa"))` ou `python3 -m huayin info pipa`.

### 3.2 Ligaduras

Uma nota em legato **não tem novo ataque**: na corda o dedo desliza (ou bate/puxa), no erhu o arco
continua, no dizi o sopro continua.

```python
qin.nota("A2", 0, 2, tecnica="gou")
qin.nota("C3", 2, 1, tecnica="deslizar")        # 上: desliza até o dó sem dedilhar
qin.nota("A2", 3, 2, tecnica="deslizar")        # 下: volta
erhu.jianpu("(3 5 6) 5 3", 8)                  # parênteses = legato com portamento
```

### 3.3 Dinâmica

`vel` (0–1 ou `"p"`, `"mf"`…), e no 简谱 `!p`, `!ff`, `!<` (crescendo até a próxima dinâmica).
Em arco/sopro também há técnicas de envelope: `crescendo`, `diminuendo`, `sforzando`, `acento`,
`staccato`.

### 3.4 Afinação desenhada à mão

```python
c = hy.CurvaAltura()
c.inicio_em(-300).para(0.3, 0, "suave")          # entra de baixo
c.vibrato(inicio=0.5, taxa=6, profundidade=30)
c.para(1.6, 0, "degrau").para(2.0, -700, "suave")  # despenca no fim
erhu.nota("D5", 12, 2.5, curva=c)
```

A curva é somada às técnicas — dá para usar as duas.

### 3.5 Humanização e semente

```python
erhu.humanizar(tempo_ms=10, vel=0.07, cents=3)
m = hy.Musica(..., semente=7)   # mesma semente → mesmo áudio, bit a bit
```

---

## 4. Uma pequena orquestra

```python
m = hy.Musica("Corte", tempo=80, tom="1=D", reverb="palacio_tang")
m.andamento(0, 56)
m.andamento(8, 80, rampa=True)                    # 散板 acelerando

pipa = m.faixa("pipa", "pipa_tang", pan=-0.4, volume_db=-2)
erhu = m.faixa("erhu", "erhu", pan=0.3, volume_db=-5)
sheng = m.faixa("sheng", "sheng", volume_db=-12, reverb=0.4)
zhong = m.faixa("sinos", "bianzhong", volume_db=-6)
tambor = m.faixa("tambor", "tanggu", pan=0.2, volume_db=-8)

pipa.jianpu("5 6 1' 6 | 5. 3/ 2 3 | 5 3 2 1 | 2{yaobo} - - - |", 0, oitava=3)
erhu.jianpu("0 0 0 0 | 3 - 5 6 | (5 - 3 2) | 1 - - - |", 0)
for t, a in [(0, "D5"), (8, "A4")]:
    sheng.nota(a, t, 8, 0.45, "hesheng")
zhong.nota("D3", 0, 4, 0.8)
zhong.nota("A3", 8, 4, 0.8, "ce")                 # o segundo tom do sino
for c in range(4):
    tambor.nota(None, c * 4, 1, 0.8)
tambor.nota(None, 14, 2, 0.6, "rufo:cresc=0.3-1.0")

erhu.efeito("eq", bandas=[("pico", 2500, 1.0, 1.5)])
pipa.automacao("pan", [(0, -0.6), (16, -0.2)])
m.loudness_alvo = -16
m.exportar("corte.wav")
m.exportar_stems("corte_stems")                   # cada faixa num arquivo
```

Dicas de mixagem para música chinesa: sopros e arcos um pouco à direita, dedilhados à esquerda (como
na 民族管弦乐团), percussão perto do centro; `reverb` de 0,2–0,35 nos solistas e mais nos sinos.

---

## 5. Criando um instrumento novo

Escolha a **base** pelo jeito que o som é produzido:

| base | para | o que você define |
|---|---|---|
| `CordaDedilhadaBase` | qualquer corda pinçada ou percutida | `AFINACOES`, `MODO_ALTURA`, `CORPO_PADRAO`, material, trastes |
| `HuqinBase` (`instrumentos/arcos.py`) | corda friccionada | `CORDAS`, `BETA`, corpo |
| `FlautaBase` / `SoproBase` (`instrumentos/sopros.py`) | flautas e palhetas | `sintetizar()` ou parâmetros |
| `PalhetaLivreBase` | sheng, harmônicas, hulusi | abertura, ressonância, ímpares |
| `PercussaoBase` | idiofones, membranas | `modos()` (razões, T60, amplitudes) |
| `Instrumento` | algo totalmente novo | `renderizar(notas, n_total, rng)` |

### 5.1 Exemplo completo: 五弦琵琶 (o pipa de 5 cordas da corte Tang)

Arquivo pronto: [`exemplos/05_instrumento_novo.py`](../exemplos/05_instrumento_novo.py).

```python
import huayin as hy
from huayin.instrumentos.pipa import PipaTang

@hy.registrar                       # registra o id (aí funciona em m.faixa, .jp, CLI...)
class Wuxian(PipaTang):             # herda palheta, seda, 4 trastes e as técnicas do pipa Tang
    id = "wuxian_pipa"
    nome = "Pipa de cinco cordas (Tang)"
    nome_cn = "五弦琵琶"
    pinyin = "wǔxián pípa"
    descricao = "Pipa de pescoço reto e 5 cordas tocado com palheta."
    extensao = ("C2", "C4")
    AFINACOES = {"padrao": ["C2", "G2", "C3", "D3", "G3"]}
    AFINACAO_PADRAO = "padrao"
    PARAMETROS = {"largura": (0.18, "abertura estéreo")}   # muda só o que difere
```

Pronto: `m.faixa("w", "wuxian_pipa")` funciona, com todas as técnicas do pipa Tang.

### 5.2 Atributos de uma corda dedilhada

| atributo | significado |
|---|---|
| `AFINACOES`, `AFINACAO_PADRAO` | dicionário nome → lista de notas (grave → agudo) |
| `MODO_ALTURA` | `"trastes"` (pipa, ruan), `"livre"` (guqin, sanxian: sem trastes), `"cordas_fixas"` (guzheng, harpa, yangqin) |
| `TRASTES` | semitons disponíveis acima da corda solta (`None` = cromático). Notas entre trastes viram 推 automático |
| `ALCANCE` | semitons alcançáveis acima da corda solta |
| `MAX_PRESSAO` | cordas fixas: quantos cents a mão esquerda sobe apertando (guzheng 300, harpa 0) |
| `CURSO`, `DESAFINACAO_CURSO` | cordas por nota e desafinação entre elas (yangqin 2–4, yueqin 2) |
| `MARTELO` | `True` = corda percutida (pulso de contato em vez de pinçada) |
| `CORPO_PADRAO` | nome em `huayin.fisica.corpo.CORPOS` |
| `PARAMETROS` | `{nome: (padrão, descrição)}` — sobrepõe os da base (`material`, `dureza`, `posicao`, `abafar`, `simpatia`…) |

Métodos que dá para sobrescrever: `golpe_padrao(nota, rng)` (como uma nota vira um golpe),
`escolher_corda(f, nota)`, `curso_da_nota(g)`, `contato_ms(g)`, `camada(tipo, g, rng)` (sons extras).

### 5.3 Um idiofone: tabela de modos

```python
from huayin.instrumentos.percussao import PercussaoBase
from huayin.fisica.modal import Modo

@hy.registrar
class Fangxiang(PercussaoBase):
    id = "fangxiang"
    nome = "Fangxiang (lâminas de ferro)"
    nome_cn = "方响"
    descricao = "16 lâminas de ferro afinadas da orquestra Tang."
    extensao = ("C5", "C7")
    PARAMETROS = {"dureza": (0.9, "malho")}

    def modos(self, b):
        # barra livre: 1 : 2,76 : 5,40 ; T60 em segundos; amp; peso na borda; participação no glide
        return [Modo(1.0, 2.5, 1.0, 1.0, 0.0), Modo(2.76, 0.9, 0.4, 1.4, 0.0), Modo(5.40, 0.4, 0.2, 1.8, 0.0)]
```

Os campos de `Modo`: `razao` (frequência/fundamental), `t60`, `amp`, `peso_borda` (multiplicador
quando golpeado na borda), `glide` (participação no glissando não linear). Em `params_modal` dá para
ligar `glide_cents`, `batimento_cents`, `florescer`, `n_aleatorio` (modos aleatórios, para pratos).

### 5.4 Totalmente do zero

```python
import numpy as np
from huayin.instrumentos.base import Instrumento

@hy.registrar
class Seno(Instrumento):
    id = "seno"
    nome = "Seno"
    familia = "teste"
    PARAMETROS = {"ganho": (0.3, "ganho")}

    def renderizar(self, notas, n_total, rng):
        buf = np.zeros((2, n_total))
        for n in notas:                         # NotaR: t0, dur (s), f0 (Hz), vel, tecnicas, curva...
            t = np.arange(int(n.dur * self.sr)) / self.sr
            cents = n.curva.avaliar(t.size, self.sr, rng) if n.curva else 0
            fase = 2 * np.pi * np.cumsum(n.f0 * 2 ** (cents / 1200)) / self.sr
            y = np.sin(fase) * np.exp(-3 * t) * n.vel * self.p["ganho"]
            self._colocar(buf, y, n.t0, 0.0)    # soma no buffer estéreo com pan
        return buf
```

### 5.5 Variante (preset) sem código novo

```python
hy.variante("guqin_metal", "guqin", "Guqin com cordas de metal", "cordas modernas de aço-náilon",
            material="aco_nylon", t60_escala=1.2)
```

### 5.6 Documentar

`descrever()` monta a ficha a partir dos atributos e das técnicas. Depois de criar/mudar um
instrumento dentro do pacote, rode `python3 -m huayin doc -o docs/INSTRUMENTOS.md` e adicione um teste
(veja `tests/test_instrumentos.py`: todo instrumento registrado já é testado automaticamente).

---

## 6. Criando uma técnica nova

Uma técnica é um método marcado com `@tecnica`. Ela recebe o "alvo" da nota, a nota resolvida
(`NotaR`: `t0`, `dur`, `f0`, `vel`…), o gerador aleatório, e os parâmetros; e devolve o alvo
modificado. O alvo depende da base:

| base | alvo | campos úteis |
|---|---|---|
| cordas dedilhadas | lista de `Golpe` | `t0`, `dur`, `corda`, `f0`, `vel`, `curva`, `posicao`, `dureza`, `harmonico`, `contato`, `t60_escala`, `t60_soltura`, `camadas`, `deslize`, `sem_corte`, `mudo`, `reexcitacoes` |
| arco/sopro | um `Segmento` (ou lista) | `curva`, `env`, `trocas`, `am`, `articulacao`, `legato`, `portamento`, `brilho`, `ruido`, `extra` |
| percussão | lista de `Batida` | `t0`, `vel`, `f0`, `dur`, `borda`, `dureza`, `t60_escala`, `extra` |
| palheta livre | lista de dicts | `f0`, `t0`, `dur`, `vel`, `curva`, `am`, `trocas` |

```python
from huayin.instrumentos.pipa import Pipa
from huayin.instrumentos.base import Golpe

class MeuPipa(Pipa):
    id = "meu_pipa"

    @hy.tecnica("eco_fantasma", "回声", descricao="repete a nota 3 vezes cada vez mais fraca",
                params={"intervalo": "s entre repetições (padrão 0.2)"})
    def _t_eco(self, golpes, nota, rng, intervalo=0.2):
        out = list(golpes)
        for g in golpes:
            for k in range(1, 4):
                ng = Golpe(**{**g.__dict__, "camadas": []})   # cópia do golpe
                ng.t0 = g.t0 + k * intervalo
                ng.vel = g.vel * 0.5 ** k
                ng.posicao = min(0.45, g.posicao * (1 + 0.3 * k))   # cada vez mais "redondo"
                out.append(ng)
        return out

hy.registrar(MeuPipa)
```

Uso: `f.nota("A3", 0, 2, tecnica="eco_fantasma:intervalo=0.15")` ou no 简谱 `5{回声}`.

Regras: os nomes em `params` são os únicos aceitos (o motor recusa os outros com mensagem clara); o
primeiro parâmetro aceita a forma curta `nome:valor`; técnicas aplicam-se na ordem escrita (`"lun+tui"`
faz o trêmulo e depois sobe a afinação de todos os golpes).

Ferramentas prontas nas bases: `self._repetir(...)` (trêmulos), `self._estrumar(...)` (pipa),
`g.curva.para(...)`/`.vibrato(...)`, camadas `("batida" | "clique" | "rasgo", {...})`.

---

## 7. Corpo, material, afinação e sala novos

### 7.1 Corpo (caixa de ressonância)

```python
from huayin.fisica.corpo import CORPOS, Corpo
CORPOS["cabaça"] = Corpo("cabaça",
    modos=[(180, 0.10, 1.0), (420, 0.07, 0.8), (900, 0.05, 0.6), (1900, 0.03, 0.4)],  # (Hz, T60 s, ganho)
    direto=0.3, passa_alta=60, passa_baixa=9000, eq=[("pico", 2500, 1.0, 2.0)])
m.faixa("x", "ruan", corpo="cabaça")
freqs, db = CORPOS["cabaça"].resposta(48000)    # confira a curva
```

Modos mais graves e T60 maiores = caixa maior/mais viva. O nível é normalizado pela energia da
resposta, então trocar de corpo não muda o volume.

### 7.2 Material de corda

```python
from huayin.fisica.corda import MATERIAIS, Material
MATERIAIS["seda_crua"] = Material("seda_crua", t60_baixo=6.0, f_baixo=100, t60_alto=0.5, f_alto=2500,
                                  B_ref=3e-5, f_B=100, ruido_atrito=1.2, enrolamentos_por_m=2200)
m.faixa("q", "guqin", material="seda_crua")
```

`T60(f)` segue `σ(f) = b1 + b3·f²` passando pelos dois pontos dados. `B_ref` é a rigidez (parciais
agudas desafinadas para cima). `ruido_atrito`/`enrolamentos_por_m` controlam o chiado do dedo deslizando.

### 7.3 Afinação

```python
m = hy.Musica(temperamento="personalizada")
m.afinacao = hy.Afinacao(la4=440, temperamento="personalizada", tonica="D",
                         tabela=[1, 256/243, 9/8, 32/27, 81/64, 4/3, 729/512, 3/2, 128/81, 27/16, 16/9, 243/128])
m.afinacao.cents[6] = -10    # e ainda dá para mexer nota a nota (classe de altura 6 = fá#/sol♭)
```

### 7.4 Sala (reverb)

```python
from huayin.efeitos import SALAS, Sala
SALAS["pagode"] = Sala("pagode", t60_grave=3.2, t60_agudo=1.4, tamanho=1.6, pre_atraso=0.03,
                       reflexoes=[(0.021, 0.5, -0.5), (0.034, 0.4, 0.5)], difusao=0.7, passa_baixa=7000)
m.sala = "pagode"
```

---

## 8. Criando um efeito novo

Um efeito é uma função `f(x, sr, **params) -> x` com `x` estéreo `(2, N)`:

```python
import numpy as np
from huayin import efeitos as FX

def tremolo(x, sr, taxa=5.0, prof=0.5):
    t = np.arange(x.shape[1]) / sr
    return x * (1 - prof * 0.5 * (1 - np.cos(2 * np.pi * taxa * t)))

FX.EFEITOS["tremolo"] = tremolo
faixa.efeito("tremolo", taxa=7, prof=0.3)
```

Laços de amostra (filtros recursivos, atrasos variáveis) ficam rápidos com `@njit` de
`huayin.dsp.kernels` (veja os kernels de lá como modelo).

---

## 9. Ajustando pelo ouvido

1. Renderize uma nota com `hy.nota_unica(...)` variando um parâmetro de cada vez.
2. Olhe o espectrograma (com matplotlib instalado):

```python
import numpy as np, matplotlib.pyplot as plt
from scipy.signal import spectrogram
y = hy.nota_unica("pipa_tang", "D3", 3, 0.8, "sao")[0]
f, t, S = spectrogram(y, 48000, nperseg=4096, noverlap=3584)
plt.pcolormesh(t, f, 10 * np.log10(S + 1e-12), vmin=10 * np.log10(S.max()) - 90); plt.ylim(0, 6000)
plt.savefig("espectro.png")
```

3. O que mexer: sustentação → `t60_escala`/material; brilho do ataque → `dureza`, `posicao`;
   "caixa" → corpo; nasal/vocal (erhu) → modos do corpo entre 600 Hz e 2,5 kHz; zumbido do dizi →
   `membrana`, `f_membrana`; ar → `ruido`.
4. Compare com uma gravação de referência no mesmo espectrograma (mesma nota).

---

## 10. Como o motor funciona por dentro

```
Musica.renderizar()
 └─ para cada Faixa
     ├─ resolver(): tempos → segundos (MapaTempo, com rampas), altura → Hz (Afinacao), humanização
     ├─ instrumento.preparar(afinacao)             (cordas seguem o temperamento)
     ├─ instrumento.renderizar(notas, n_total, rng)
     │    cordas:  nota → corda → golpe → técnicas → corte por corda → guia de onda (numba)
     │             → atrito/camadas → corpo (convolução) → ressonância simpática
     │    arco/sopro: notas → frases → curvas por amostra (f, amp, dinâmica) → modelo físico → corpo
     │    percussão: nota → batidas → técnicas → síntese modal
     ├─ efeitos de inserção → automação (volume, pan, largura) → envio de reverb
 ├─ reverb FDN do bus · efeitos do master · corte do silêncio
 └─ loudness (BS.1770) + limitador → exportar
```

A física de cada modelo e as fontes estão em [`FIDELIDADE.md`](FIDELIDADE.md).
