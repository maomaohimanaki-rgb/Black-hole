# SINGULARITY — Storyboard do buraco negro

**Buraco negro** · 720 ticks · 36,0 s · 20 TPS (+ 20 ticks de saída)
*Direção + supervisão de VFX e de som. Nome do addon provisório: ver `docs/DECISIONS.md`, D-01.*

> **Logline.** Dois pontos de nada aparecem sobre o seu mundo, começam a dançar e a cantar o chirp que o LIGO ouviu em 2015. Eles viram um só. O buraco negro acende um disco, dispara dois jatos e come o chão. A câmera cai junto com um pedaço de terra, atravessa o horizonte e o filme fica preto e mudo por um segundo. Do lado de fora sobra uma cratera perfeita e um buraco negro que evapora numa última luz.

**Quem manda em quê:** `spec/storyboard.json` manda no **tempo** (ticks, keyframes, onsets) e este documento manda na **direção** (o que a imagem e o som querem dizer). Se os dois discordarem, o JSON vence no tempo e este texto vence na intenção, e a divergência vira nota em `docs/DECISIONS.md`. A tabela de beats (`docs/BEAT_TABLE.md`) é gerada do JSON por `tools/check_spec.py`.

Este é o **primeiro dos dois eventos** do addon. O segundo, o rival, é o **magnetar** (`docs/MAGNETAR.md`).

---

## 0. O storyboard vem antes do som

Não existe áudio pronto: **este storyboard vem primeiro**, e o áudio é **sintetizado em Python a partir dele** (`docs/AUDIO_DESIGN.md`):

```
storyboard (este doc + spec/storyboard.json + spec/audio_cues.json)
   → sintetizador Python → .ogg + build/timeline.json
   → analisador re-detecta os onsets e confere com o pedido (±0,5 tick), senão o build falha
   → motor do jogo (relógio mestre, câmera, árbitro — docs/ARCHITECTURE.md)
```

A vantagem é que o som e a imagem saem da **mesma matemática**. A fase da órbita dos dois buracos negros é uma fórmula só (`spec/layout.json → binary`). O sintetizador gera o chirp com ela e o cliente do jogo anima a órbita com ela (Molang). Os dois ficam sincronizados por construção, não por ajuste fino.

---

## 1. Regras de tradução (som → imagem)

Os dois eventos do addon (buraco negro e magnetar) usam a mesma "gramática" de flash e tremor.

### Intensidade (`rms_norm` do onset)

| rms_norm | Nível | O que a tela faz |
|---|---|---|
| 0,00–0,25 | **N0 Sussurro** | Sem flash. Shake 0. |
| 0,25–0,50 | **N1 Brilho** | Bloom suave, +0,5 EV. Shake ≤ 1. |
| 0,50–0,75 | **N2 Pulso** | Halo, +1 EV. Shake ≤ 3. |
| 0,75–0,90 | **N3 Flash** | Flash cheio de 2–3 ticks, +2 EV. Shake ≤ 6. |
| 0,90–1,00 | **N4 Detonação** | White-out ou impacto de 1–2 ticks, +4 EV. Shake 10 (exceto o clarão final). |

### Cor

O disco segue a **cor de corpo negro**: o som "quente" (centroide alto) é a luz mais quente, que é azul-branca, e não vermelha. Isso inverte a intuição comum ("vermelho = quente") de propósito, porque aqui a física manda.

| Centroide | Cor | Onde |
|---|---|---|
| < 1 kHz | laranja-escuro `#FF6A1E` (2 000 K) | anel externo, brasa |
| 1–2,5 kHz | âmbar `#FFB46B` (4 000 K) | meio do disco |
| 2,5–5 kHz | branco quente `#FFF4EA` (6 500 K) | anel interno |
| > 5 kHz | branco-azulado `#DCE4FF` (9 000 K) | borda interna, lado que se aproxima |
| > 7 kHz isolado | branco-gelo `#E8FBFF` | brilhos de lente, Hawking |

Fora do disco: as ondas gravitacionais são **prata** `#D8E2F0`, os jatos **violeta-azul** `#8FA8FF` e a queda é o **desvio para o vermelho** (overlay `#FF7A3D → #2A0000`). Paleta completa em `spec/palette.json`.

### Linguagem de cinema
- **Câmera "on ones"** (1 pose por tick, com ease linear de 1 tick). Spline nativa só como opção experimental.
- **Letterbox como gravidade.** As barras não só fecham: elas são **puxadas**: 16:9 → 2,39 (o par se forma) → rebote na fusão → apertam até 3,2 na queda → **se encontram** no horizonte (preto) → abrem de uma vez para 16:9 do lado de fora.
- **O preto é personagem.** O buraco negro é a única coisa do filme que é preta de verdade (`#000000`). Nada mais na tela pode chegar a preto absoluto antes do 590.
- **Impacto ao contrário.** O único impact frame é **negativo**: no tick 240 o buraco negro fica BRANCO e o mundo preto por 2 ticks.
- **Tipografia:** IBM Plex Mono SemiBold (HUD) e Poppins SemiBold (título). `黑洞` em Noto Sans CJK Thin. Atenção: `☉`, `⁷`, `⁹`, `→` e `∞` precisam de fonte de apoio (ver PITFALLS P-25).

---

## 2. Mapa de atos

| Ato | Ticks | Segundos | Energia | Cor | Sensação |
|---|---|---|---|---|---|
| I Anomalia | 0–79 | 0,0–4,0 | quase nada → pings | noite fria | Algo errado e invisível |
| II Inspiral | 80–239 | 4,0–12,0 | 0,3 → 1,0 (chirp) | noite + prata | Hipnose que acelera |
| III Fusão | 240–279 | 12,0–14,0 | 1,0 → silêncio | branco-negativo → prata | Clímax e respiração |
| IV Disco | 280–419 | 14,0–21,0 | 0,5 → 1,0 → 0,6 | corpo negro → violeta | Beleza perigosa |
| V O Puxão | 420–539 | 21,0–27,0 | 0,6 → 1,0 | âmbar → vermelho | Fome, queda |
| VI Horizonte | 540–619 | 27,0–31,0 | 0,8 → **0** | vermelho → **preto** | Tempo parando |
| VII Evaporação | 620–719 | 31,0–36,0 | 0,3 → 1,0 (luz) | branco-gelo | Perdão |

**Regra emocional:** a primeira metade é **a gravidade como música** (a dança, o chirp, a fusão). A segunda é **a gravidade como fome** (o disco, os jatos, o chão subindo, a queda). O horizonte é **silêncio** e a evaporação é **luz sem violência**.

---

## 3. Geometria de cena (resumo de `spec/layout.json`)

> **v0.2.4 (T-18): escala B.** Os números abaixo são os do kit. Hoje toda distância da cena é ×3,5 (sombra ~7 blocos, disco de 84 de diâmetro, O = G + 49), a cratera tem raio 45 e a mira fica a 60–160 blocos. A fonte é `spec/layout.json`.

- **G** é o bloco mirado (chão) e **O = G + 14 blocos para cima** é o centro do buraco negro.
- A mira precisa estar a **40–128 blocos** do jogador. O corpo dele fica onde está e a cratera tem raio 30.
- **O par:** A tem 36 M☉ (sombra de 1,21 bloco) e B tem 29 M☉ (0,97). Eles giram no plano horizontal em volta de O, no sentido anti-horário visto de cima. A distância vai de 8,0 (tick 60) a 2,18 (tick 239), quando as sombras se tocam.
- **O buraco final** tem 62 M☉ e sombra de 2,08 blocos. O disco vai de 2,4 a 12 blocos em 5 anéis keplerianos (o interno gira mais rápido). Os jatos sobem 180 blocos e descem até o fundo da cratera.
- **A cratera** é uma esfera de raio 30 centrada em G + 2: uma bacia de ~60 blocos de largura e ~28 de fundo, com vidro escuro e obsidiana chorosa. Só a borda brilha.

Os números do chirp são reais (GW150914: 36 + 29 → 62 M☉, 3 M☉ irradiados, spin final 0,67). Os tamanhos são artísticos.

---

## 4. Storyboard por blocos

### ATO I — ANOMALIA

#### B01 · Ticks 0–19 · 0,00–0,95 s · "O SILÊNCIO ERRADO"
**Áudio:** `sgx_void_in`, um *swell* invertido (o ar sendo sugado). Onsets 0 (0,2) · **12 (0,7, queda de sub)** · 19 (0,35, corte quase a zero).
- **Câmera:** rente ao chão (0,6 bloco), 10 blocos antes de G, FOV 50, olhando para o ar acima da mira. Avança 2 blocos e inclina devagar para cima.
- **VFX:** poeira, pólen e pétalas **derivam devagar para um ponto vazio** 14 blocos acima do chão. No 12, junto com o sub, as partículas de grama inclinam todas para lá.
- **Cor:** noite fria, nada brilha.
- **Tela:** 16:9. HUD `ANOMALY DETECTED` (legenda) e `GRAV. GRADIENT +0.003 g`.

#### B02 · Ticks 20–39 · 1,00–1,95 s · "O PONTO"
**Áudio:** `sgx_point`: um brilho de sino inarmônico com um soco de sub. Onsets **20 (1,0)** · 24 · 28 · 32 (pings 0,5 → 0,35).
- **Câmera:** grua para trás e para cima (outCubic). Termina 14 blocos atrás, 3 à direita e 6 acima, FOV 42, fechando no ponto.
- **VFX:** no 20 nasce **A**, um ponto de **preto absoluto** menor que um pixel, com um fio de anel de fótons. Do 26 ao 38 ele cresce até o tamanho final (outExpo). Em cada ping, um **brilho de lente** (estrela de 4 pontas fina) corre pelo anel. A poeira acelera.
- **Flash:** N2 *negativo micro* no 20: por 1 tick, só a região do ponto inverte.
- **Tela:** `SINGULARITY · A` · `MASS 36 M☉`.

#### B03 · Ticks 40–59 · 2,00–2,95 s · "O GÊMEO"
**Áudio:** `sgx_twin`, a mesma receita um tom abaixo. Onsets **40 (1,0)** · 44 · 48.
- **Câmera:** whip-pan de 2 ticks (40 → 42) para revelar **B** do outro lado. Depois, órbita lenta para a direita a 16 blocos, elevação 15°, FOV 55.
- **VFX:** B nasce no 40 e cresce de 46 a 56. **No 48 os dois começam a girar** com a fórmula de `layout.binary`, que roda no cliente. No 50 a poeira forma uma espiral de **dois braços**.
- **Tela:** **as barras começam a fechar no 48** (16:9 → 2,39 até o 79): o enquadramento está sendo puxado. HUD `SECOND BODY · 29 M☉`, legenda `BINARY LOCKED`.

#### B04 · Ticks 60–79 · 3,00–3,95 s · "A DANÇA COMEÇA"
**Áudio:** **começa o `sgx_chirp`**: a onda gravitacional de verdade, 35 Hz, grave a ponto de ser mais sentida que ouvida. A primeira meia-órbita marcada é o 74.
- **Câmera:** grua sobe de 15° para 50° de elevação e gira 20°. Mostra a dança de cima.
- **VFX:** **primeira ondulação no chão** no 74. É um anel prateado que se expande sob o par, e uma ondulação nasce a cada meia-órbita (19 no total, até o 236).
- **Tela:** `INSPIRAL · f 35 Hz · d 8.0`.

### ATO II — INSPIRAL (`sgx_chirp`, 9 s)

**Como o chirp funciona (vale para os 3 blocos):** a frequência segue `f(t) = 35·(τ/9 s)^(−3/8)` com `τ = (240 − t)/20`. Ela quase não muda por 6 segundos (35 → 61 Hz) e dispara nos últimos 2 (61 → 245 Hz). É assim no LIGO, e é por isso que funciona como drama: a tensão do Ato II vem do **ritmo** (as meias-órbitas encurtando: 13 → 12 → 10 → 7 → 4 ticks), não da altura do som.

#### B05 · Ticks 80–139 · 4,00–6,95 s · "ESPIRAL"
**Áudio:** chirp de 37 a 41 Hz. Acentos nas meias-órbitas **87 · 99 · 112 · 124 · 135** (rms 0,32 → 0,40).
- **Câmera:** órbita **contrária** ao par (de +40° para −60°), descendo de 50° para 25°, de 22 para 16 blocos. O par parece mais rápido do que é.
- **VFX:** ondulações nos acentos. Cada corpo carrega um **disquinho de poeira** (impostor pequeno). No 90, folhas e pétalas sobem em funil por baixo do par.
- **Tela:** HUD atualiza `f 37 Hz · d 7.8` → `f 39 Hz · d 7.5` → `f 41 Hz · d 7.2`.

#### B06 · Ticks 140–199 · 7,00–9,95 s · "ACELERAÇÃO"
**Áudio:** chirp de 44 a 60 Hz. Acentos **146 · 156 · 166 · 176 · 185 · 194**.
- **Câmera:** desce até o **plano da órbita** (elevação 6°), a 12 blocos, FOV 58 → 66, com leve câmera na mão. Os corpos passam rente à lente.
- **VFX:** **brilhos de eclipse**: quando um corpo passa na frente do outro visto da câmera (calculado pela fase e pela pose), o anel de trás se deforma em arco e brilha (N1). A espiral de poeira aperta.
- **Tela:** `f 44 Hz · d 6.9` → `f 50 Hz · d 6.3`.

#### B07 · Ticks 200–239 · 10,00–11,95 s · "O GRITO"
**Áudio:** o chirp **sobe de verdade**: 62 → 103 → 146 → **245 Hz**. Acentos **202 · 209 · 216 · 222 · 227 · 232 · 236 · 239** (0,67 → 1,0). A partir do 232 entra o *pré-roll* invertido do `sgx_merge`.
- **Câmera:** **8 snap-zooms** secos nos acentos. Cada um fecha 3° de FOV e aproxima ~0,9 bloco, girando 4°. O último (239) fica a 6 blocos, FOV 42, colado nos dois corpos.
- **VFX:** no 220, os dois anéis de fótons se deformam num **8**. No 230, a espiral de poeira vira **uma lâmina**.
- **Flash:** N1 branco-gelo em cada snap. **Shake:** 3 → 4 → 5 → 6.
- **Tela:** HUD corre: `f 62 Hz · d 5.5`, `f 103 Hz · d 3.9`, `f 146 Hz · d 3.1`, `f 245 Hz`.

### ATO III — FUSÃO

#### B08 · Ticks 240–259 · 12,00–12,95 s · "FUSÃO / RINGDOWN"
**Áudio:** `sgx_merge` com pico **exato no 240** + `sgx_ringdown` a partir do 241 (senoide amortecida de 250 Hz com τ de 0,6 s, um "sino" se apagando).
- **Câmera:** **impact frame negativo de 2 ticks** (240–241), com o buraco negro **branco** num mundo **preto**. **Corte seco no 242** para o plano aberto a 40 blocos. Quando a onda passa pela câmera (247), **o FOV respira**: 76 → 66 → 73 → 68 → 70 até o 259 (as polarizações + e × de uma onda gravitacional esticando o espaço).
- **VFX:** A + B viram um só (sombra 2,08). **Ringdown visível:** a sombra pulsa (`1 + 0,15·e^(−Δt/10)·sin(2π·Δt/12)`). **Casca da onda gravitacional:** uma esfera de ar "tremido" e um anel prateado no chão saem a 6 blocos/tick. Folhas e poeira são empurradas quando ela passa.
- **Flash:** N4 negativo no 240 e N3 branco no 242. **Shake: 10 no 241**, 6 no 247 (a onda chega) e 3 no 250.
- **Tela:** rebote das barras (2,39 → 2,7 → 2,39 entre 240 e 246). Legenda `THEY BECAME ONE`, HUD `MERGER · 62 M☉` e depois `ΔM = 3.0 M☉ → GRAVITATIONAL WAVES`.

#### B09 · Ticks 260–279 · 13,00–13,95 s · "O VAZIO RESPIRA"
**Áudio:** cauda do ringdown. **Do 268 ao 279 é quase-silêncio** (rms < 0,05).
- **Câmera:** empurrão lento de 39 para 26 blocos, FOV 70 → 64.
- **VFX:** a poeira **cai de volta**. Sobra um buraco negro sozinho com o anel fino. No 272, as primeiras faíscas de matéria começam a orbitar.
- **Tela:** HUD dissolve (some no 262). Shake 0.

### ATO IV — DISCO

#### B10 · Ticks 280–309 · 14,00–15,45 s · "IGNIÇÃO DO DISCO"
**Áudio:** `sgx_disk_ignite`, um rugido subindo (ruído marrom com banda varrendo 300 → 4 000 Hz). Um "whoomp" por anel: **280 · 286 · 292 · 298 · 304** (0,5 → 1,0). O centroide sobe junto com a cor.
- **Câmera:** grua em volta, de 26 para 20 blocos, subindo para 12° e girando 60°.
- **VFX:** **5 fluxos de matéria** sobem do chão em espiral até o plano do disco (poeira e detritos com textura do bioma). Os anéis acendem **de fora para dentro**: o 5 (laranja-escuro) no 280 e o 1 (branco-azulado) no 304.
- **Flash:** N3 no 304 (o anel interno). **Shake:** 2 → 3 → 4.
- **Tela:** `ACCRETION` · `T 10⁷ K`.

#### B11 · Ticks 310–349 · 15,50–17,45 s · "O ANEL" (o plano-herói)
**Áudio:** `sgx_disk_loop`, rugido estável com **Doppler** (modulação de 1 Hz e pan L↔R em fase, só no mix 2D da cutscene).
- **Câmera:** o disco **quase de lado** (elevação ~10°). Empurrão lento de 20 para 14 blocos, FOV 60 → 52. **Shake 0.** É o plano que todo mundo vai printar.
- **VFX:** o **impostor** mostra o que o Interstellar mostrou: o lado de trás do disco aparece **dobrado por cima e por baixo da sombra** (lente gravitacional), com o anel de fótons nítido. **Doppler:** o lado que vem na direção da câmera (esquerda) fica **azul-branco e forte**, e o que se afasta (direita) **laranja e fraco**. Em volta, um **anel de Einstein** com as estrelas reais da NASA. A turbulência do disco gira mais rápido por dentro.
- **Tela:** `SPIN a* = 0.67` · `ISCO 3 r_s`.

#### B12 · Ticks 350–389 · 17,50–19,45 s · "JATOS"
**Áudio:** `sgx_jet`: assobio de pré-carga 358–359, **explosão no 360 (1,0)**, um segundo golpe no 362 (0,7) e zumbido de síncrotron (dente-de-serra filtrado) decaindo até o 400.
- **Câmera:** 350–359 ainda no plano-herói. **Corte no 360** para contra-plongée a partir do chão (30 blocos, elevação −10°). Ela segue o jato de cima até as nuvens (pitch −80° no 380) e depois desce para mostrar o **jato de baixo furando o chão** (389).
- **VFX:** os polos acendem 2 ticks antes. Saem dois jatos (`lookat_y`) com núcleo branco-lilás, bainha violeta-azul e **nós de plasma** subindo a 8 blocos/tick. No chão, um brilho onde o jato de baixo bate.
- **Destruição:** **poço de raio 3 e 28 de fundo em G**, escondido pelo flash N4 do 360.
- **Flash:** N4 no 360 e N3 no 361. **Shake: 10 no 360**, depois 6 e 3.
- **Tela:** `RELATIVISTIC JETS` · `v = 0.99 c`.

#### B13 · Ticks 390–419 · 19,50–20,95 s · "O OLHO DO MUNDO"
**Áudio:** o zumbido do jato decai. O disco continua e um **coral grave sintetizado** (`sgx_pad`) entra no 400.
- **Câmera:** plano geral a 60 blocos, grua subindo. O buraco negro como um olho sobre a paisagem.
- **VFX:** decalques no chão com a cor do disco (a paisagem "iluminada" por ele). Os jatos afinam e somem entre 400 e 419.
- **Tela:** sem HUD. Shake 1 (ronco).

### ATO V — O PUXÃO

#### B14 · Ticks 420–459 · 21,00–22,95 s · "MARÉ"
**Áudio:** `sgx_tidal`: estalos de madeira e pedra esticados, sobre um ronco de sub. **420 · 430 · 438 · 446 · 452 · 457** (0,6 → 1,0, acelerando).
- **Câmera:** **corte** para rente ao chão, a 34 blocos, olhando para cima *através do terreno* (elevação −8°). Avança devagar.
- **VFX:** **o mundo cai para cima.** Blocos do próprio terreno (texturas do bioma: grama, terra, pedra, tronco, folhas, areia) sobem em espiral e **esticam**, com até 48 detritos vivos. O chão ondula para cima.
- **Destruição:** a cratera é cortada de cima para baixo em 4 fatias (422, 432, 440, 448), **escondida pela poeira e pelos detritos**. O resto vai no preto (B19) e depois do filme.
- **Flash:** N1, N1 e N2 nos três últimos estalos. **Shake:** 3 → 8.
- **Tela:** `TIDAL FORCES` · `STRAIN 10⁹ g`.

#### B15 · Ticks 460–499 · 23,00–24,95 s · "ESPAGUETE"
**Áudio:** `sgx_fall`, vento subindo com a velocidade.
- **Câmera:** **smash-cut** para trás de um **bloco de grama** (o "pedaço-herói"), que sai de G + 12 à direita e vai em espiral até o disco. A câmera vai 3 blocos atrás e 1 acima, com FOV 66 → 90.
- **VFX:** o pedaço **estica** (até ×6 no comprimento e ×0,3 na largura) conforme se aproxima. Linhas de velocidade, detritos riscando. O disco vai enchendo o quadro.
- **Tela:** as barras **apertam** (2,39 → 2,8). HUD `r = 6 r_s` → `r = 3 r_s` → `r = 1.5 r_s · PHOTON SPHERE`.

#### B16 · Ticks 500–539 · 25,00–26,95 s · "A QUEDA"
**Áudio:** **whoosh Doppler no 500** (cruzando o disco). A partir do 510 **o tempo amolece**: a reprodução desacelera de 1,0 para 0,5, e o som afina e arrasta.
- **Câmera:** cruza o plano do disco no 500 (clarão N3) e **mergulha** para a sombra. FOV 90 → 120: o anel de fótons vira **um círculo gigante** em volta do quadro.
- **VFX:** o universo de fora **comprime num anel** atrás da câmera (overlay assado: aberração relativística). No 520 o pedaço vira **um fio** e depois luz. **Desvio para o vermelho** começa (0 → 0,5).
- **Tela:** as barras apertam até 3,2. HUD `r → r_s` e `z = 9.0`. **Shake:** 7 → 5 → 3 (o tremor também desacelera).

### ATO VI — HORIZONTE

#### B17 · Ticks 540–579 · 27,00–28,95 s · "O ÚLTIMO OLHAR"
**Áudio:** `sgx_horizon`. A "mistura" inteira desacelera como fita parando (0,5 → 0,05) e batidas de sub com intervalos crescentes fazem de coração: **540 · 552 · 566 · 584**.
- **Câmera:** **dilatação temporal na imagem**: a pose segura cada vez mais (1, 1, 2, 2, 3, 4, 6, 8 ticks). A câmera chega a 2,5 blocos da sombra, que ocupa ~70 % do quadro.
- **VFX:** tudo fica vermelho (0,5 → 0,95). O anel do universo de fora encolhe para uma linha fina na borda.
- **Tela:** `t → ∞`, depois `SIGNAL LOST` com HUD tremendo (HT 3).

#### B18 · Ticks 580–599 · 29,00–29,95 s · "CRUZAMENTO"
**Áudio:** última batida no 584. De 590 a 599, só um sub sumindo até **zero digital exato no 600**.
- **Câmera:** congelada (segura 8 ticks) e um último empurrão.
- **VFX:** **as barras se encontram** no 590, junto com uma íris circular. Sobra **um ponto de luz no centro**, o último fóton, que encolhe até o 599.

#### B19 · Ticks 600–619 · 30,00–30,95 s · "SILÊNCIO ABSOLUTO"
**Áudio:** **nada.** Nenhum som de cutscene pode estar ativo (o `check_spec.py` falha se tiver).
- **Tela:** preto puro, 1 segundo. É o melhor momento do filme.
- **Por baixo do preto** (o engasgo cai onde não se vê): a câmera teleporta para fora, os detritos somem, nasce o buraco negro remanescente (escala 0,6) e o brilho da borda da cratera. A **fila de destruição ganha 25 ms por tick** e corta o grosso da cratera.

### ATO VII — EVAPORAÇÃO

#### B20 · Ticks 620–659 · 31,00–32,95 s · "DE FORA"
**Áudio:** `sgx_hawking`, um ambiente quase inaudível com brilhos agudos esparsos (6–14 kHz).
- **Câmera:** fade-in do preto (620–632). Plano aberto a 70 blocos, elevação 35°, descendo devagar.
- **VFX:** do lado de fora o tempo é normal: **uma cratera perfeita** com borda brilhando e um **buraco negro pequeno** pairando, com o resto do disco apagado. Faíscas de Hawking saem dele, poucas.
- **Tela:** **as barras abrem para 16:9 entre 620 e 630** (a respiração). **Sem HUD** daqui até o título.

#### B21 · Ticks 660–699 · 33,00–34,95 s · "HAWKING"
**Áudio:** brilhos cada vez mais densos e um tom puro subindo (2 → 8 kHz, muito baixo). Cintilações em **660 · 672 · 682 · 690 · 696 · 699** (0,3 → 0,9).
- **Câmera:** empurrão lento de 55 para 30 blocos.
- **VFX:** o buraco negro **encolhe** (0,6 → 0,05, inExpo) e o brilho em volta fica **mais quente**: branco → azul → branco-violeta. Isso é física: a temperatura de Hawking sobe quando a massa cai. As faíscas aceleram e cada cintilação é um piscar azul-branco.
- **Flash:** N1 nas três primeiras e N2 nas três últimas. **Shake 0.**

#### B22 · Ticks 700–719 · 35,00–35,95 s · "O ÚLTIMO CLARÃO"
**Áudio:** `sgx_burst`, um acorde maior com 9ª, ataque de vidro e decaimento de 3 s que cai no outro. **Sem sub-grave violento.**
- **Câmera:** segura e recua devagar (30 → 40 blocos).
- **VFX:** **o único branco de paz do filme** (N4 suave, **shake 0**). Uma casca de luz limpa se expande devagar e lava a cratera. Depois só restam as estrelas e a cratera sob a noite.
- **Tela:** título 704–716 em fade-in, `SINGULARITY` e abaixo, em traço mínimo, `黑洞`. Fade-out até o 719. O quadro final **não é preto**: é o mundo, com a cicatriz. Os 20 ticks de saída devolvem câmera, FOV, HUD e regras.

---

## 5. Continuidade (checklist de supervisão)

| Elemento | Regra |
|---|---|
| **Letterbox** | 16:9 (0–47) → 2,39 (79) → rebote na fusão → 2,39 até 459 → 2,8 (499) → 3,2 (539) → fechado (590) → preto (600–619) → 16:9 (630–fim). |
| **HUD** | Plex Mono branco-gelo. Existe de 4 a 579 e nunca depois do 580. Título só no 704. |
| **Shake 10** | Só no 241 (fusão) e no 360 (jatos). |
| **Shake 0 obrigatório** | B11 (plano-herói), B19 (silêncio) e B20–B22 (lado de fora). |
| **Silêncios** | 268–279 (quase) e **600–619 (absoluto: nenhum som, nenhuma imagem)**. |
| **Preto absoluto** | Só o buraco negro, até o 590. Depois, a tela inteira (590–619). |
| **Flash N4** | 240 (negativo), 360 (jatos) e 700 (o branco de paz, sem shake). |
| **Escala do buraco negro** | Nunca encolhe antes do 600 (a troca para o remanescente é escondida no preto). |
| **Destruição** | Todo corte de bloco fica sob algo que já cobre a tela: flash do 360, poeira 420–459, preto 600–619. |
| **Ordem das cores** | noite fria → prata → corpo negro (laranja → branco-azul) → violeta → âmbar → vermelho → preto → branco-gelo. |

---

## 6. Nota final do diretor

Este filme é sobre **atração** que vira **silêncio**. (O magnetar, o rival, é o contrário: **repulsa** que vira **luz**.) A primeira metade precisa ser tão bonita que a pessoa esqueça que está vendo uma ameaça: dois pontos dançando, um som que parece música. A partir do disco, a beleza fica com fome, e o filme inteiro (som, barras, cor, tempo da câmera) vai sendo **puxado para um ponto**. O segundo de preto e mudo no 600 é a coisa mais importante do filme: se ele não doer um pouco, nada antes funcionou. O último clarão não é explosão. É o buraco negro devolvendo, em luz, tudo o que comeu.

---

## 7. O que este storyboard ainda não decide (vai para a Fase 0)

- Se o **impostor** (sprite pré-renderizado da sombra + anel + disco dobrado) e o **disco 3D** (entidade) se ordenam certo na profundidade. Teste S-01 em `docs/ROADMAP.md`.
- Se `q.camera_rotation` / `q.rotation_to_camera` refletem a **câmera da cutscene** (setCamera). Se não, os billboards de entidade não servem e tudo vira partícula `lookat_xyz` (teste S-02).
- Se som **estéreo** em `is3D:false` toca estéreo no celular (o pan do Doppler depende disso, teste S-05).
- O que fazer se a mira estiver em **água/oceano** (proposta em `docs/DECISIONS.md` D-07).
