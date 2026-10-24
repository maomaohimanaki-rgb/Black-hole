# Changelog — Dooms Day

Formato: versão · data · o que mudou e **por quê**. Builds de teste saem em `dist/DoomsDay_<versão>_teste-<n>.mcaddon`, cada um com UUIDs novos.

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
