# Changelog — Dooms Day

Formato: versão · data · o que mudou e **por quê**. Builds de teste saem em `dist/DoomsDay_<versão>_teste-<n>.mcaddon`, cada um com UUIDs novos.

## 0.2.6 (em teste) · out/2026 — o Ato VII pelo ponto de audição

**Por quê:** o usuário aprovou o áudio como "funcional", mas o B20–B22 era "sumiu, sumiu e mais nada, o som não induz nada" (no mixdown, o B20 estava em −37 LUFS, o mais baixo do filme). A pesquisa levou ao **ponto de audição** (point-of-audition): depois do trauma, o som é o que o OUVIDO escuta (o zumbido de *O Resgate do Soldado Ryan*, *Vá e Veja*). E um clímax só aterrissa com contraste antes.

- **B20, a volta:** do preto nasce um **zumbido agudo** (Ré8, dois senos batendo devagar, no meio da cabeça). Por baixo, o **mundo abafado**: a cratera e o vento, com um passa-baixa que abre de 160 Hz a 16 kHz, como o ouvido destampando. O B20 foi de −37 para −28 LUFS.
- **B21, Hawking:** o zumbido **desce e pousa no Ré6 do coral** (o trauma vira música) e um **Shepard–Risset sobe** (o espelho da queda sem fim). O enxame de brilhos chega ao máximo em 693–696.
- **697–699, drop-out:** tudo cai 32 dB e só um brilho fica no vazio. O contraste faz o clarão aterrissar.
- **B22, o clarão:** Ré maior pleno, e o som **abre de quase mono para estéreo largo** em 1,5 s (a luz se espalhando, por M/S: a soma mono não muda).
- Tudo como dado em `spec/score.json → act7`, compartilhado por trilha, ritmo e efeitos (`tools/synth/act7.py`).

## 0.2.5 (em teste) · out/2026 — a camada rítmica + o palco (ticking area)

**Por quê:** o retorno da 0.2.4 aprovou a trilha e os efeitos, mas faltava a terceira camada de "Mountains": o ritmo que une a trilha e os efeitos e deixa o relógio respirar. E, com a escala B, o centro do filme saiu da distância de simulação do jogador (P-55, medido pelo usuário).

- **Camada rítmica** (`spec/rhythm.json` → `tools/synth/rhythm.py`, sons `sgx_rhythm_a`/`b`), com instrumentos sintetizados: baixo pulsante, tom grave tipo taiko, shaker, poeira granular, tique de madeira/vidro e subidas que terminam secas no impacto. O pulso nasce da mesma matemática do filme:
  - **Ato I:** dois golpes distantes (o ponto e o gêmeo) e poeira granular crescendo;
  - **Ato II:** o baixo pulsa nas **meias-órbitas** (o relógio do chirp), seguindo a raiz dos acordes da trilha; o tom grave entra a cada meia-órbita, o shaker no fim, e uma subida para dentro da fusão;
  - **Ato IV:** um golpe a cada passagem do **Doppler de 1 Hz** do disco, baixo em colcheias, subida para os jatos e o ritmo pleno; no "olho do mundo" só fica um tique de madeira;
  - **Ato V:** tudo **acelerando** com a maré, com o baixo descendo junto com o pedal;
  - **Ato VI:** um pulso cujos intervalos **alongam** (o tempo dilatando, como o stutter da câmera);
  - **Ato VII:** tiques de vidro acelerando até o clarão, um golpe longo e o eco se espalhando.
- **Palco (ticking area):** o filme abre uma área em volta da mira, **espera ela carregar** ("Carregando a área…") e só então começa; a área some 60 s depois do fim (P-40). Os spikes com cena longe (S-01, S-03) também abrem a própria área. Sobra de crash é removida na carga do mundo.
- Testes novos: a área abre antes do filme, cobre a cratera e o disco, e some depois de 60 s. 60 testes.

## 0.2.4 (em teste) · out/2026 — escala B (o buraco negro 3,5× maior)

**Por quê:** a pergunta do usuário sobre a física (um horizonte de 1,6 m teria a massa de Saturno e mataria o planeta) levou à decisão D-14 → T-18: a escala B.

- **Toda distância da cena ×3,5** (`spec/layout.json → scene_scale`):
  - sombra de ~7 blocos e disco de 84 de diâmetro;
  - centro 49 blocos acima do chão;
  - o par começa a 28 blocos;
  - jatos mais grossos;
  - onda gravitacional mais rápida (passa pela câmera no mesmo tick 247);
  - o disco gira a **metade da velocidade** (coisa grande gira devagar).
- **Câmera ×3,5 também**, então os enquadramentos aprovados ficam iguais. O teto é de 150 blocos (render 12 = 192). As alturas rente ao chão não escalam: o olho humano olhando para cima é a régua.
- **Cratera:** raio 45 (×1,5, P-06). **Mira:** 60–160 blocos, e sem mira válida usa o chão 90 blocos à frente.
- Os tamanhos saem do spec (`DATA.scene`), sem número fixo no código. Os testes conferem a separação do par contra o spec, nenhuma câmera passando de 150 blocos e a mira mínima fora da cratera.

## 0.2.3 · out/2026 — efeitos de cinema (redesenho do SFX)

**Por quê:** com a trilha boa, os efeitos ficaram "SFX de YouTube de 2015" por cima de uma catedral: secos, fora do tom, cliques de ruído e bitcrush. Três regras para os 16 efeitos:

1. **O mesmo espaço da trilha:** todos passam pela mesma catedral (`dsp.cathedral`, parâmetros em `spec/score.json`). A dose varia: quase seco no chirp, que é a coisa mais perto do filme.
2. **O mesmo tom:** afinados em Ré, nas notas dos acordes da trilha naquele instante.
   - o ponto em Lá e o gêmeo em Fá (a terça menor da trilha);
   - os anéis do disco subindo Lá2 → Ré4 (a temperatura sobe, a nota sobe);
   - a maré como gemidos afinados que cedem;
   - o rasante do 500 em Lá dobrando para baixo;
   - os brilhos de Hawking no pentatônico de Ré maior;
   - o ringdown em Ré4;
   - o rugido do disco "canta" em Ré.
3. **Impacto tonal em vez de explosão:**
   - a fusão é um "braam" de metais graves em Ré com sub caindo até o Ré1 (o bitcrush saiu);
   - os jatos são um braam em Fá;
   - as subidas são o acorde da trilha em reverb invertido.

Também mudou:
- **Marcas de articulação:** viraram brilhos afinados de 12 ms, no nível do trecho, no lugar dos cliques de ruído.
- **Reverb:** as reflexões iniciais estavam ×30 e viravam filtro pente (um tom que varre oscilava ±3 dB tick a tick). Isso melhora a trilha também.
- **Ida e volta:** os testes pegaram duas caudas de sala vazando no vazio de 268–279. Corrigido: o quase-silêncio vale também para o reverb.
- **Ferramenta nova:** `tools/synth/diagnose.py <som>`, que mostra por que um onset falhou.

## 0.2.2 (em teste) · out/2026 — a trilha com "escala"

**Por quê:** a trilha da 0.2.1 melhorou, mas faltava "noção de escala": o poder do buraco negro, angelical e destrutivo ao mesmo tempo, sem precisar de explosão (referência do usuário: o Gargantua de Interestelar). A pesquisa virou técnica:

- **Pedal de "32 pés resultante":** fundamental + quinta, e o ouvido reconstrói uma oitava abaixo (o truque dos órgãos grandes, como o da Temple Church, onde Interestelar foi gravado). Tem batimento lento, a massa "respirando". Ele cai meio tom a cada passo na maré (Ré → Lá).
- **Extremos sem meio:** coral "aah" sintetizado no agudo (o angelical) sobre o pedal profundo (o destrutivo). No plano-herói do anel o meio fica vazio de propósito, e essa distância soa vasta.
- **Harmonia lenta sobre o Ré pedal**, a gravidade puxando tudo para uma nota, e poucos acordes longos.
- **O relógio de Interestelar:** a mesma nota repetida, presa às meias-órbitas (acentuada na meia-órbita, subdividida no meio).
- **Shepard–Risset descendo na queda** (460–600): a ilusão de um som que cai para sempre (o Zimmer usou em Dunkirk).
- **Espaço gigante:** reverb de 9 s com pré-delay de 95 ms e reflexões esparsas, com a cauda escurecendo (a distância come o agudo). Ele é aplicado por trecho e não vaza no corte do 240, no vazio de 268–279 nem no preto de 600–619 (um teste pegou o vazamento no 268 durante o desenvolvimento).
- A composição continua toda em `spec/score.json`: pedal, órgão, coral, dinâmicas por voz, relógio e Risset.

## 0.2.1 (em teste) · out/2026 — a trilha (score)

**Por quê:** ouvindo o mixdown da 0.2.0, o usuário achou o som "bem sintético, bem SFX", com falta de "um fundo, como o Hans Zimmer em Interestelar": a composição melódica que corre por baixo dos efeitos o tempo todo.

- **Trilha nova**, `sgx_score_a` (0–600) e `sgx_score_b` (620–760), com a composição como dado em `spec/score.json` (acordes, dinâmica, ostinatos). Para mudar a música, mexe no spec, não no código.
- **Ré menor → Ré maior:**
  - Ato I: só o pedal grave, com uma nota aguda no ar a cada buraco negro que aparece.
  - Ato II: Dm → Bb → F → C → Gm → A, crescendo até o grito, com **corte seco no 240**.
  - Ato III: só o grave respirando.
  - Ato IV: o órgão abre com o disco, Bb maj9 no plano-herói, órgão pleno nos jatos.
  - Ato V: o baixo cai cromático sob um cluster dissonante.
  - Ato VI: a dominante sem resolver, numa **parada de fita** (desacelera e afina para baixo até zero no 600).
  - Ato VII: Ré maior nascendo no agudo até o clarão.
- **Ostinato preso às meias-órbitas:** o "tique" acelera junto com a dança dos dois buracos negros (o mesmo relógio do chirp e das ondulações). Na maré ele volta cada vez mais rápido, e no fim vira um arpejo subindo até o clarão.
- **Órgão de tubos** por síntese aditiva (registros que abrem com a intensidade, coro de 3 tubos, vento do fole) e **reverb de catedral** de 4,5 s, aplicado por trecho para não vazar nos silêncios.

## 0.2.0 (em teste) · out/2026 — F2: o motor de áudio

**Por quê:** o som do filme agora é o de verdade, sintetizado em Python a partir do spec, e não mais um bipe por onset. O storyboard vem antes do som (T-03), e o som sai da mesma matemática da imagem (T-05).

- **`tools/synth/`** (numpy + scipy, sem nenhum sample de terceiros):
  - `recipes.py`: os 16 sons do AUDIO_DESIGN, do ar sendo sugado à última luz;
  - `render.py`: calibra, masteriza (−16 LUFS, pico −1 dBFS), exporta .ogg estéreo (2D) e mono (posicional) e gera o mixdown;
  - `analyze.py`: a ida e volta.
- **O chirp do LIGO** (35 → 245 Hz em 9 s) usa a **mesma fase** da órbita visual: os 19 acentos caem nas meias-órbitas (testado). Ele tem camadas 2Φ e 4Φ para o celular ouvir (P-48) e termina seco no 240, onde a fusão assume.
- **Ida e volta (o build falha se não bater):** cada um dos 62 onsets pedidos é re-detectado no áudio a ±0,5 tick e com rms_norm a ±0,15. O silêncio de 600–619 é digital (zero absoluto) e o ringdown fica abaixo de 5 % a partir do 268.
- **Mixdown:** `dist/DoomsDay_0.2.0_mixdown.mp3`, o filme inteiro como se ouve na cutscene, para ouvir no fone e no celular antes do jogo.
- **No jogo:** `timeline_data.js` (gerado) diz o que tocar e quando, com a envelope e os onsets detectados para a imagem seguir o som da F4 em diante.
- **Achados no caminho** (cada um travado por teste ou pela ida e volta):
  - o estéreo "largo" por atraso curto virava filtro pente na soma mono, e o chirp afundava ao passar por 150 Hz. Agora é L = x + s, R = x − s, que soma mono exata;
  - a frequência do chirp vai ao infinito no último tick e achatava o volume do resto. Agora f ≤ 245 Hz;
  - o envelope do chirp segue a curva do spec (T-16);
  - o calibrador começa com ganhos pequenos e tem busca de escala global.

## 0.1.1 (em teste) · out/2026 — correções do primeiro teste no aparelho

**Por quê:** o retorno do teste-1 (vídeo, relatos e print do chat) aprovou os 10 spikes e o ritmo da câmera, mas mostrou dois bugs.

- **Câmera presa no fim do S-01 e do S-02:** o `clear()` saía no mesmo tick do último `setCamera` com ease de 0,05 s, e o ease terminava depois religando a câmera livre. Agora a câmera é solta de novo 3 e 10 ticks depois (`releaseCamera`), também no fim do filme e no `sgx:stop`.
- **Erros `camera.pose @535…539` no chat:** o B16–B18 pede FOV 120 e o jogo só aceita até 110. O FOV fica preso em 30–110 (T-14). As mensagens de erro agora trazem o texto do erro, não só a linha (no QuickJS o stack vem sem a mensagem).
- **Menu sem mira válida:** em vez de recusar ("Perto demais…" 4 vezes no print), usa o chão 60 blocos à frente e avisa.
- **F0 concluída:** resultados em `docs/SPIKES.md` e decisões T-13 a T-15.
- Testes: o jogo falso agora recusa FOV fora de 30–110 como o de verdade, e os spikes precisam soltar a câmera depois do último ease (os dois testes ficam vermelhos sem a correção). 54 testes.

## 0.1.0 (em teste) · out/2026 — F0 (spikes) + começo da F1 (animatic)

**Por quê:** a F0 responde às 10 perguntas que só o aparelho responde. Com o motor pronto, dá para ver também o **ritmo da câmera** do filme inteiro em caixas cinzas, que é a hora em que mudar o storyboard é barato.

- **Nome:** o addon passa a se chamar **Dooms Day** (D-01). "Doom" é o destino inevitável, palavra muito ligada a buracos negros. Os ids internos (`singularity:`, `sgx:`) continuam iguais.
- **F0, os 10 testes:** `/scriptevent sgx:spike 1…10`, cada um explicando no chat o que olhar. Ver `docs/SPIKES.md`.
- **Motor (escrito do zero, com testes):** relógio mestre preso ao tempo real (catch-up de até 40 ticks e reancoragem depois de pausa), árbitro com janelas, prioridades e não-inanição, câmera por keyframes (cortes, step, stutter, câmera na mão), barramento de HUD por título, ajudante de partículas que conta as chamadas e segurança (noite fixa, sem mobs, HUD escondido, restauração depois de crash).
- **Animatic do buraco negro:** `/scriptevent sgx:play blackhole`, ou o item → BURACO NEGRO. Ele roda os 22 blocos com a câmera certa, o par A/B na órbita da fórmula do LIGO, 19 ondulações, a onda gravitacional, o disco acendendo de fora para dentro, os jatos, o pedaço-herói, Hawking e o clarão. Também tem o letterbox "puxado" (16:9 → 2,39 → 3,2 → fecha → preto no 600), o desvio para o vermelho, os flashes, o impacto negativo no 240, o tremor, o HUD provisório na actionbar e um bipe por onset do áudio.
- **Trace:** a actionbar mostra o bloco e o tick (ex.: `B07 · 215`) para o retorno do animatic. Para desligar: `/scriptevent sgx:trace off`.
- **Ferramentas:** `tools/build_all.py` (todos os geradores), `tools/package.py` (valida e empacota com UUIDs novos), `tools/gen_assets.py`, `tools/gen_ui.py`, `tools/build_storyboard_data.py` e `tools/synth/placeholder.py`.
- **Correção no kit:** o modelo do detrito usava textura de 16×16, mas a UV de caixa de um cubo 16³ ocupa 64×32 (a textura sairia esticada).
- **Testes:** 53 (`node --test tests/*.test.mjs`). O animatic inteiro roda no Node com um jogo falso e ficou em ~7 partículas/tick de média e 16 de pico (meta: 60/120).
