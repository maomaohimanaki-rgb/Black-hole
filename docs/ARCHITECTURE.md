# Arquitetura — SINGULARITY

Addon **novo, escrito do zero**, com dois eventos cinematográficos: o **buraco negro** (`docs/STORYBOARD.md`) e o **magnetar** (`docs/MAGNETAR.md`). Nenhum arquivo vem de outro projeto. O que vem de experiência anterior são as **regras** (`docs/BEDROCK_PITFALLS.md`) e o **desenho** do motor descrito aqui, que já se provou em aparelho real.

---

## 1. Princípios

1. **Um relógio só.** Todo efeito é "dispare quando `t ≥ N`". Nada de `runTimeout` encadeado, que acumula erro. O relógio é travado no **relógio de parede** porque o áudio toca em tempo real (P-03).
2. **Módulos que não se conhecem.** Cada parte do filme é uma função `(ctx) => void` que agenda cues, registra hooks por tick e limpeza.
3. **A fila da thread do servidor é o gargalo** (P-01). Toda técnica começa por "quantas chamadas nativas por tick isso custa?".
4. **O cliente anima, o servidor só dá a partida.** Partículas persistentes com curva no Molang, entidades animadas por Molang e órbitas por fórmula fechada.
5. **O peso cai onde não se vê** (P-07). Corte de bloco e trabalho grande ficam sob flash, poeira ou tela preta.
6. **Dados gerados, nunca editados à mão.** Timeline, storyboard em JS, HUD, geometrias, partículas, estruturas e texturas saem de scripts idempotentes, e testes conferem gerado × fonte.
7. **Tudo testável fora do jogo.** O motor não importa `@minecraft/server` direto: `system`, `world` e enums entram por injeção. Um harness em Node simula ticks, servidor atrasado e conta chamadas.

---

## 2. Fluxo de dados

```
spec/*.json (storyboard, áudio, layout, paleta, orçamento, projeto)          ← fonte única
   │
   ├── tools/synth/         Python: RP/sounds/singularity/*.ogg + build/timeline.json
   │                          └─ tools/build_timeline.py → BP/scripts/singularity/<evento>/timeline_data.js
   ├── tools/build_storyboard_data.py   spec/storyboard.json → BP/scripts/singularity/<evento>/storyboard_data.js
   ├── tools/bake/          Python: impostores (traçado de raios), disco, céu com lente, linhas de campo, overlays, HUD, ícones
   ├── tools/gen_assets.py  entidades, geometrias, partículas (+ gêmeas persistentes), render controllers, sons
   ├── tools/gen_ui.py      RP/ui/hud_screen.json (barramento por título, letterbox, overlays)
   ├── tools/gen_structures.mjs   cortes da cratera (.mcstructure) com as MESMAS funções de forma do JS
   ├── tools/check_spec.py  coerência do spec + docs/BEAT_TABLE.md
   └── tools/package.py --profile alto|equilibrio|leve  ·  tools/release.py → dist/Singularity_<v>.zip
```

---

## 3. Estrutura do repositório

```
singularity-bedrock/
├── CLAUDE.md · README.md · CHANGELOG.md
├── spec/  docs/  assets/ (nasa/, fonts/)  templates/  (deste kit)
├── build/                         saídas intermediárias (timeline.json, mixdown, relatórios) — fora do git ou no .gitignore
├── BP/
│   ├── manifest.json · pack_icon.png · texts/ · items/sgx_core.json
│   ├── entities/  sgx_disk, sgx_debris, sgx_anchor, …
│   ├── structures/sgx/
│   └── scripts/
│       ├── main.js                       item, menu (Buraco negro · Magnetar · Opções), scriptevents, boas-vindas
│       └── singularity/
│           ├── engine/                   o motor (seção 4), sem nada específico de evento
│           │   clock.js  arbiter.js  camera_engine.js  cull.js  persist.js  ui_bus.js  i18n.js
│           │   profiler.js  block_worker.js  stage.js  cutscene.js  audio.js  hud.js  letterbox.js  safety.js
│           ├── blackhole/                o evento 1
│           │   layout.js  binary_math.js  storyboard_data.js (GERADO)  timeline_data.js (GERADO)
│           │   modules/ binary ripples disk jets tidal fall horizon hawking crater camera
│           └── magnetar/                 o evento 2 (F9+)
│               layout.js  field_math.js  storyboard_data.js  timeline_data.js
│               modules/ field star quake flare tail filings sky camera
├── RP/  entity/ models/ render_controllers/ animations/ particles/ sounds/ textures/sgx/ ui/hud_screen.json (GERADO)
├── tools/
└── tests/  harness.mjs  mc_stub_loader.mjs  *.test.mjs
```

---

## 4. O motor (escrito do zero, com este desenho)

### 4.1 `clock.js`: `TickScheduler` + `MasterClock`
- `scheduler.at(tick, fn, {order, tag})`: tick fracionário arredonda (`Math.round`). Ordena por (tick, order, inserção) e é **selado** no start. `advanceTo(t)` dispara em ordem tudo com `tick ≤ t`. Um cue que lança erro **não** derruba o filme: o erro vai para uma lista.
- `MasterClock`:
  - `t` vem do tempo real desde o start (`floor(ms/50)`), **nunca volta**, nunca fica atrás dos ticks do servidor e nunca passa mais de 40 ticks na frente deles;
  - uma pausa maior que 2,5 s entre ticks (menu do jogo, app em segundo plano) **reancora** em vez de pular;
  - o tick 0 dispara na mesma chamada do start, então o som do tick 0 não atrasa;
  - `stop(reason)` é idempotente e chama `onStop` uma vez só;
  - registra `lag.skippedFrames` e `lag.maxSkip`.
- `from <t>` (preview): descarta sem executar os cues anteriores a `t`.

### 4.2 `arbiter.js`: orçamento por tick
- Cada hook declara `win: [de, até]` e fora dela nem é chamado. `prio`: `critical` (câmera, UI, áudio, palco, blocos) sempre roda; `normal` roda enquanto o tick estiver abaixo do orçamento; `optional`, abaixo de uma fração dele.
- **Não-inanição:** quem ficou de fora num tick roda obrigatoriamente no seguinte.
- **Tarefas de fundo:** geradores que andam nas sobras de ms (`system.runJob` quando existir). `finish(nome)` completa na hora se alguém precisar do resultado antes.
- Orçamento por perfil, de `spec/budgets.json` (14 / 12 / 10 ms).

### 4.3 `camera_engine.js`: câmera "on ones"
- Keyframe `{t, p, l | r:{pitch,yaw}, fov, roll, ease, cut}`. O `ease` diz como se chega **neste** keyframe; `cut` = chegada seca; fov e roll herdam do anterior.
- Convenção: pitch positivo = olhando para baixo; yaw 0 = +Z.
- Easings: linear, step, in/out/inOut × Quad/Cubic/Expo/Sine, outBack, outBounce. `lerpAngle` pelo caminho mais curto.
- Envio por tick com ease linear de 0,05 s (P-10). **Novo para este addon:** `stutter: [n…]` (a pose segura n ticks) e alvos que seguem uma fórmula (pedaço-herói, órbita).
- Modo spline nativa opcional e experimental (P-11), com volta automática para o modo tick.

### 4.4 `cull.js`: recorte por campo de visão
- Esfera (centro, raio) contra o frustum com **FOV vertical** (P-12), aspecto 2,22 (o mais largo que o jogo usa) e margem de 8 %. Atrás da câmera = cortado. Câmera dentro da esfera = visível. Com roll, usa o círculo da diagonal.

### 4.5 `persist.js`: efeitos parados com 1 chamada
- O efeito descreve o estado em função do tempo: `sample(t) → {id, pos, a, col, num, fixed}`.
- O persistidor testa períodos de 16, 8, 4 e 2 ticks e escolhe o **maior** em que o efeito cabe numa **quadrática** (início, meio, fim). Solta **uma** partícula `sgx_p_*` com a curva em variáveis `Vector3` (`v.lf`, `v.a`, `v.s`, `v.c0`, `v.c1`) e fade cruzado de 2 ticks com soma 1.
- Teste: brilho constante ±2 % na troca.

### 4.6 `ui_bus.js`: HUD por título
- Vários canais (2 letras, valor 00–99) num único título: `SGXB;AB=03;LB=40;RS=12;`. Envia só quando muda, com reenvio a cada 100 ticks. Limpeza com `SGX_CLEAR`.
- O `hud_screen.json` gerado esconde todo título com `SGX` (P-13) e liga os controles pelo teste de substring.

### 4.7 `block_worker.js`: destruição
- **Uma** fila global, fatiada por **tempo de CPU** por tick (6 ms normal, 25 ms em frame preto ou congelado).
- Tipos de tarefa:
  - `cmd`: comando;
  - `structure`: `structure load` de corte pré-gerado, no máximo 1 por tick;
  - `protect` e `restore`: salva os contêineres antes e devolve depois;
  - `seal`: água vira crosta;
  - `fill`: preenche.
- **Termina depois do filme** se precisar (a destruição é permanente).
- Antes do corte: drops desligados, verga contra areia e limpeza de copa (P-38, P-39). Depois: limpeza de itens.

### 4.8 `stage.js`, `safety.js`, `audio.js`, `hud.js`, `letterbox.js`
- **Palco:** ticking area só durante a obra, com prazo de 60 s depois do filme e nome gravado para limpar após crash (P-40).
- **Segurança:**
  - noite fixa na hora certa para a Lua (P-42), sem mobs (P-41) e HUD do jogador escondido;
  - tag `cinematic_busy` no jogador durante o filme (P-51);
  - estado original gravado para restaurar após crash (P-44).
- **Áudio:** mix 2D na cutscene e posicional para quem está fora, nos mesmos ticks (P-45), com pré-decodificação ao abrir o menu (P-46).
- **HUD:** PNGs assados por canal (P-25).
- **Letterbox:** canal `LB` = altura da barra em % da meia-tela (99 = fechado), pela largura (P-17).

### 4.9 `cutscene.js`: o orquestrador
`startFilm({ event, system, world, mc, player, target, options })`:
1. confere a tag `cinematic_busy` e monta o `layout` do evento;
2. cria `scheduler`, `clock`, `arbiter`, `ui`, `persist` e, se ligado, o `profiler` (proxies que contam chamadas nativas);
3. roda os módulos do evento na ordem (a câmera antes de quem usa `ctx.pose`) e dá a prioridade padrão por nome de módulo;
4. adiciona o hook final de `ui.flush` e dá `clock.start()`;
5. no `onStop`, roda os teardowns em ordem inversa, imprime o relatório do profiler e mede a obra pós-filme.

### 4.10 O `ctx` que todo módulo recebe
```js
ctx = {
  system, world, mc, player, dimension, target, options,
  layout,                         // G, O, F, R, U, toWorld(), orbit(), groundY(x, z)
  at(tick, fn, {order, tag}),     // cue no relógio mestre
  frameHooks: [],                 // fn(t), com fn.win = [de, até] e fn.prio
  onTeardown(fn),                 // limpeza (ordem inversa, também no abort)
  pose,                           // câmera do tick: p, rot, fov, roll, basis
  ui, persist, arbiter, profiler, clock, scheduler,
  isValid(e), warn(m), trace(m), say(m),
};
```
**Regra de ouro:** todo hook tem `win`. Hook sem janela roda o filme inteiro e conta no orçamento de todos os ticks (P-05).

---

## 5. Técnica por elemento (buraco negro; detalhes em `docs/VISUAL_TECH.md`)

| Elemento | Técnica | Custo no servidor |
|---|---|---|
| Sombra + anel de fótons + disco dobrado | **Impostor**: partícula `lookat_xyz`, quadro pela inclinação | 1 chamada a cada 2–16 ticks |
| Disco perto da câmera | **Entidade** `sgx_disk`: 5 anéis de cubos finos, Kepler no Molang | 0 por tick |
| Par A/B em órbita | posição por fórmula fechada no cliente (`φ(t)`, `d(t)`) | 0 por tick depois do spawn |
| Ondulações e onda gravitacional | decalque `direction_z` + casca instanciada | 1 por meia-órbita |
| Jatos | `lookat_y` persistente + nós instanciados | ≤ 4 por tick |
| Detritos | **Entidade** `sgx_debris`, espiral e esticamento no Molang | 1 por detrito, ≤ 48 vivos |
| Overlays de tela | JSON UI pelo barramento | 1 título quando muda |
| Cratera | `structure load` de cortes pré-gerados | sob flash, poeira e preto |

O magnetar reaproveita o mesmo motor e a maior parte das técnicas (linhas de campo como `lookat_direction`, a estrela como impostor, o clarão por overlay e pela hora do dia). Ver `docs/MAGNETAR.md` §5.

---

## 6. Identidade (tudo em `spec/project.json`)

| Coisa | Valor |
|---|---|
| Namespace | `singularity:` |
| Scriptevents | `sgx:` |
| Dynamic properties | `sgx:*` |
| Título do barramento | `SGXB…` (limpeza `SGX_CLEAR`) |
| Controles de UI | `sgx_*` |
| Tag do jogador durante o filme | `cinematic_busy` |
| Item | `singularity:core` |

Prefixos próprios em tudo: se o usuário tiver outros addons instalados, nada pode colidir (P-14, P-51).

---

## 7. Opções do jogador e comandos

**Menu do `singularity:core`:** BURACO NEGRO · MAGNETAR · OPÇÕES (i18n EN/PT desde o primeiro dia, P-50).

**OPÇÕES:**
- **Destruição:** completa · leve (só o poço do jato / só a extração de ferro do magnetar) · desligada.
- **Dano às criaturas:** puxão e morte no centro (buraco negro) ou empurrão e queimadura (magnetar).
- **Proteger** contêineres (padrão sim) e outros jogadores (padrão não).
- **Qualidade dos efeitos:** alto · equilíbrio · leve (vem do perfil do pacote).
- **Câmera:** por tick (padrão) · spline nativa (experimental).

**Scriptevents** (`/scriptevent sgx:…`): `play blackhole|magnetar`, `from <t>`, `stop`, `trace`, `gizmos`, `profile on|off|dump`, `quality`, `destroy`, `damage`, `protect`, `cammode`, `areas [clear]`, `mobs`, `spike <n>` (Fase 0).

---

## 8. Testes que travam regressão

- **Motor:**
  - relógio: catch-up, reancoragem, stop idempotente;
  - árbitro: janelas, não-inanição;
  - persistidor: brilho constante ±2 % na troca;
  - recorte: nada visível cortado;
  - câmera: continuidade, cortes, FOV, stutter;
  - pacotes de câmera e título por segundo;
  - i18n: as mesmas chaves e os mesmos `%n` nos dois `.lang`.
- **Spec ↔ código:** `storyboard_data.js` e `timeline_data.js` batem com `spec/` (o `check_spec.py` + um teste em JS).
- **Órbita ↔ áudio:** `binary_math.js` e o sintetizador dão as mesmas 19 meias-órbitas.
- **Silêncio:** nenhum som de cutscene em 600–619, e < −90 dBFS no áudio renderizado.
- **Destruição escondida:** todo corte cai num tick com flash ≥ N3, poeira ativa ou tela preta.
- **Chamadas por tick:** média ≤ 60 e pico ≤ 120 partículas por tick no simulador, por bloco.
- **Cratera:** os `.mcstructure` batem byte a byte com as funções de forma.
