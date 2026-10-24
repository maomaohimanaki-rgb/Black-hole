# Roadmap — SINGULARITY (buraco negro → magnetar)

**Uma fase = uma branch `feature/fN-<nome>` + tag de versão + `.mcaddon` com UUIDs novos para teste + entrada no CHANGELOG (em português).** O usuário testa no tablet (2304×1440) e no celular (20:9) e responde com vídeo, print ou relatório do profiler. Nada é dado como pronto sem esse retorno.

A ordem existe para reduzir risco: primeiro descobrir o que o Bedrock deixa fazer (F0), depois montar o filme inteiro em "caixas cinzas" (F1), e só então som, imagem e cenas.

---

## F0 — Testes de renderização (spikes) · v0.0.x
**Por quê:** a técnica toda (`docs/VISUAL_TECH.md`) depende de 10 perguntas que só o aparelho responde.
- Addon mínimo: item `singularity:core`, `/scriptevent sgx:spike <1–10>` montando cada teste (S-01 … S-10 da tabela em VISUAL_TECH §10) na frente do jogador, com instrução no chat do que olhar.
- Texturas de teste com números grandes nos quadros, para ler no print.
- **Pronto quando:** `docs/SPIKES.md` tem os 10 resultados (tablet e celular) e a técnica de cada camada está decidida, com o plano B aplicado onde falhou.

## F1 — Esqueleto + animatic · v0.1.0
- Repositório no formato de `docs/ARCHITECTURE.md` §3. **Motor escrito do zero** pelo desenho de `docs/ARCHITECTURE.md` §4 (relógio, árbitro, câmera, UI bus, i18n, persist, cull, profiler, fila de blocos), cada peça com teste no harness de Node.
- `tools/build_storyboard_data.py`: `spec/storyboard.json` → `storyboard_data.js`.
- **Áudio provisório:** um bipe por onset pedido (gerado pelo `tools/synth/placeholder.py`), para o tempo ser ouvido desde o primeiro dia.
- **Filme inteiro em gizmos:** O, A, B (órbita certa), G, disco como anel de partícula simples, jatos como linha, câmera de todos os blocos, letterbox (com 2,7/2,8/3,2/fechado), HUD por canal (texto provisório), flashes, shake, FOV respirando, stutter, preto do 600.
- Menu, OPÇÕES e i18n EN/PT desde já. Mira com distância mínima de 40.
- **Pronto quando:** o animatic roda do 0 ao 740 no tablet sem erro, com `sgx:profile` ≤ 8 ms típico (quase nada pesa ainda), e o usuário aprova o **ritmo da câmera**. É a hora de mudar o storyboard, quando mudar é barato.

## F2 — Motor de áudio · v0.2.0
- `tools/synth/` completo (`docs/AUDIO_DESIGN.md`). Primeiro o **chirp** e o **merge** (o coração), depois o resto.
- `build/singularity_mix.wav` para ouvir antes do jogo.
- Ida e volta: onsets pedidos × detectados (±0,5 tick); silêncio em 600–619 < −90 dBFS.
- **Pronto quando:** o usuário aprova o mixdown no celular e no fone, e o filme no jogo toca com o áudio novo, em sincronia, a 16 TPS.

## F3 — Motor de imagem · v0.3.0
- `tools/bake/bh_engine.py`: traçado de Schwarzschild, disco (temperatura, g⁴, turbulência em loop), impostores por inclinação (só as do plano), impostores pequenos de A/B.
- Texturas do disco 3D, do jato, das ondulações, de bloco para detritos (se não usar o atlas do jogo), anel de Einstein (B11) e overlays (aberração, íris, último fóton, impacto negativo com a pose exata do 240, vermelho).
- HUD assado com fonte de apoio (P-25) e relatório de glifos.
- **Pronto quando:** um "contact sheet" (PNG com todos os quadros-chave) é aprovado, e nenhum PNG passa de 2048.

## F4 — Atos I–III no jogo · v0.4.0
- `binary.js` (órbita no cliente + brilhos de eclipse), `ripples.js` (19 ondulações + casca da onda), fusão, ringdown, FOV respirando, impacto negativo.
- **Pronto quando:** a dança e o chirp estão em sincronia visível (as ondulações batem nos acentos) e o profiler do B07–B08 fica dentro do orçamento.

## F5 — Ato IV (disco e jatos) · v0.5.0
- `disk.js` (entidade + impostor + anel de Einstein; acender de fora para dentro), `jets.js`, poço do 360.
- **Pronto quando:** o plano-herói B11 é aprovado em print e a destruição do poço fica escondida no flash.

## F6 — Atos V–VI (o puxão, a queda e o horizonte) · v0.6.0
- `tidal.js` (detritos com textura do bioma, puxão de mobs), `crater.js` (fatias + grosso no preto + fila depois do filme), `fall.js` (pedaço-herói, cruzamento do disco, aberração, vermelho), `horizon.js` (stutter, íris, último fóton, silêncio).
- Aplicar as regras de mundo (P-36 a P-41): proteção de contêineres, vedação de água, verga contra areia, drops desligados, limpeza de copa, prazo das ticking areas.
- **Pronto quando:** obra pós-filme ≤ 5 s em terreno comum (num projeto anterior, 3,4 s foi possível) e o 600–619 é preto e mudo de verdade.

## F7 — Ato VII e acabamento · v0.7.0
- `hawking.js` (remanescente, encolhimento, faíscas, clarão sem shake), título `SINGULARITY` / `黑洞`, outro de 20 ticks.
- Multiplayer: quem está fora vê o espetáculo e ouve o mix posicional (`_ext` do disco).
- **Pronto quando:** o filme inteiro é aprovado em vídeo.

## F8 — Otimização e lançamento do buraco negro · v1.0.0
- Profiler bloco a bloco (B01…B22), metas de `spec/budgets.json`.
- 3 perfis (Alto, Equilíbrio, Leve), `tools/release.py` com UUIDs estáveis, `LEIA-ME.txt` (PT) + `README_EN.txt`, ícones próprios (D-09), créditos (D-10).
- Teste com algum outro addon de HUD instalado (P-14): o título-barramento não pode aparecer como texto.
- **Pronto quando:** o usuário instala o zip final nos dois aparelhos sem erro de conteúdo.

## F9 — Magnetar: spec e spikes · v1.1.0-alpha
- `docs/MAGNETAR.md` vira `spec/magnetar.json` (keyframes, HUD, flashes), com o mesmo `check_spec.py` estendido. Receitas de áudio em `spec/magnetar_audio.json`.
- Teste **S-11**: laço de linha de campo como emissor instanciado girando no cliente a cada 151 ticks. Teste **S-12**: `setTimeOfDay` por 4 ticks (a noite vira dia) sem piscar a iluminação dos chunks de um jeito feio.
- Decidir D-11 e D-12.

## F10 — Magnetar: som e imagem · v1.1.0-beta
- Síntese: zumbido de rede, pulso de rotação, estalos de crosta, rajadas precursoras, o estalo de 4 ticks, a cauda pulsada e o pad com "whistlers" de VLF.
- Bake: impostor da estrela (halo, polos, rachaduras), textura das linhas, aurora, limalha no chão para o raio do campo.

## F11 — Magnetar no jogo e lançamento · v1.1.0
- Módulos `field`, `star`, `quake`, `flare`, `tail`, `filings`, `sky`, mais a extração de ferro (busca binária, fila de blocos).
- Menu com os dois eventos, LEIA-ME atualizado e os 3 perfis.
- **Pronto quando:** o clarão de 0,2 s e a limalha desenhando o campo são aprovados em vídeo.

---

## Metas de desempenho (de `spec/budgets.json`)

| Métrica | Meta |
|---|---|
| Script por tick | ≤ 8 ms típico · ≤ 14 / 12 / 10 ms (alto / equilíbrio / leve) · 25 ms só em frame preto ou congelado |
| Partículas por tick | média ≤ 60 · pico ≤ 120 |
| Pacotes de câmera e título | câmera 20/s no modo tick (aceito) · títulos só quando mudam |
| TPS no filme | ≥ 16 no pior trecho |
| Obra pós-filme | ≤ 5 s |
| Detritos vivos | ≤ 48 |
| Textura | ≤ 2048 de lado |
