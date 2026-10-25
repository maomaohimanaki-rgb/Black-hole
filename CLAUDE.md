# CLAUDE.md — Dooms Day (addon de Minecraft Bedrock)

> Nome decidido em 24/10/2026 (D-01 → T-08): **Dooms Day**. Nos docs do kit ainda aparece "SINGULARITY", que era o nome provisório. Os ids internos (`singularity:`, `sgx:`) continuam valendo.

Addon **novo, do zero**, focado em objetos compactos extremos, com dois eventos cinematográficos com destruição real:
1. **Buraco negro**: par em órbita com o chirp do LIGO, fusão, disco de acreção, jatos, o puxão, a queda pelo horizonte e a evaporação (`docs/STORYBOARD.md`);
2. **Magnetar**: SGR 1806-20 e a erupção de 27/12/2004 (`docs/MAGNETAR.md`), depois do buraco negro.

Não existe código de outro projeto aqui e **não se importa nem se copia nada de fora**. O que existe é conhecimento: o usuário e o Claude já fizeram um addon de cutscene parecido, e as lições viraram as regras de `docs/BEDROCK_PITFALLS.md` e o desenho do motor em `docs/ARCHITECTURE.md`. O motor é escrito aqui, com testes.

## Leia antes de qualquer código (nesta ordem)
1. `docs/STORYBOARD.md`: o filme do buraco negro (direção).
2. `docs/BEDROCK_PITFALLS.md`: 54 armadilhas medidas em aparelho real. Ignorar uma delas custa dias.
3. `docs/ARCHITECTURE.md`: o motor, a estrutura do repositório e a técnica de cada elemento.
4. `docs/ROADMAP.md`: em que fase estamos. **Comece pela F0 (spikes)**, não pelo filme.
5. `docs/VISUAL_TECH.md` e `docs/AUDIO_DESIGN.md` quando chegar nessas partes; `docs/MAGNETAR.md` na F9.
   - **Áudio de verdade:** o motor fica em `audio/` (pacote próprio, com spec próprio em escala B, D-14). Antes de mexer em qualquer som, leia `audio/docs/SOUND_DIRECTION.md`: ciência como gramática (T-16), o vocabulário de fases e o processo. Rodar: `cd audio && python3 tools/synth/render.py` (falha se a ida e volta ou o `psycho.py` reprovar).
6. `docs/DECISIONS.md`: o que já foi decidido e o que falta perguntar.

## Fontes da verdade
- **`spec/*.json` manda no tempo e nos números.** Depois de mexer em `spec/`, rode `python3 tools/check_spec.py`: ele falha em incoerência e regenera `docs/BEAT_TABLE.md`. O `spec/storyboard.json` é gerado por `tools/build_storyboard_json.py`: edite o gerador, não o JSON.
- **`docs/STORYBOARD.md` manda na direção.** Se tempo e direção brigarem, o JSON vence no tick e o texto vence na intenção. Anote a divergência em `docs/DECISIONS.md`.
- **Arquivos gerados nunca se editam à mão:** `timeline_data.js`, `storyboard_data.js`, `RP/ui/hud_screen.json`, geometrias e partículas geradas, `.mcstructure`, texturas assadas, `docs/BEAT_TABLE.md`, `templates/`.

## Quem é o usuário e como ele testa
- Fala **português do Brasil**, informal e com humor ("kkkkk"). Responda no mesmo tom, curto e direto. Ele entende bem de Minecraft e de física (é ele quem traz ideias como o magnetar), mas não programa no dia a dia.
- **Ele quer este projeto independente.** Não sugira reaproveitar arquivos, timelines ou pacotes de outros addons dele.
- Testa importando o `.mcaddon` num **tablet 2304×1440** (aparelho principal, perfil Alto) e num **celular de tela 20:9** (pega erro de Molang e de layout que o tablet não pega). O retorno vem como **vídeo, print ou relatório do profiler** (`/scriptevent sgx:profile on`).
- Cada build de teste precisa de **UUIDs novos** (`tools/package.py` faz isso), senão o jogo acusa pacote duplicado. Só o release usa os UUIDs estáveis de `spec/project.json`.
- Ele prefere ver resultado a ler plano. Entregue o `.mcaddon` testável com 2–4 linhas do que olhar, e explique a técnica só se ele perguntar.
- Já aconteceu de ele achar que uma listra na borda era bug, e era a margem de tela do celular (configuração do jogo). Pergunte antes de "consertar" (P-54).

## Como montar e testar (v0.1.0+)
- `python3 tools/build_all.py`: roda todos os geradores (check_spec → templates → storyboard_data → assets → áudio provisório → UI). **Tudo em `BP/` e `RP/` é gerado, exceto `BP/scripts/`** (só o `storyboard_data.js` é gerado lá dentro).
- `node --test tests/*.test.mjs`: o harness (`tests/harness.mjs` + `tests/mc_stub_loader.mjs`) roda o `main.js` de verdade, os 10 spikes e o filme inteiro com um jogo falso que conta chamadas.
- `python3 tools/package.py`: valida e gera `dist/DoomsDay_<versão>_teste-<n>.mcaddon` com UUIDs novos (`--release` usa os estáveis). A versão fica em `spec/project.json`.

## Convenções do repositório
- Uma fase = branch `feature/fN-<nome>`. Correção depois de release = `hotfix/<versão>`. Merge `--no-ff`, tag `vX.Y.Z` e entrada no `CHANGELOG.md` **em português**, explicando o que mudou e por quê (com o vídeo ou print que motivou, quando houver).
- Comentários de código em português: o **porquê** e a versão em que a decisão entrou (ex.: `// v0.4.1: …`).
- Testes: `node --test tests/*.test.mjs`. Cada fase adiciona testes que travam a regressão do que ela resolveu. **Não entregue com teste vermelho.**
- Ferramentas Python idempotentes. Dependências com `pip install --break-system-packages` se precisar.
- Namespaces e prefixos de `spec/project.json` (`singularity:`, `sgx:`, `SGXB`, `sgx_`, tag `cinematic_busy`). Nada pode colidir com outros addons (P-14, P-51).
- Texto do jogador sempre por chave de tradução (`sgx.*` em `RP/texts/en_US.lang` e `pt_BR.lang`), nunca literal (P-50).

## Regras de desempenho (não negociáveis)
- O gargalo é a **fila da thread do servidor**: conte chamadas nativas por tick antes de escolher uma técnica (P-01, P-02).
- Todo hook com janela (`win`) e prioridade. Trabalho pesado em tarefa fatiada ou sob frame que já cobre a tela.
- Metas em `spec/budgets.json`. O profiler (`sgx:profile`) mede no aparelho; o bench com `node --jitless` estima antes.

## Recursos do kit
- `assets/nasa/starmap_2020_4k.exr`: Deep Star Maps 2020 (NASA SVS), para o anel de Einstein.
- `assets/fonts/`: IBM Plex Mono/Sans e Poppins (OFL) para o HUD e os títulos. Falta uma fonte de apoio para `☉ ⁷ ⁹ → ∞` e uma CJK fina para `黑洞`/`磁星` (P-25).
- `templates/`: esqueleto BP/RP gerado por `tools/gen_templates.py` (modelos para a F0, não testados no jogo).
