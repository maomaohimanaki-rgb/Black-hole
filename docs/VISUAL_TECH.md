# Técnica visual — como cada coisa vira pixel no Bedrock

A ideia combinada é **híbrida**: o principal em **ossos e Molang** (geometria que o cliente anima sozinho) e em **texturas assadas em Python** (o que o Bedrock não sabe calcular, como a lente gravitacional). Tudo foi pensado para o servidor mandar o **mínimo** (PITFALLS P-01) e para ter um plano B com técnica que já funcionou em aparelho real quando um teste da Fase 0 falhar.

---

## 1. Camadas do buraco negro

Do fundo para a frente da câmera:

| # | Camada | Forma | Material | Quem anima | Plano B (técnica já vista funcionando) |
|---|---|---|---|---|---|
| L0 | **Anel de Einstein** (estrelas da NASA dobradas em volta) | partícula `lookat_xyz` grande, persistente | `particles_add` | nada (textura por plano) | — (é enfeite; dá para cortar) |
| L1 | **Buraco negro em malha** (v0.3.1, T-25): disco, corcova, arco de baixo, sombra, anel de fótons e halo | entidade `sgx_bh`: malhas por bin de elevação, osso virado para a câmera (`q.rotation_to_camera`) | `charged_creeper` (aditivo, `uv_anim`) + `entity_alphatest` (sombra) | Molang: giro por `uv_anim` (Kepler por anel, `q.frame_alpha`), escala, ignição | o impostor de partícula da 0.3.0 (vetado pelo usuário) |
| L2 | **Disco 3D** (só nos planos próximos: B10, B11, B15, B16) | entidade `sgx_disk`, 5 anéis de cubos finos | `entity_emissive` (núcleo) + `entity_beam_additive` (brilho) | Molang: rotação kepleriana | decalque de partícula `direction_z` com flipbook girando |
| L3 | **Jatos** | partículas `lookat_y` (núcleo + bainha) + nós instanciados | `particles_add` | Molang | — |
| L4 | **Matéria caindo** (detritos, pedaço-herói) | entidade `sgx_debris` | `entity_alphatest` (textura de bloco) | Molang: espiral + esticamento | partícula com textura de bloco |
| L5 | **Ondulações / onda gravitacional** | decalque `direction_z` (0, 1, 0,02) + casca instanciada | `particles_add` | Molang | — |
| L6 | **Tela** (vermelho, íris, aberração, impacto negativo, último fóton, linhas de velocidade) | JSON UI pelo barramento de título | — | o cliente (por canal) | — |

### v0.3.1: por que malha (T-25)

O usuário vetou sprite: o buraco negro tem que ser **objeto** (entidade, JSON, Molang). Os vídeos da NASA que ele mandou mostram o disco xadrez como uma **malha dobrada pela lente**, e é isso que `tools/bake/bh_model.py` faz:
- **O mapa da lente por vértice** (`bh_lens.py`): cada vértice do disco (r, ψ) vai para onde a sua imagem aparece. A imagem direta fica no ponto real do disco deslocado pela lente: perto do buraco ela vira a corcova por cima da sombra; longe, é o disco 3D de verdade, com paralaxe. A secundária (o arco por baixo) fica no plano do céu, sem as partes que a direta já cobre.
- **Um conjunto de malhas por bin de elevação** (16 do buraco final, 7 de A/B), num osso que o cliente vira para a câmera a cada quadro. O script troca o bin (`singularity:bin`) só quando a câmera passa de um para o outro; negativo = câmera abaixo, o cliente espelha (escala −1 em Y).
- **O giro do disco é a textura andando** (`uv_anim`), um render controller por anel com o ω de Kepler. O tempo usa `(floor(q.life_time·20) + q.frame_alpha)/20`, a mesma conta do creeper carregado do vanilla: liso em qualquer FPS.
- **O Doppler** fica parado no referencial da câmera, então ele é uma segunda camada aditiva (textura por grupo de elevação e por imagem). As texturas são espelhadas em V, então a malha funciona igual se o jogo contar V de cima ou de baixo.
- A **prévia** (`build/bake/lens_sheet.png`) é um rasterizador numpy que soma as camadas como o jogo soma.

### Por que impostor

A lente gravitacional não é um efeito de shader que o Bedrock tenha. O que se vê de um buraco negro com disco é **uma imagem**: a sombra, o anel de fótons e o lado de trás do disco aparecendo por cima e por baixo, que muda **só com a inclinação** (o ângulo entre a câmera e o eixo de spin). Como o eixo do nosso buraco negro é vertical (U) e a câmera do Bedrock não tem roll (P-09), a projeção do eixo na tela é sempre vertical. **Uma partícula virada para a câmera com o quadro certo da inclinação é fisicamente a imagem certa**, para qualquer posição de câmera em volta.

---

## 2. O motor de imagem (Python): `tools/bake/bh_engine.py`

### 2.1 Traçado de raios de Schwarzschild (numpy, offline)
- Para cada pixel do impostor: um raio que sai da câmera a uma distância grande (ex.: 60 r_s) com parâmetro de impacto `b`. Integre a órbita do fóton `d²u/dφ² = −u + (3/2)·r_s·u²` (u = 1/r) com RK4. É a forma clássica: plana, por simetria esférica, só precisa de `b` e da inclinação.
- O raio é **capturado** (sombra) se `u` passa de `1/r_s`, e **escapa** (fundo) se volta para longe. Se ele cruza o plano equatorial entre `r_in` e `r_out`, **acerta o disco** (primeira, segunda e terceira imagem: as 3 primeiras passagens).
- **Tabela pré-computada:** para cada `b` (≈ 2 000 valores) e cada cruzamento do plano, o raio `r` onde cruza. O pixel só consulta a tabela, o que deixa tudo rápido.

### 2.2 Brilho e cor do disco
- **Temperatura:** `T(r) ∝ r^(−3/4) · (1 − √(r_in/r))^(1/4)` (Novikov–Thorne simplificado), normalizada para 9 000 K no pico e 2 000 K na borda.
- **Fator g** (Doppler + gravitacional): `g = √(1 − 3r_s/2r)` / `(1 + β·cos ψ)` com `β` de Kepler; brilho × **g⁴** e cor da temperatura × **g**. O lado que se aproxima fica mais claro e mais azul. Use `β` visual 0,45 no anel interno (`spec/layout.json`) se o real deixar o lado de lá apagado demais.
- **Turbulência:** ruído fBm em coordenadas polares (r, φ − ω(r)·t), com ω kepleriano. **8 quadros** de tempo fazem um loop: o quadro 8 encosta no 1 porque o deslocamento de cada anel é múltiplo de 2π/8.
- **Anel de fótons:** sai sozinho do traçado (raios que dão quase uma volta), com uma camada extra de bloom fino.
- **Tonemap:** `1 − e^(−1,15x)` seguido de gama 1,12, com dither de ±1 LSB só onde tem luz (dither no preto engorda o PNG à toa). Fica em `tools/bake/common.py`.

### 2.3 O que assar (orçamento de textura)
O storyboard define **quais inclinações aparecem de verdade**. Asse **só essas** (lista gerada da câmera em `spec/storyboard.json` pelo `bh_engine.py --plan`), arredondadas para 7,5°. Isso dá umas 6 a 9 inclinações, não as 24 possíveis.
- Cada inclinação: 8 quadros de 512² num atlas 2048×1024 (≤ 2048, P-52).
- Perfis: equilíbrio 0,75× e leve 0,5× pela mesma `res_profile.json`.
- O mesmo motor gera os **impostores pequenos** de A e B (só sombra + anel + disquinho de poeira, 256²).
- **v0.3.0:** o que foi assado:
  - `bh_atlas.png`: 14 inclinações (±45…±90 de 7,5 em 7,5), mais +37,5 e um quadro "sem disco";
  - `bh_small.png`: 16 inclinações de A/B.
  - Lista e números visuais em `spec/bake.json` (T-24). No jogo, o quadro sai da inclinação da câmera a cada spawn (`modules/impostor.js`).

### 2.4 Escolher o quadro no Molang
O script manda a inclinação **uma vez por plano**, no spawn da partícula persistente (`v.incl` = índice). O quadro de tempo vem de `v.particle_age`:
```
v.fr = math.mod(math.floor(v.particle_age * 10), 8);          // 8 quadros em 0,8 s
uv   = [ math.mod(v.fr, 4) * 512 , math.floor(v.fr / 4) * 512 ]
```
(Molang não tem o operador `%`: use `math.mod`. E as funções trigonométricas recebem **graus**.)
(Com uma textura por inclinação. Se o Bedrock não aceitar trocar textura por variável na partícula, cada inclinação vira um identificador de partícula, `sgx_imp_00…08`, e o script escolhe o id.)

### 2.5 Quando a câmera chega perto
O impostor é uma imagem "de longe": a câmera a ≥ 25 blocos de O (2× o raio do disco) não percebe a falta de paralaxe. Mais perto que isso (B11 termina a 14 blocos, e B15–B16 entram no disco), use o **modo lente**: o impostor sem o lado da frente do disco (variante `front_cut`), e o disco 3D (L2) desenha a parte da frente. Assim a profundidade é real onde ela se nota. O teste S-01 decide se a ordem de desenho funciona.

---

## 3. O disco 3D: `sgx_disk`

- **Geometria** (gerada por `tools/gen_assets.py`; modelo em `templates/`): 5 ossos `ring_1…ring_5`, filhos de `spin_root`. Cada anel tem 32 cubos com 0,1 unidade de altura (P-30), girados em volta de Y, com a largura do anel. As UVs apontam para uma faixa do atlas do disco (a turbulência daquele raio).
- **Animação** (Molang no `pre_animation`, sem script):
  ```
  v.ang = (v.ang ?? 0) + q.delta_time * 180;                      // ω do anel interno (°/s)
  ring_k.rotation = [0, v.ang * math.pow(r_k / 2.4, -1.5), 0]     // Kepler: ω ∝ r^-3/2
  ```
- **Acender de fora para dentro** (B10): propriedade `singularity:lit` (int 0–5) escrita em 5 cues (280…304); `part_visibility` mostra os anéis acesos, e a textura troca de "brasa" para "acesa" por anel.
- **Brilho geral:** propriedade `singularity:heat` (float `[0.0, 1.0]`, P-29), escrita nos cues.
- **Escala:** a propriedade `singularity:scale` é **escrita no spawn** (P-28) e segue a `scale_curve` do `layout.json` em cues.
- `visible_bounds` de 32×32 blocos (P-31).

---

## 4. Par A/B em órbita (Ato I–II): zero chamadas por tick

A fase vem de uma **fórmula fechada** (`spec/layout.json → binary.orbit_phase`). O script faz o spawn de A e B uma vez (no 20 e no 40) com:
- `v.t0` = segundos de filme no spawn e `v.tc` = 12,0 s (tick 240);
- massa, sombra e lado (+1 / −1).

O cliente calcula a posição de cada quadro (tanto faz entidade com osso deslocado ou partícula persistente):
```
τ   = math.max(v.tc - (v.t0 + q.life_time), 0.001);
d   = 8 * math.pow(τ / 9, 0.25);
φ   = φ0 + 6.2832 * (35 / (2 * 24)) * math.pow(9, 0.375) * 1.6 * (math.pow(9, 0.625) - math.pow(τ, 0.625));
pos = side * d * (m_outro / 65) * [cos φ, 0, sin φ]   // no referencial de O (R, U, F)
```
**Atenção:** Molang trabalha em graus nas funções trigonométricas (`math.cos(graus)`). Converta: `math.cos(φ * 57.2958)`.

O **mesmo** `binary_math.js` gera a lista de meias-órbitas que o script usa para as ondulações, e o sintetizador gera o chirp com a mesma fase. O teste `órbita ↔ áudio` trava isso.

**Risco:** o cliente pode ter `q.life_time` um pouco defasado do relógio de parede do script (o spawn chega com atraso de rede/tick). No pior caso, alguns ms: invisível. Se ficar visível no vídeo, o script reenvia `v.t0` corrigido a cada meia-órbita (19 chamadas no filme inteiro).

---

## 5. Detritos e pedaço-herói: `sgx_debris`

Uma entidade com um cubo de 1 bloco cuja textura é escolhida por propriedade (`singularity:kind`, int 0–15). O script lê o bloco real do chão e escolhe o mais parecido: grama, terra, pedra, areia, tronco, folhas, neve, cascalho, argila, terracota, deepslate, madeira, gelo, água (cubo azul translúcido), lava (raro), "genérico".

Propriedades escritas **no spawn**:

| Propriedade | Tipo | Faixa |
|---|---|---|
| `r0` | float | `[0.0, 64.0]` |
| `phi0` | float | `[-360.0, 360.0]` |
| `y0` | float | `[-32.0, 32.0]` |
| `tc` | float | `[0.5, 6.0]` |
| `spin` | float | `[-720.0, 720.0]` |
| `kind` | int | `[0, 15]` |

O Molang anima o osso `body` (a entidade em si não se mexe, P-31: `visible_bounds` de 64×64):
```
u     = math.clamp(q.life_time / q.property('singularity:tc'), 0, 1);
r     = q.property('singularity:r0') * math.pow(1 - u, 0.6667);        // cai acelerando
ang   = q.property('singularity:phi0') + 360 * 2.5 * u * u;              // espiral apertando
y     = q.property('singularity:y0') * (1 - u) + 14 * (u * u * (3 - 2 * u));   // sobe até o plano do disco (O)
st    = 1 + 5 * math.pow(u, 3);                                          // esticamento (espaguete)
body.position = [r * math.cos(ang) * 16, y * 16, r * math.sin(ang) * 16];   // unidades de geometria
body.scale    = [1 / math.sqrt(st), st, 1 / math.sqrt(st)];
body.rotation = [0, -ang, q.property('singularity:spin') * u];          // o comprido aponta para dentro (ajuste no S-04)
```
Quando `u` chega a 1, a entidade se remove (evento `singularity:despawn` por `minecraft:timer` com o mesmo `tc`) ou o script remove em lote no B19.

O **pedaço-herói** (B15–B16) é a mesma entidade com `tc` maior. A câmera segue **a mesma fórmula**, calculada no script por tick (a câmera já é 1 pacote por tick), sem teleportar a entidade.

**Puxão de criaturas** (B14–B16): os mobs num raio de 40 recebem `applyImpulse` na direção de O a cada 4 ticks, com força crescente (≤ 12 mobs por tick, prioridade normal no árbitro). Os que chegam a 3 blocos de O morrem (dano customizado, se o "Dano às criaturas" estiver ligado).

---

## 6. Ondulações e onda gravitacional

- **Ondulação no chão** (19 vezes, nas meias-órbitas): decalque `direction_z` com normal (0, 1, 0,02) (P-21). Anel prateado que cresce de 2 para 18 blocos em 1,2 s e apaga. É **uma** chamada por ondulação (a curva toda está no Molang).
- **Casca da onda gravitacional** (241): uma esfera de "ar tremido" feita de ~300 grãos instanciados (P-27), num anel na superfície de uma esfera que cresce a 6 blocos/tick, mais um decalque de anel no chão com a mesma velocidade. Quando passa pela câmera (247), o **FOV respira** (B08). Isso é câmera, não partícula.

---

## 7. Jatos

- **Núcleo:** `lookat_y` (P-21), 1,2 bloco de largura e 180 de altura (para cima). Para baixo vai até o fundo da cratera. Persistente (o brilho segue a curva do áudio por Molang).
- **Bainha:** `lookat_y`, 5 blocos, violeta-azul a 40 % de alfa.
- **Nós de plasma:** emissor instanciado que solta uma bolha a cada 4 ticks, que sobe a 8 blocos/tick sozinha (velocidade no Molang).
- Nunca use `lookat_direction` com (0, 1, 0) exato (P-21).

---

## 8. Tela (JSON UI, pelo barramento de título)

Canais (2 letras, valor 00–99; ver ARCHITECTURE §4.6):

| Canal | O quê | Valores |
|---|---|---|
| `LB` | altura da barra (% da meia-tela; 99 = fechado) | curva `letterbox_curve` |
| `RS` | desvio para o vermelho (overlay cor + alfa) | 0–99 |
| `AB` | anel de aberração (quadros PNG) | 1–16 |
| `IR` | íris circular | 1–16 |
| `LP` | último fóton (tamanho) | 1–16 |
| `IN` | impacto negativo (quadro PNG assado com a pose exata do 240) | 1–2 |
| `SP` | linhas de velocidade | 1–8 |
| `FL` | flash (branco, branco-gelo, branco-quente, violeta) | 1–N |
| `SB`, `HD`, `HT`, `TT`, `TT2` | legenda, HUD, tremor, título, subtítulo CJK | ids do catálogo |

**Impacto negativo (240):** a UI não inverte a imagem do mundo. O quadro é **assado** pelo Python com a pose exata da câmera no 240 (o overlay pré-renderizado casa com o mundo porque o FOV é vertical e o pixel é quadrado, P-12): tela preta, o buraco negro como disco **branco** na posição projetada, anel em traço de pincel (sumi-e) e linhas radiais. A câmera olha para O nesse tick, então o disco fica no centro (confira no gizmo).

---

## 9. Céu e noite

- **Noite fixa** durante o filme, na hora que deixa a Lua do jogo longe dos planos (P-42). Sem spawn de mobs (P-41).
- **Anel de Einstein (L0):** usa o mapa da NASA de `assets/nasa/` (ver `assets/nasa/SOURCES.md` para o tratamento: difuso + catálogo de estrelas nítidas). Ele é assado **por plano**, porque o fundo dobrado depende da direção da câmera, e só para os planos que precisam (B11 e talvez B20). Ele não casa com o céu do Minecraft atrás (é outro céu), por isso fica fraco e só perto da sombra (até ~3× o raio dela). Decisão D-05.

---

## 10. Testes de renderização da Fase 0 (spikes)

Cada um é um `/scriptevent sgx:spike <n>` que monta a cena de teste na frente do jogador e mostra no chat o que observar. O resultado vai para `docs/SPIKES.md` (print + "funcionou / não funcionou").

| ID | Pergunta | Montagem | Se falhar |
|---|---|---|---|
| **S-01** | Profundidade: o disco 3D na frente da sombra e a sombra (partícula alfa) na frente do lado de trás do disco? | `sgx_disk` + partícula preta no centro, câmera girando em volta | Tudo impostor (sem disco 3D); planos próximos com FOV maior para não chegar tão perto |
| **S-02** | `q.camera_rotation` / `q.rotation_to_camera` refletem a câmera da **cutscene** (`setCamera`)? | entidade-billboard + câmera de cutscene orbitando | Billboards só por partícula `lookat_xyz` |
| **S-03** | Entidade com cubos finos de 0,1 unidade e `entity_emissive` renderiza no tablet e no celular? | um anel do disco | Espessura 0,4 ou decalque de partícula |
| **S-04** | Detrito com osso deslocado 30 blocos por Molang continua visível quando a origem sai da tela? Esticamento e rotação certos? | 20 detritos em espiral | Aumentar `visible_bounds`; ou partícula com textura de bloco |
| **S-05** | Som `is3D:false` estéreo toca estéreo no celular? E o pan do Doppler? | um .ogg com pan L→R | Mix 2D mono; o Doppler fica só na AM |
| **S-06** | Partícula escolhe o quadro do atlas por variável (`v.incl`) e anima por `particle_age`? | impostor de teste com números nos quadros | Um id de partícula por inclinação |
| **S-07** | `poly_mesh` em geometria de entidade funciona nos dois aparelhos? (disco liso em vez de cubos) | um disco `poly_mesh` | Fica nos cubos (já funciona) |
| **S-08** | Barra do letterbox em 3,2:1 e fechamento total em 20:9 com margem de área segura | canal `LB` varrendo 0 → 99 | Ajustar o `gen_ui.py` |
| **S-09** | FOV respirando ±5° a cada 3 ticks fica liso (ease de 1 tick)? | câmera parada com FOV oscilando | Oscilação mais lenta (6 ticks) |
| **S-10** | `applyImpulse` em mobs a cada 4 ticks é liso, sem "teleporte"? | 10 vacas puxadas para um ponto | Impulso a cada 2 ticks, menor |
