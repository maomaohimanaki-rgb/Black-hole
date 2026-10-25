# Partituras: 简谱 em texto, arquivo `.jp` e formato JSON

## 1. 简谱 (jianpu) em texto

Usado em `faixa.jianpu("...")`, nos arquivos `.jp` e na linha de comando (`python3 -m huayin jianpu`).
Tokens separados por espaço; quebras de linha e barras são livres.

### Notas e durações

| escrita | significado |
|---|---|
| `1 2 3 4 5 6 7` | graus da escala maior a partir do tom (`1=D` → 1 = ré, 3 = fá#, 5 = lá) |
| `0` | pausa (aceita as mesmas durações: `0/`, `0.`) |
| `X` | golpe sem altura (percussão) |
| `1'` `1''` | uma / duas oitavas acima (os pontos em cima do número) |
| `1,` `1,,` | uma / duas oitavas abaixo (os pontos embaixo) |
| `#4` `b7` | sustenido / bemol (antes do número) |
| `5` | semínima = 1 tempo |
| `5/` `5//` `5///` | colcheia, semicolcheia, fusa (cada `/` = um traço embaixo do número) |
| `5.` `5..` | pontuada (×1,5), duplamente pontuada (×1,75) |
| `5 - - -` | cada `-` soma um tempo à nota anterior (5 vira semibreve) |
| `5~ 5` | ligadura de valor: soma as durações (mesma altura) |
| `1+3+5` | acorde (duração e técnica do último) |
| `<3 1 2 3 >` | quiáltera: 3 no tempo de 2 (`<5 … >` = 5 no tempo de 4, `<6 … >` = 6 no de 4) |
| `[56]1` | apojaturas (倚音): 5 e 6 rapidinhos ANTES do tempo do 1 |
| `\|` `\|\|` | barras (só para leitura) |

A oitava do `1` sem pontos é a da faixa (`oitava=4` por padrão; `oitava=3` para pipa/guzheng
graves, `5` para dizi). Mude no meio com `@oitava=5`.

### Técnicas

```
5{lun}                    técnica
3{tui:cents=300}          com parâmetros
3{tui:300}                primeiro parâmetro sem nome
6{tiao}{yin}              várias (em ordem)
1{guazou:ate=D6,tempo=0.6}
5{轮指}                    em chinês também
```

### Expressão

| escrita | significado |
|---|---|
| `!ppp !pp !p !mp !mf !f !ff !fff` | dinâmica a partir daqui |
| `!< … !f` | crescendo (as notas entre os dois sobem aos poucos) |
| `!> … !p` | diminuendo |
| `( 1 2 3 )` | legato: as notas de dentro não rearticulam (slide na corda, mesma arcada, mesmo sopro) |

### Diretivas

| escrita | efeito |
|---|---|
| `@tempo=96` | muda o andamento aqui (vale para a música toda) |
| `@rit` … `@tempo=60` | do `@rit` até o `@tempo` muda gradualmente (rit./accel.) |
| `@tom=1=G` | muda o tom (modulação) |
| `@oitava=5` | oitava do `1` sem pontos |
| `@vel=0.7` ou `@vel=mf` | dinâmica |
| `@tecnica=lun` | técnica padrão para as notas seguintes (`@tecnica=` desliga) |
| `@corda=2` | força a corda (`@corda=auto` volta ao automático) |
| `@dur=0.5` | duração base de um número sem traços (padrão 1 tempo) |

Comentários: `%` ou `//` até o fim da linha.

### Exemplo

```
% 散板 → 慢板
@tempo=50 !p [3]5 - 6/ 5/ 3 | (2 - 3 -) |
@rit 5 6 1' 2' @tempo=72
!mf 3'{huarou} - 2'/ 1'/ 6 | 5. 6/ 5 3 | <3 2 3 5 > 6 1'{fanyin} | 5 - - - ||
```

---

## 2. Arquivo `.jp`

```
% comentário
titulo: Noite no lago
autor: eu
tempo: 72
tom: 1=D
compasso: 4/4
la4: 440
temperamento: igual
reverb: jardim
nivel_reverb: 0.9
semente: 3

[faixa melodia: dizi]          % [faixa NOME: INSTRUMENTO]
volume_db: -2
pan: 0.2
reverb: 0.3
oitava: 5
humanizar: 8 0.06 2            % tempo_ms vel cents
membrana: 0.5                  % qualquer parâmetro do instrumento
5 6 1' 2' | 3'{vibrato} - - - |

[faixa base: guzheng]
oitava: 3
inicio: 4                      % começa no tempo 4
1{huazhi} - 5 - | 1 - - - |
```

Chaves de faixa especiais: `volume_db`, `pan`, `largura`, `reverb`, `tom`, `oitava`, `inicio`,
`humanizar`. O resto vai para o instrumento (`afinacao`, `material`, `vibrato`…).

---

## 3. Formato JSON (`m.salvar` / `Musica.carregar`)

Guarda tudo, inclusive curvas desenhadas à mão. Exemplo mínimo:

```json
{
  "titulo": "Exemplo", "tempo": 80, "tom": "1=D", "la4": 440, "temperamento": "igual",
  "reverb": "palacio_tang", "nivel_reverb": 1.0, "loudness": -16,
  "andamentos": [[16, 100, true]],
  "master": [["compressor", {"limiar_db": -20, "razao": 2}]],
  "faixas": [
    {
      "nome": "pipa", "instrumento": "pipa_tang", "params": {"afinacao": "pingdiao"},
      "volume_db": -2, "pan": -0.3, "largura": 1.0, "reverb": 0.25,
      "humanizar": {"tempo_ms": 8, "vel": 0.05, "cents": 2},
      "efeitos": [["eq", {"bandas": [["pico", 2500, 1.0, 2.0]]}]],
      "automacoes": [["pan", [[0, -0.6], [16, -0.1]], "linear"]],
      "notas": [
        {"t": 0, "dur": 1, "altura": "D3", "vel": 0.8, "tecnica": [["sao", {}]]},
        {"t": 1, "dur": 2, "altura": "A3", "vel": "mf", "tecnica": "tui:cents=200"},
        {"t": 3, "dur": 1, "altura": "B3", "legato": true},
        {"t": 4, "dur": 2, "altura": 62,
         "curva": {"pontos": [[0, -200, "degrau"], [0.2, 0, "suave"]],
                   "vibratos": [{"inicio": 0.4, "taxa": 5.5, "profundidade": 20}]}}
      ],
      "jianpu": "5 6 1' 6 | 5 - - - |", "inicio_jianpu": 8
    }
  ]
}
```

Campos de nota: `t`, `dur` (tempos), `altura` (nome, MIDI, Hz ou `null`), `vel` (0–1 ou dinâmica),
`tecnica` (texto, lista ou dict), `corda`, `legato`, `pan`, `params`, `curva`.
