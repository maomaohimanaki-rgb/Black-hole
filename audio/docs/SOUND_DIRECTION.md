# Direção de som: a gramática do Dooms Day (v0.4.0 do áudio)

> **Em uma frase:** a física diz o que **não pode** acontecer (as condições de contorno). A direção escolhe **como** acontece (a forma). O v0.3.2 tratava a física como roteiro, então a dilatação era uma rampa, que é bonita no papel e não dá impacto nenhum no ouvido.

Retorno do usuário que motivou este documento (25/10/2026): *"A dilatação está matematicamente e cientificamente coesa, só que muito linear. No ZA WARUDO não é só o tempo desacelerado: tem uma explosão inicial, o áudio se contorce, faz um monte de coisa, e aí para. O cérebro detecta 'caiu a velocidade, legal', mas não sente o impacto. A gente pode usar a ciência como gramática em vez de lei universal."*

Este documento é o **sistema de raciocínio**: o que o corpo precisa para sentir um golpe, como isso vira dado (`spec/dramaturgy.json`), quem aplica (`tools/synth/director.py`), quem confere (`tools/synth/psycho.py`) e como pensar um momento novo sem chutar.

---

## 1. O diagnóstico (medido, não opinião)

Medição do mixdown v0.3.2 com o `psycho.py` (loudness de 200 ms, bandas de 8ª ordem, força de ataque em 24 bandas críticas):

| Medida | Fusão (12 s) v0.3.2 | Fusão v0.4.0 | Horizonte (27 s) v0.3.2 | Horizonte v0.4.0 |
|---|---|---|---|---|
| Golpe acima do build | **−3,3 dB** (golpe mais BAIXO que o build) | +2,2 dB | **−1,1 dB** | +7,5 dB |
| Grave volta no golpe (sub no golpe − sub logo antes) | **−4,8 dB** (o grave SOME no golpe) | +18 dB | +2,9 dB | +52 dB |
| Celular ouve o golpe (150–600 Hz) | +6,5 dB | +10,8 dB | +0,0 dB | +13,5 dB |
| O golpe é o ataque mais nítido da vizinhança | não (0,82) | sim | não (0,49) | sim |
| Relógio do mundo | rampa linear 1,0 → 0,5, depois **outra** rampa 1,0 → 0,25 (salto para cima no 540) | — | — | soluços → inspiração 1,1 → despencada 0,2 → ricochete 0,74 → balanço 3,4 Hz → assíntota 0 |
| Respiração do filme (p97 − p10) | 12,1 dB | 14,2 dB | | |

**Leitura:** o v0.3.2 não tinha pouco efeito. Tinha **contraste zero**. O filme ficava num platô de −10 a −15 dB de 4 s a 30 s, o grave era constante do começo ao fim, e os dois "golpes" ficavam **abaixo** do que vinha antes. Pior: o morph do chirp fazia a frequência **descer** para 0,16× (≈ 40 Hz no tick 239). O maior riser natural da física murchava logo antes do drop, e ainda reprovava a ida e volta nos ticks 202 e 216.

A dilatação estava espalhada em **três rampas lineares independentes** (vento 1,0 → 0,5; trilha 1,0 → 0,25; horizonte 1,0 → 0,35), cada uma num stem, sem um relógio comum. O cérebro ouvia três fitas desacelerando, não o tempo parando.

---

## 2. Por que o corpo sente (ou não): os princípios

Cada princípio vira uma fase do vocabulário (§4) e uma medida do ouvido automático (§6).

**P1 · Contraste relativo.** Loudness e impacto são percebidos **em relação ao que veio antes**. Um golpe só existe se tiver espaço. Nos estudos empíricos sobre o "drop" da música eletrônica (Solberg; Solberg & Dibben 2019), o drop é a seção com maior resposta de condutância da pele, **depois** de um breakdown e de um build-up que tiram energia de propósito. → *fader de tensão* (o build começa abaixo do pico) e *master de golpe* (o golpe não é normalizado como uma cama).

**P2 · Expectativa: prenúncio, previsão, reação.** Na teoria ITPRA de Huron (*Sweet Anticipation*, 2006), parte do prazer vem de **prever certo**, e a reação a um evento forte é amplificada pela tensão da incerteza que o precede. Um motivo que aparece pequeno ("soluços" do tempo) ensina o cérebro o que esperar. Quando o grande vem, ele é reconhecido e maior do que o previsto. → fase `hiccup` (202 e 216 antes da fusão; 470, 500, 518 e 531 antes do horizonte, cada vez mais fundos).

**P3 · O vácuo.** Um som forte mascara o que vem logo depois (mascaramento para frente), e o sistema auditivo leva de dezenas a algumas centenas de ms para se recuperar. Um buraco curto antes do golpe deixa o ouvido "descansado" e cria o contraste de P1 no próprio instante. Todo trailer, todo drop e o ZA WARUDO fazem isso. → fase `vacuum` (90 ms na fusão, 80 ms no horizonte).

**P4 · Aproximação (looming).** Som que **sobe** de intensidade é percebido como mais forte e mais perto do que um som que desce na mesma medida (Neuhoff, *Nature* 1998, e trabalhos seguintes; vale também para macacos rhesus, o que sugere viés evolutivo). Antes do golpe, o mundo tem que **crescer**, não encolher. → fase `inhale`: ganho subindo, o mundo acelerando e subindo de tom (desvio para o azul de quem cai).

**P5 · O grave que volta.** No build-up, a música eletrônica tira o grave (filtro passa-alta) e o devolve no drop. O corpo sente a **volta** do grave mais do que o grave em si. → `inhale` com passa-alta subindo até 260/480 Hz; no golpe o grave volta de uma vez (sub do golpe + mundo inteiro).

**P6 · O golpe em camadas.** Um golpe de cinema não é um som: são várias camadas, cada uma cuidando de uma faixa e de um tempo. **Transiente** (0–20 ms, agudo: marca o instante), **corpo** (150–900 Hz: é o que o celular reproduz, P-48), **sub** (30–110 Hz: fone e TV) e **cauda** (a sala). No 540 ainda tem a **floração**: o "BOOM" chega 40–120 ms depois do "TÁ". → `impact()` em `recipes.py`.

**P7 · Princípios de animação aplicados a curvas.** Antecipação, impacto, *overshoot*, *follow-through* e acomodação (Thomas & Johnston, *The Illusion of Life*, 1981) valem para qualquer parâmetro que se move no tempo: taxa de reprodução, filtro, ganho, pan. Uma rampa linear não tem nenhum deles. A curva do relógio do mundo no 540 tem todos: acelera antes (antecipação), despenca a 0,2 (impacto), volta a 0,74 (overshoot), balança como mola amortecida (follow-through) e afunda assintótica (acomodação). **É isso o "o áudio se contorce".**

**P8 · Dois relógios.** Dilatação do tempo **é** a discordância entre dois relógios. Se tudo desacelera junto, não há referência e o ouvido só registra "ficou lento". No horizonte, o mundo (trilha, ritmo, vento, a cauda do golpe) segue o relógio do mundo, e o **coração** (552 · 566 · 584) continua seco, perto e no tom certo. É o ponto de audição de Chion (*Audio-Vision*): o som de dentro do corpo contra o mundo de fora. O disco arranhado bate nos ticks do stutter da câmera (1, 1, 2, 2, 3, 4, 6, 8), que é a *sincrese*: imagem e som segurando a pose juntos viram um evento só.

---

## 3. A gramática: o que a física obriga e o que a direção escolhe

| Fenômeno | A física obriga (contorno) | A direção escolhe (forma) |
|---|---|---|
| Chirp GW150914 | f ∝ τ^(−3/8), sobe até a fusão; fase igual à da órbita (T-05) | timbre, harmônicos, onde o grave some (o chirp não é tocado: é ele que **faz** o build) |
| Soluços antes dos eventos | nada (não é física, é prenúncio) | quando, quão fundo; **devolvem o tempo** (∫(taxa − 1) = 0), então a fase do chirp continua batendo com a órbita |
| Queda pelo horizonte | afinar e desacelerar **juntos** (desvio para o vermelho = taxa); tender a zero no horizonte; quem cai vê o lado de fora desviado para o azul | a curva: antecipação, despencada, ricochete, balanço, a velocidade da assíntota |
| Fusão | um evento único, seco no 240, depois o anel | vácuo, grave sugado e devolvido, camadas do golpe |
| O coração | (licença: o corpo de quem cai tem tempo próprio normal) | seco, perto, fora do relógio do mundo |

Regra prática: **se a física não proíbe e o corpo sente, pode.** Se a física proíbe (exemplo: o chirp descer antes da fusão), não pode, mesmo que soe bem, porque quebra a identidade.

---

## 4. A arquitetura

```
spec/audio_cues.json   QUANDO e QUANTO (o contrato com o storyboard)
spec/music.json        a trilha (v5)          ┐
music.py / organ.py    órgão, coral, relógio  ├─ os sons (receitas)
recipes.py / gw.py     os efeitos             ┘
spec/dramaturgy.json   a DIREÇÃO: papéis, fader de tensão, momentos em fases, master de golpe   ← v0.4.0
        │
render.py: receita → calibra → master → ida e volta (som cru × storyboard)
        → director.apply (som dirigido, no tempo absoluto do filme)          ← v0.4.0
        → mixdown → psycho.check (o mix funciona no corpo?)                 ← v0.4.0
        → falha o build se qualquer um reprovar
```

**Papéis** (`roles`): `world` (a trilha, o vento, o disco, o coral do 400) é o universo de fora, que o diretor encolhe, contorce e congela. `signal` (o chirp) só sofre os soluços e o fader de tensão, nunca o vácuo, porque ele é o riser. O resto é `event` ou corpo: a receita já nasce dirigida (o golpe do 540 usa o relógio do diretor por dentro, via `director.warp_from`).

**Por que no stem e não no mix:** o jogo toca cada stem separado. Toda operação do diretor é linear e variante no tempo (ganho, filtro, reamostragem, pente), então aplicar a mesma cadeia em cada stem do mundo é igual a aplicar no barramento do mundo. O jogo soa como o mixdown.

**O vocabulário de fases** (cada momento é uma lista delas):

| Fase | O que faz | Parâmetros |
|---|---|---|
| `hiccup` | soluço de tempo que devolve o tempo (prenúncio) | `ticks`, `depth`, `length_ticks` |
| `inhale` | o mundo cresce, perde o grave e (opcional) acelera | `from`, `to`, `highpass_hz [ini, fim]`, `gain_db [ini, fim]`, `rate_to` |
| `vacuum` | buraco antes do golpe (só o mundo) | `from`, `to`, `gain_db` |
| `release` | o mundo volta inteiro no golpe | `at` |
| `warp` | a contorção e a suspensão depois do golpe | `rate_keys` (PCHIP), `wobble {hz, depth, tau_s}`, `comb`, `lowpass_hz`, `highpass_hz`, `gain_db`, `impact_follow` |

**Master de golpe** (`master.impact_stems`): um golpe não se normaliza a −16 LUFS como uma cama de 30 s. Era isso que deixava a fusão 3 dB abaixo do build: o `volume` do jogo só abaixa, então quem tem que ser maior tem que nascer maior. O golpe vai com pico em −1 dBFS e densidade pela saturação dentro dele (`dense()`).

---

## 5. Como pensar um momento novo (o processo)

1. **O que o corpo tem que sentir?** Uma palavra: golpe, queda, alívio, suspensão, ameaça. Se não der para dizer em uma palavra, o momento não está claro.
2. **O que a física obriga?** Liste os contornos (§3). Isso é o que não se negocia.
3. **Qual é a referência?** Um momento conhecido que faz isso bem (ZA WARUDO, o drop, o BRAAAM). Decomponha em fases: o que acontece antes, no instante e depois.
4. **Escolha as fases do vocabulário** (§4). Se faltar uma, crie a fase no `director.py` com um porquê, nunca um ajuste solto numa receita.
5. **Orçamento de contraste:** quanto o golpe precisa estar acima do build (≥ 2 dB), quanto grave volta (≥ 12 dB), onde fica o vácuo. Se o build já está no teto, **abaixe o build** (fader de tensão). Não dá para subir o golpe acima de −1 dBFS.
6. **Escreva as medidas em `checks`** antes de renderizar. A meta vem primeiro, o ajuste depois.
7. **Renderize, meça, e só então ouça** no tablet e no celular. O `psycho.py` reprova o que é mensurável. O ouvido decide o resto.

---

## 6. O ouvido automático (`psycho.py`)

| Medida | Por quê | Meta (padrão) |
|---|---|---|
| golpe acima do build (loudness de 200 ms) | P1. 200 ms é a escala da integração de loudness para sons curtos; 400 ms engolia o próprio vácuo | ≥ +2 dB |
| grave volta no golpe | P5 | ≥ +12 dB |
| celular ouve o golpe (150–600 Hz) | P6 / P-48 | ≥ +2 dB sobre o p90 do build |
| ataque mais nítido da vizinhança (±1,5 s) | P3 + P6: o golpe tem que ser o instante mais marcado | = 1,0 |
| inspiração tira o grave | P5 | < 0 dB |
| antecipação / despencada / ricochete / balanço / assíntota | P7 (só no horizonte) | ≥ 1,04 · ≤ 0,35 · ≥ 0,25 · ≥ 3 extremos · ≤ 0,05 |
| respiração do filme (p97 − p10 da loudness) | o filme precisa de vale para ter pico | ≥ 14 dB |
| silêncio 600–619 | o melhor momento do filme | < −90 dBFS |

Saídas: `build/psycho_report.md` e `build/psycho.png` (loudness, bandas, ataques e o relógio do mundo, com os golpes marcados). Rodar sozinho: `python3 tools/synth/psycho.py [mix.wav]`.

**O que ele NÃO mede:** gosto, timbre, se o golpe soa "barato", se o balanço do relógio está rápido demais. Isso é o ouvido do usuário, no tablet e no celular.

---

## 7. Os dois momentos como ficaram

**M1 · Fusão (tick 240, 12,0 s)**
*(na v5 a fusão não tem mais soluços, ver §10)* `222–238` o grave é sugado (passa-alta 25 → 260 Hz) enquanto o chirp sobe sozinho e inteiro → `238,2–240` vácuo de 90 ms, só o último ciclo do chirp → `240` golpe em camadas (estalo + placa em Ré + braam + sub Ré2 → Lá0) com o mundo voltando inteiro → anel.

**M2 · Horizonte (tick 540, 27,0 s)**
`480, 510, 525` (v5: nos tempos fortes) soluços cada vez mais fundos → `524–538,4` inspiração: o mundo acelera para 1,1×, sobe de tom e perde o grave, a sala do próprio golpe cresce de trás pra frente e o riser corta → `538,4–540` vácuo de 80 ms → `540` TÁ (estalo) e BOOM no tick seguinte (floração) → `540–556` contorção (v5: o tutti é ouvido inteiro e só então o tempo cede): a taxa cai a 0,6, ricocheteia a 0,9 e balança a 3,4 Hz; a cauda do golpe vai junto a 70 % e o pente estica o espaço → `556–598` suspensão: o mundo afunda assintótico e escurece (passa-baixa até 180 Hz), a foto congelada e o disco arranhado nas poses da câmera, e o **coração seco** batendo fora do relógio → `600` zero digital.

---

## 8. Botões (se achar X no aparelho, mexa em Y)

Tudo em `spec/dramaturgy.json`, sem tocar em código:

| Se achar… | Mexa em |
|---|---|
| o golpe ainda fraco | baixe o build: `tension_db` (ex.: −8 → −10 antes do golpe) |
| o build ficou baixo demais no celular | suba `tension_db` no trecho e confira se o `psycho` continua passando |
| o vácuo curto/longo demais | `vacuum.from` (80–150 ms é a faixa usual; acima de 250 ms vira pausa) |
| o mundo "se contorce" pouco | `warp.wobble.depth` (0,22) e `rate_keys` (o 0,2 da despencada e o 0,74 do ricochete) |
| o balanço enjoativo ou rápido | `warp.wobble.hz` (3,4) e `tau_s` (0,55) |
| a cauda do golpe some cedo / dura demais | `warp.impact_follow` (0,7) e `warp.gain_db` |
| os soluços chamando atenção demais | `hiccup.depth` |
| o grave não "volta" | `inhale.highpass_hz` (o segundo número sobe) |

---

## 9. Próximos passos sugeridos

- Aplicar a mesma gramática ao **Ato I** (0–4 s, "mais ou menos" no retorno): o nascimento do ponto como um mini-golpe com vácuo.
- Aplicar ao **clarão do Ato VII** (700): o drop-out de 3 ticks já existe, mas não está medido pelo `psycho`. Basta declarar um momento M3 com `checks`.
- Reconciliar este pacote com o jogo (ver `docs/DECISIONS.md` no repositório: o pacote de áudio está em escala B e na v0.2.7 do spec).

## Fontes

- Huron, D. *Sweet Anticipation: Music and the Psychology of Expectation*. MIT Press, 2006 (teoria ITPRA).
- Solberg, R. T. "Waiting for the bass to drop" (2014); Solberg & Jensenius, *Empirical Musicology Review* (2017); Solberg & Dibben, *Music Perception* (2019): build-up, drop, prazer e condutância da pele.
- Neuhoff, J. G. "Perceptual bias for rising tones", *Nature* 395 (1998), e trabalhos seguintes sobre o viés de aproximação (looming).
- Chion, M. *Audio-Vision: Sound on Screen* (1994): sincrese, valor agregado, temporalização e ponto de audição.
- Thomas, F. & Johnston, O. *The Illusion of Life: Disney Animation* (1981): antecipação, overshoot, follow-through.
- Mascaramento para frente: a recuperação leva de dezenas a algumas centenas de ms (literatura de psicoacústica; ver p. ex. Jesteadt, Bacon & Lehman, JASA 1982).
- LIGO/Virgo, GW150914 (o chirp).

---

## 10. A trilha v5 (do zero, 25/10/2026)

Pedido do usuário: "zerar só a música, manter as ferramentas". Referência de **ofício** (não de notas): Interestelar. Nenhuma melodia copiada. Partitura em `spec/music.json`, instrumentos em `organ.py`, render em `music.py`.

**A música vem primeiro.** Grade de 80 BPM: 1 tempo = 15 ticks exatos, 1 compasso = 3 s. Os eventos do filme caem nos tempos fortes: fusão (240) = compasso 4, jatos (360) = 6, maré (420) = 7, horizonte (540) = 9, preto (600) = 10. O Ato VII tem grade própria, 60 BPM a partir do 620, e o clarão (700) cai no tempo 1 do compasso seguinte.

**O órgão e o 32' resultante.** Um órgão não tem dinâmica por nota: ela vem dos registros puxados (crescendo por soma) e da caixa expressiva (persiana: fechada = −20 dB e escura). O pedal toca 16' + 10⅔' (Ré 36,7 Hz + Lá 55 Hz, razão 2:3). A soma só se repete a cada 1/18,35 s, e o ouvido ouve um Ré0 que nenhum tubo toca (a fundamental fantasma). `check_organ.py` prova isso antes de todo render: periodicidade de **18,35 Hz** com só os dois tubos, e 18,34 Hz depois de cortar tudo abaixo de 150 Hz (o celular). Por baixo vai um 32' de verdade, baixinho, para fone e TV. Os tubos ficam como num órgão real: semitons pares de um lado, ímpares do outro, então o arpejo anda pelo estéreo sozinho.

**Forma (compasso a compasso):**

| Compasso (ticks) | O quê | Ofício de referência |
|---|---|---|
| 0 (0–60) | só o pedal de 32' nascendo; uma flauta no ponto (20) e a terça no gêmeo (40) | antes do tempo existir |
| 1–3 (60–240) | Rém → Si♭ → Solm → Fá/Lá → Lá7sus4 → Lá; o MESMO arpejo acelerando pela subdivisão (colcheia → tercina → semicolcheia → sextina), um registro a mais por compasso; o coral entra | o ostinato que só soma camadas (Cornfield Chase, No Time for Caution) |
| 4 (240) | tutti em **Si♭** (cadência de engano: esperava Ré): o espanto de nascer fora de casa | |
| 5–6 (300–420) | o arpejo volta em seis (gira como o disco) e acelera; no 360, tutti em **Fá** maior, o único momento heroico; no 390, calmaria em Rém9 (o mesmo acorde do sgx_pad) | a subida longa (Detach) |
| 7–8 (420–540) | o pedal vira pulso de palheta com Mi♭ (frígio, ameaça); o **relógio** entra, um tique por tempo, depois colcheias, depois semicolcheias; o arpejo só sobe; Lá7(♭9) | o tique de Mountains (o tempo de fora passando) e o pulso de Coward |
| 9 (540) | tutti em **Ré menor**, o primeiro em casa: o destino. O relógio continua regular no tempo do mundo, e é o relógio do diretor que espaça os tiques até parar | |
| Ato VII (620–760) | do zumbido nascem flautas no alto em Ré maior; o clarão (700) em Ré maior com 9ª, sem palhetas (luz sem violência) | quietude (The Wormhole) |

**A narrativa harmônica:** a fusão evita a tônica (Si♭), os jatos fogem para o maior (Fá) e o horizonte é a primeira vez que a música chega ao Ré com tudo. O buraco negro passa o filme inteiro puxando para o Ré, e no horizonte ele ganha.

**O que ficou das ferramentas:** o diretor (vácuo, grave sugado, contorção e congelamento, agora sobre a trilha nova), o ouvido automático, a ida e volta, o `act7` (ponto de audição do Ato VII) e os efeitos. **O que saiu:** `score.py`/`score.json` e `rhythm.py`/`rhythm.json` (a música antiga), os soluços da fusão (a grade já acelera por subdivisão) e o Risset de subida do Ato VII.

---

## 11. v5.1: a hierarquia e o material (o que estava errado no mix)

Retorno do usuário sobre a v5.0: *"a música sozinha ficou boa, tirando uns engasgos; o mix não parece a mesma música; os SFX matam; o fim parece toque de celular de 2010"*.

**Diagnóstico (medido):**
1. **Hierarquia invertida.** Cada efeito era normalizado a −16 LUFS, igual à trilha, e ficava 10–20 dB ACIMA dela: a maré +14, o horizonte +13, o chirp +9. No mix a música virava fundo dos efeitos, por isso parecia outra música.
2. **Material errado.** O fim (Hawking + clarão) era feito de senoides puras em sino, afinadas no pentatônico e quase secas. É exatamente a receita de um toque de celular. E todo onset de todo efeito ganhava um estalo mecânico de articulação.
3. **Engasgos na música.** Cada troca de acorde soltava os tubos antes do próximo, e o tubo grande leva até 0,2 s para falar (buraco de 8–11 dB acima de 150 Hz). Depois da fusão ficava um buraco de 1,7 s (a música só voltava no 300). E os soluços de tempo, numa música com grade, soam como a reprodução travando.

**Regras novas (valem para tudo daqui pra frente):**
- **A música é a referência do mix** (`dramaturgy.json → mix`, `render.automix`). Cada efeito de cama fica a `offsets_db` abaixo da trilha, no trecho em que toca. Só os golpes (fusão, jatos, horizonte) e o Ato I ficam livres, e o `psycho.py` cobra o espaço deles.
- **Efeito é feito do mesmo material da música.** Brilho = tubo de flauta curto, com o sopro do ataque (`pipe_ping`), nunca seno puro. Sino = tubo principal. Luz = ar. Tudo na mesma sala do órgão.
- **Articulação é ar, não clique.** A marca que a ida e volta usa para achar o instante virou um sopro curto (o chiff do tubo), a 30 % do pico local.
- **Legato de organista.** A nota comum entre dois acordes fica presa e as outras invadem a próxima em 60 ms (`music.legato`). Medido acima de 150 Hz, só restam os quatro cortes de propósito: os dois vácuos, o quase-silêncio do 268 e o drop-out do 697.
- **Medir onde o ouvido escuta.** Uma janela de 10 ms "vê" a onda do 32' (54 ms) subindo e descendo e acusa corte onde não há. Quem procurar engasgo mede acima de 150 Hz.
- **Mini-vácuo também vale no pequeno:** um brilho marcado precisa de ~75 ms sem nada da mesma banda antes dele (no Hawking, o enxame aleatório engolia o brilho do 696, para o ouvido e para o detector).
