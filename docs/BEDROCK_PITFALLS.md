# Armadilhas do Bedrock — o que já se sabe antes de começar

Este addon começa do zero, **sem nenhum arquivo de projeto anterior**. Mas o usuário e o Claude já fizeram um addon de cutscene parecido (out/2026), e cada item abaixo foi **medido ou visto em vídeo** naquela jornada, no tablet do usuário (2304×1440, render 12, simulação 8) ou no celular (tela 20:9). Aqui ficou só o conhecimento, em forma de regra. **Leia isto antes de escrever a primeira linha de código.** Os IDs `P-xx` são citados no resto dos documentos.

## Desempenho e tempo

- **P-01 · O gargalo é a fila da thread do servidor.** O vídeo mostrou GPU 4–18 %, CPU ~50 % e 10–13 FPS: é uma thread presa. O script roda nela, e cada `spawnParticle`, `runCommand`, `setCamera`, `setTitle` e setter de `MolangVariableMap` é uma travessia nativa. Meça chamadas por tick, não FPS.
- **P-02 · O JavaScript é interpretado (QuickJS).** No Node com JIT o filme custa ~0,5 ms por tick; no tablet, 30–80 ms. O modelo calibrado é `tablet ≈ 6,5 × JS sem JIT + 0,02 ms por travessia nativa + 0,12 ms por comando`. Para estimar, rode o bench com `node --jitless`.
- **P-03 · Relógio travado no tempo real.** O áudio toca em tempo real; contando ticks do servidor, a imagem atrasava em relação ao som. Use o `MasterClock`: catch-up de até 40 ticks e reancoragem quando a pausa passa de 2,5 s (menu ou app em segundo plano).
- **P-04 · Cálculo pesado num cue só trava.** Um pico de 388 ms veio de calcular 5 000 pontos inteiros no tick 470. Use tarefas de fundo fatiadas (geradores no árbitro, `system.runJob` quando existir), prontas antes da hora.
- **P-05 · Hook sem janela é desperdício.** Eram ~25 checagens por tick, até de módulos sem nada para fazer. Todo hook declara `win`.
- **P-06 · Depois do filme, quem pesa é o motor do mundo.** O caso medido foi 5,9 TPS com 2,5 ms de script, por causa de luz, malha de subchunk e fluidos dos blocos trocados. Corte menos blocos (casca fina), use poucas fontes de luz (6 000 → 600) e vede a água antes do corte.
- **P-07 · Trabalho pesado sob o que já cobre a tela.** Hit-stop, white-out e tela preta são quando a fila de blocos pode usar 25 ms por tick.

## Câmera

- **P-08 · `camera.fade` tem piso de ~0,35 s.** Medido: flashes programados de 50–150 ms saíram com 300–400 ms. Todo flash mais curto que 0,4 s vai por overlay de JSON UI.
- **P-09 · `setCamera` não tem roll.** Roll só existe no z do `playAnimation`. O jeito que funcionou foi girar o **conteúdo** (efeitos) em volta do eixo de visão; sobre terreno real o roll não existe, e a composição compensa.
- **P-10 · Câmera em degraus.** Sem `easeOptions` o cliente segura cada pose por 4–5 quadros. Use ease linear de 0,05 s por tick (1 tick de atraso constante), com cortes e teleportes secos. Partículas presas à câmera nascem na pose **anterior**, com a velocidade da câmera.
- **P-11 · Câmera nativa por spline (`playAnimation`).**
  - O intervalo entre quadros tem que ser maior que 0,05 s (use ≥ 2 ticks).
  - A rotação usa `x = −pitch` e `y = 180 − yaw` em relação ao `setCamera`.
  - Ela roda no relógio do aparelho e não nos ticks: a 16 TPS, 10 s de câmera viram 2 s de atraso. Use trechos ≤ 3 s, esticados pelo TPS medido.
  - Deixe como experimental, com o modo por tick como padrão e volta automática se a API recusar.
- **P-12 · O FOV do Bedrock é vertical** e o pixel é quadrado (medido: estrelas caíram no pixel previsto com FOV vertical de 61°). Com isso dá para casar overlay pré-renderizado com o mundo: altura = altura da tela, largura 240 %y.

## JSON UI e HUD

- **P-13 · Esconder o título do barramento.** `hud_title_text` é um `stack_panel` criado por fábrica, então a visibilidade na raiz é ignorada. A condição vai nos filhos `title_frame/title` e `title_frame/title_background`. O teste de substring que funciona é `((#text - 'X') = #text)`; o `'%.4s'` não funcionou.
- **P-14 · Outros addons mexendo no HUD.** Se outro pacote instalado também sobrescrever os bindings de `title_frame/title`, eles não se somam: vale o de cima, e o título-barramento pode aparecer como texto. Use um marcador próprio e raro (`SGX`). Controles próprios entram por `modifications` com `insert_back` no `root_panel`, que mesclam entre pacotes. Vale testar uma vez com outro addon de HUD instalado.
- **P-15 · Imagem de UI mantém a proporção por padrão.** Use `keep_ratio: false` em overlay. `tiled: true` **não** repete o mosaico: estica.
- **P-16 · Centenas de controles na raiz avaliam a condição a cada quadro.** Agrupe em poucos painéis (1 por canal) e só os ativos descem.
- **P-17 · Letterbox em qualquer tela.** A barra se calcula pela largura (`%x`). Use barra mínima de 6 % em 20:9, sobra de 12 % para fora da área segura do celular e altura do texto pela largura (no celular largo, a legenda por altura virava "formiga").
- **P-18 · Reenvio de título.** Envie só quando o valor muda; o reenvio periódico é a cada 100 ticks, com `stay` de 160.

## Partículas

- **P-19 · O modo de direção é `"custom"`, não `"custom_direction"`.** A documentação da Microsoft está errada; o vanilla (`shriek.json`) usa `"custom"`. Com o modo inválido, nenhuma partícula direcional aparecia.
- **P-20 · Linhas e feixes** usam `lookat_direction` + `derive_from_velocity` (como o `vibration_signal` vanilla). O **eixo X** do billboard é a direção, então o comprimento vai em `size[0]`.
- **P-21 · Direções exatas degeneram.** Decalque `direction_z` com normal (0, 1, 0) exata falha: use (0, 1, 0,02). Pilar vertical com `lookat_direction` (0, 1, 0) também falha: use `lookat_y`.
- **P-22 · `rotate_xyz` não é "virado para a câmera".** Ele é perpendicular ao **eixo** da câmera, e um disco grande fora do eixo explode na projeção. Para planetas e discos use `lookat_xyz`.
- **P-23 · `size` do billboard é meia-largura** (medido, dentro de ~20 %).
- **P-24 · Partícula rápida duplica.** Dê velocidade por Molang para a cópia do tick anterior andar junto, e compense o alfa do par (`1 − √(1 − a)`).
- **P-25 · Fontes do HUD.** O Plex Mono do jar é um subconjunto. O Plex Mono completo não tem grego, e a família Mono não cobre grego. Para `☉ ⁷ ⁹ → ∞ ≈` use uma cadeia de fontes de apoio no bake (Noto Sans Symbols / Noto Sans Math) e **teste cada glifo** no relatório de bake.
- **P-26 · Persistente vale muito.** O efeito parado vira 1 partícula com curva quadrática no Molang (variáveis `Vector3`: `v.lf`, `v.a`, `v.s`, `v.c0`, `v.c1`), com fade cruzado de 2 ticks. Num efeito parado grande, isso levou de ~150 para ≤ 30 chamadas por tick.
- **P-27 · Instancing e fluxo.** Um emissor solta N grãos que calculam a posição pelo índice. A poeira vira um disco que solta grãos com taxa ∝ velocidade (numa viagem rápida, 266 chamadas → 1 a cada 3–5 ticks). Teto de ~1 100 partículas vivas no cliente.

## Entidades

- **P-28 · Propriedade não escrita vale 0 no cliente.** Uma propriedade nova `size` com padrão 1 chegou como 0 até ser escrita, e o anel ficou com escala 0. **Nunca multiplique a escala por uma propriedade que o script não escreve no spawn.**
- **P-29 · Faixa de propriedade float precisa ser literal float** (`[0.0, 1.0]`). O celular recusa `[0, 1]` com o erro "'range' array should contain only 'float' type elements", e a entidade fica sem **nenhuma** propriedade (daí o "query.property called on an actor without a property component").
- **P-30 · Plano de espessura zero não renderizou no tablet** (face única, alfa-blend). Cubos finos (anéis de 0,8 × 1,6 unidade) e decalques de partícula renderizam. **Use espessura ≥ 0,1 unidade.**
- **P-31 · Unidade da geometria: 16 unidades = 1 bloco.** A cúpula do céu saiu com 90 blocos em vez de 1 440 porque a escala foi contada em blocos. E quando os ossos se movem longe da origem, `visible_bounds` tem que cobrir o caminho, senão o jogo corta a entidade quando a origem sai da tela.
- **P-32 · Faces para dentro e UV do Blockbench.** Cima e baixo vêm girados 180° e o x espelhado. Um cubo de céu só fecha sem vinco visto do centro, por isso a casca anda com a câmera.
- **P-33 · Luz própria em bloco custa caro.** Cada bloco que emite luz força recálculo em volta, então use poucas fontes fortes. A crosta não emite luz.
- **P-34 · Propriedade por jogador.** `Player.setPropertyOverrideForEntity` / `clearPropertyOverridesForEntity`: o mesmo objeto no mundo, e cada cliente vê o próprio valor. Tenha uma volta para API antiga.
- **P-35 · `material`.** `entity_emissive` (alfa-teste, escreve profundidade) funcionou nos anéis; `entity_beam_additive` funcionou na cúpula (aditivo). O comportamento de profundidade entre aditivo × partícula alfa × emissivo **não foi medido**: é o teste S-01 da Fase 0.

## Mundo e destruição

- **P-36 · `fillBlocks` com filtro custa ~3 ms por caixa** (o filme acabou com quase nada cavado). Use `structure load` de cortes pré-gerados (ar dentro, `structure_void` fora), no máximo 1 pesado por tick. O gerador compara byte a byte com as funções de forma do JS.
- **P-37 · Água.** Ache com busca binária (`containsBlock` numa caixa, descarte a metade vazia) e vede antes do corte, senão o lago escorre de volta e ~400 chunks forçados simulam a água.
- **P-38 · Itens no chão pesam mais que blocos.** Desligue os drops durante a obra e limpe os itens no fim. Tronco cortado deixa folhas órfãs que apodrecem por minutos: limpe a copa.
- **P-39 · Areia e cascalho despencam.** Converta antes do corte uma verga de 2 camadas acima do teto.
- **P-40 · Ticking area não é para desempenho.** Ela só existe durante a obra, com prazo de 60 s depois do filme, e a lista fica gravada para remover depois de um crash.
- **P-41 · Noite forçada gera monstros.** Desligue `doMobSpawning` no filme e restaure no fim (e também depois de crash).
- **P-42 · Lua do jogo.** Às 18000 ela fica no zênite e entra nos planos para cima. Use 14500 ou 21500 (~37° acima do horizonte, do lado oposto ao olhar do jogador).
- **P-43 · Nuvens no Y 192.** Jatos e planos de céu devem considerar isso.
- **P-55 · Distância de SIMULAÇÃO, não de renderização** (medido pelo usuário em 25/10/2026, build 0.2.4). Com a cena maior (escala B), o centro do filme ficou além da distância de simulação do jogador e nada do addon aparecia lá: entidade e partícula só "acontecem" em chunk simulando. Aumentar a distância de simulação (exige sair e entrar no mundo) resolveu, o que prova a causa. A solução no addon é uma ticking area SÓ durante o filme (P-40): `world.tickingAreaManager.createTickingArea` (estável na 2.10), cuja promessa resolve quando os chunks estão carregados e simulando. O filme espera essa promessa antes de começar.
- **P-44 · Restaurar depois de crash.** Grave o estado original (regras, hora, modo de jogo, HUD) numa propriedade do jogador e restaure no próximo `playerSpawn` inicial.

## Áudio

- **P-45 · `playSound` sem posição toca no CORPO.** Na cutscene o corpo está no chão e o ouvinte é a câmera, então o som "ia só para a direita". Na cutscene use cópias 2D (`is3D: false`, `stream: false`, categoria `ui`); para quem está fora, posicional no ponto do evento, nos mesmos ticks.
- **P-46 · Primeira reprodução atrasa.** Pré-decodifique tocando cada som com volume 0,0001 quando o menu abre.
- **P-47 · Som posicional deve ser mono.** O 2D pode ser estéreo, mas **confirme no celular** (teste S-05).
- **P-48 · Alto-falante de celular não toca grave.** Abaixo de ~150 Hz some. Um chirp de 35 Hz precisa de harmônicos (saturação) para ser ouvido, porque o cérebro reconstrói a fundamental.

## Pacote, idiomas e aparelhos

- **P-49 · UUID novo por build de teste.** Isso evita "pacote duplicado" ao reimportar; use UUIDs estáveis no release. Valide JSON, dependência BP→RP, entry do script, imports, sons referenciados e ids de propriedades antes de empacotar.
- **P-50 · i18n.** `minecraft:display_name` literal impede tradução: o nome do item vem de `item.<id>` no `.lang`. Textos do script vão por `{translate, with}` (formulários aceitam `RawMessage`), com placeholders `%1`, `%2` e os mesmos `%n` nos dois idiomas.
- **P-51 · Dynamic property é por pacote.** Um addon não lê as do outro. Para sinal entre addons, use **tags** no jogador (`cinematic_busy`).
- **P-52 · Texturas.** Atlas de 8192 não é seguro em todo aparelho: máximo 2048 por textura. Use perfis de qualidade 1 / 0,75 / 0,5 (no projeto anterior: Alto ~40 MB, Equilíbrio ~28, Leve ~15).
- **P-53 · "APIs Beta".** Nunca foi confirmado se o experimento "APIs Beta" é necessário com `@minecraft/server` 2.10.0. Teste nos dois aparelhos **sem** a opção antes de escrever no manual que ela é necessária.
- **P-54 · A margem de tela do celular** (configuração de área segura do próprio jogo) muda o que aparece nas bordas. O usuário já confundiu isso com bug uma vez: pergunte antes de "consertar" uma listra na borda.
