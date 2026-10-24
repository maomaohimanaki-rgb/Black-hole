# MAGNETAR · SGR 1806-20 — o rival (evento 2)

**600 ticks · 30,0 s · 20 TPS.** Storyboard por blocos. O detalhamento tick a tick (keyframes de câmera, `spec/magnetar.json`, receitas de áudio) é a fase **F9** do roadmap, depois do buraco negro estar de pé, com o mesmo motor.

> **Logline.** Uma estrela de 20 km pesando mais que o Sol aparece sobre o seu mundo. Ela gira a cada 7,56 segundos e tem o campo magnético mais forte do universo: todo ferro em volta acorda, levanta e corre pelas linhas do campo. A crosta dela racha. Por **0,2 segundo** ela brilha mais que tudo, e a noite vira dia. Depois ela pulsa, o céu inteiro vira aurora e o ferro cai no chão desenhando o campo magnético, como limalha em volta de um ímã.

---

## 1. A física que vira cena (conferida)

| Fato | Valor | Onde aparece no filme |
|---|---|---|
| O que é | Estrela de nêutrons com o campo magnético mais forte que se conhece | o "ímã" que acorda o ferro |
| Tamanho e massa | ~20 km de diâmetro, ~1,4 massa solar | esfera minúscula e ofuscante (1,5 bloco) |
| Campo magnético | ~10¹⁵ gauss (SGR 1806-20: ~2×10¹⁵ G), cerca de mil trilhões de vezes o da Terra | HUD `B = 2×10¹⁵ G`; linhas de campo |
| Rotação | **7,56 s** = 151,2 ticks | pulsos da estrela e da cauda a cada 151 ticks |
| A erupção | 27/12/2004. Pico com subida em < 1,5 ms; por **~0,2 s** foi mais brilhante que a Lua cheia vista da Terra | **4 ticks** de branco total, com a noite virando dia |
| Energia | ~2×10⁴⁶ erg no pico, cem vezes as erupções gigantes anteriores | HUD |
| Distância | ~50 000 anos-luz (15 kpc) | HUD `50,000 ly` |
| Cauda | ~6 minutos pulsando no período de 7,56 s (~50 pulsos) | Ato IV: os pulsos e a legenda `+50 PULSES · 6 MIN` |
| Efeito na Terra | Ionizou a atmosfera do lado diurno **até ~20 km de altitude**. A 60 km, os elétrons livres subiram ~10⁶ vezes por alguns segundos, com efeito fraco por ~1 h | HUD `IONOSPHERE`; o céu inteiro em aurora |
| Gatilho | **Terremoto estelar**: a crosta racha sob o estresse do campo, e o campo se reconecta | Ato II: a crosta racha e as linhas torcem |

**Correção carinhosa da lenda:** a erupção não "quase destruiu" a Terra. Ela **ionizou a alta atmosfera** (a ionosfera) do lado iluminado por uns segundos, vinda de 50 000 anos-luz. É justamente isso que impressiona: um evento do outro lado da galáxia mexeu com o nosso céu em 0,2 s. O filme exagera de propósito (o magnetar está a 24 blocos, não a 50 000 anos-luz), e o HUD mostra os números reais.

Fontes: [Mereghetti et al., "Gamma Ray Observations of a Giant Flare from SGR 1806-20"](https://ar5iv.arxiv.org/html/astro-ph/0503030) · [Inan et al. / Stanford, ScienceDaily (2006)](https://www.sciencedaily.com/releases/2006/02/060221084628.htm) · [Massive disturbance of the daytime lower ionosphere (Inan et al. 2007)](https://vlfstanford.ku.edu.tr/?p=580)

---

## 2. Linguagem (o contrário do buraco negro)

O buraco negro é **atração que vira silêncio**. O magnetar é **repulsa que vira luz**.

| | Buraco negro | Magnetar |
|---|---|---|
| Cor | corpo negro, depois vermelho, depois preto | azul-elétrico `#5FD7FF`, magenta de campo `#FF4FD8`, branco absoluto |
| Letterbox | puxado até fechar | **abre** no clarão: 2,39 → 16:9 de uma vez no 300 (a tela explode para fora) |
| Destruição | uma cratera (o mundo é comido) | **o ferro é arrancado** e redesenhado; o resto do mundo fica |
| Momento-chave | 1 s de preto e silêncio | **0,2 s de branco**, com a noite virando dia (hora do jogo = meio-dia por 4 ticks) |
| Som | chirp (música da gravidade) | zumbido elétrico com pulso de rotação (151 ticks), estalos de crosta e um estalo de 4 ticks |

Mesma gramática de flash (N0–N4) e tremor do buraco negro.

---

## 3. Storyboard por blocos

**Geometria:** G = mira no chão, **M = G + 24 blocos** (centro da estrela). Eixo de rotação vertical; eixo magnético inclinado 35° (o campo "balança" a cada volta, como um farol). **Fase da rotação:** os pulsos caem em **38 · 189 · 340 · 491** (151 ticks entre eles = 7,56 s).

### ATO I — O ÍMÃ (0–119)

#### M01 · 0–29 · "A BÚSSOLA"
- **Câmera:** close no chão, rente: limalha de ferro (partículas cinza) tremendo sobre a terra.
- **Tela:** overlay de **bússola** no canto, com a agulha girando cada vez mais rápido. Legenda `MAGNETIC ANOMALY`.
- **Som:** zumbido de rede elétrica (60 Hz com harmônicos), subindo de volume.

#### M02 · 30–69 · "A ESTRELA"
- **Câmera:** tilt-up rápido até M.
- **VFX:** no 30, a estrela acende: um ponto **ofuscante** com halo azul-elétrico (impostor) que cresce até 1,5 bloco. Dois pontos quentes nos polos magnéticos. **Primeiro pulso no 38**: o feixe de um polo varre a câmera como um farol.
- **Tela:** HUD `NEUTRON STAR · Ø 20 km · 1.4 M☉`, `B = 2×10¹⁵ G`.
- **Som:** apito agudo e fino; pulso grave no 38. Flash N2 no 30, shake 2.

#### M03 · 70–119 · "AS LINHAS"
- **VFX:** as **linhas do campo** (laços de dipolo `r = L·sin²θ`, de 6 a 40 blocos) se desenrolam a partir dos polos e **giram com a estrela**. Tudo que é de **ferro** num raio de 32 acorda e desliza para as linhas: limalha, itens no chão, minério e blocos de ferro (se a destruição estiver ligada), trilhos, barras, bigornas, caldeirões, carrinhos e golens de ferro.
- **Tela:** HUD `P = 7.56 s`.
- **Câmera:** órbita lenta a 40 blocos.

### ATO II — TENSÃO (120–299)

#### M04 · 120–199 · "O ESTRESSE"
- **VFX:** as linhas **torcem** (giro helicoidal crescendo) e a crosta da estrela mostra rachaduras brilhantes (flipbook no impostor). **Rajadas precursoras** em **133 · 151 · 176 · 188 · 197**: micro-flashes de 2 ticks (os "soft gamma repeaters" soltam rajadas de ~0,1 s). Segundo pulso de rotação no 189.
- **Tela:** HUD `CRUST STRAIN 87 %`.
- **Som:** estalos metálicos de crosta, e um "tic" seco em cada rajada.
- **Câmera:** fecha de 40 para 22 blocos, com leve câmera na mão.

#### M05 · 200–269 · "TERREMOTO ESTELAR"
- **VFX:** as linhas se emaranham. Rachaduras no **chão** (decalques azuis) em anel. O ferro voando acelera.
- **Shake:** 3 → 7.
- **Tela:** HUD `STARQUAKE`.
- **Som:** ronco de sub com rangido de metal esticado (granular).

#### M06 · 270–299 · "O SEGUNDO ANTES"
- **VFX:** tudo **congela** de repente no 284: as linhas param e o ferro para no ar.
- **Câmera:** plano aberto a 60 blocos, travado.
- **Tela:** o HUD some.
- **Som:** silêncio de **284 a 299** (o oposto do buraco negro: o silêncio vem **antes**).

### ATO III — A ERUPÇÃO (300–339)

#### M07 · 300–303 · "0,2 SEGUNDO"
- **4 ticks de branco total** (N4) e, ao mesmo tempo, a **hora do jogo vai para meio-dia** (a noite vira dia: "mais brilhante que a Lua cheia").
- **Som:** estalo com subida instantânea, o som mais alto do addon.
- **Shake 10.** O letterbox **abre** de 2,39 para 16:9 nesses 4 ticks.

#### M08 · 304–339 · "A BOLA DE FOGO"
- **VFX:**
  - a hora volta para a noite no 304;
  - uma **bola de plasma** (casca aditiva branco-magenta) se expande de M;
  - as linhas do campo **arrebentam** em pedaços e se **reconectam** em laços novos;
  - uma onda de choque varre o chão e o ferro é soprado para fora.
- **Tela:** HUD `E ≈ 2×10⁴⁶ erg IN 0.2 s` e legenda `BRIGHTER THAN THE FULL MOON · FROM 50,000 ly`.
- **Som:** rugido largo com cauda de chiado.

### ATO IV — A CAUDA (340–539)

#### M09 · 340–419 · "A PULSAÇÃO"
- **VFX:** **pulso de cauda no 340**: a estrela respira, inchando e brilhando no período de rotação, com o feixe varrendo.
- **Câmera:** sobe devagar até as nuvens (Y 192).
- **Tela:** legenda `TAIL · 50 PULSES · 6 MIN`.
- **Som:** zumbido pulsado, com AM no período de 151 ticks.

#### M10 · 420–499 · "IONOSFERA"
- **VFX:** acima das nuvens, o **céu inteiro** acende em cortinas de aurora (verde, violeta e magenta) de horizonte a horizonte. **Pulso no 491**: a aurora pisca junto.
- **Tela:** HUD `IONOSPHERE · e⁻ ×10⁶ @ 60 km` e `IONIZED DOWN TO 20 km`.
- **Som:** pad etéreo com estalos de rádio (VLF: "whistlers", chiados descendo).

#### M11 · 500–539 · "LIMALHA"
- **Câmera:** desce para um **top-down** a 50 blocos.
- **VFX:** o ferro cai e **assenta no chão desenhando o campo magnético**, como a limalha em volta de um ímã na aula de ciências. São decalques de linhas de ferro mais os detritos pousados.
- **Destruição (opcional):** ficam os buracos de onde o minério saiu, mais algumas pepitas reais (`raw_iron`) espalhadas ao longo das linhas.
- **Som:** chuva fina de metal.

### ATO V — ECO (540–599)

#### M12 · 540–599 · "O FAROL"
- **VFX:** a estrela encolhe e esmaece até ser um ponto que gira e pisca fraco no período de rotação (o próximo pulso, 642, já fica fora do filme).
- **Tela:** título 556–592, `MAGNETAR · SGR 1806-20`, e abaixo `磁星`. Fim.
- **Som:** um último pulso grave distante.

---

## 4. Continuidade

| Elemento | Regra |
|---|---|
| Pulsos de rotação | 38 · 189 · 340 · 491 (151 ticks = 7,56 s). Nunca outro período. |
| Branco total | **Só** 300–303 (4 ticks = 0,2 s). |
| Hora do jogo | noite fixa, exceto 300–303 (meio-dia) |
| Silêncio | 284–299 (antes do clarão) |
| Shake 10 | só no 300 |
| Letterbox | 16:9 (0–29) → 2,39 (30–299) → **abre** no 300 → 16:9 até o fim |
| Ferro | só materiais de ferro reagem (lista em `field_math.js`); o resto do mundo nunca se mexe |

---

## 5. Técnica (reaproveita o motor do buraco negro)

| Elemento | Técnica |
|---|---|
| Estrela | impostor `lookat_xyz` (halo, polos quentes e rachaduras em flipbook) |
| Feixe do farol | `lookat_direction` com a direção do eixo magnético girando, persistente |
| Linhas de campo | cadeias de segmentos `lookat_direction` em laços de dipolo, persistentes. A rotação a cada 151 ticks é feita **no cliente** (o laço inteiro é um emissor com N segmentos que calculam a posição pelo índice e pelo tempo). Teste novo **S-11** na F9. |
| Ferro voando | a mesma entidade de detrito do buraco negro (`sgx_debris`), com textura de ferro e caminho ao longo do laço (fórmula no Molang) |
| Branco de 0,2 s | overlay de UI (o `camera.fade` tem piso de 0,35 s, P-08) + `world.setTimeOfDay` 6000 por 4 ticks e volta |
| Aurora no céu | cortinas de partícula `lookat_y` gigantes acima das nuvens, persistentes, cor animada no Molang |
| Limalha no chão | decalques `direction_z` (0, 1, 0,02) com textura de linhas de campo assada pelo Python para o tamanho do raio |
| Destruição | busca de blocos de ferro com `containsBlock` em busca binária (P-37), troca por ar via fila de blocos, devolução de alguns `raw_iron` |

---

## 6. Perguntas em aberto (vão para `docs/DECISIONS.md`)
- **D-11 · Ferro do jogador:** a armadura de ferro do jogador e dos outros também é puxada? Proposta: só visualmente (partículas), nunca tirar item de ninguém.
- **D-12 · Redstone:** piscar lâmpadas de redstone no clarão seria lindo, mas mexe na máquina dos outros. Proposta: não mexer.
- **D-13 · Duelo:** um terceiro evento "magnetar caindo no buraco negro", depois dos dois prontos.
