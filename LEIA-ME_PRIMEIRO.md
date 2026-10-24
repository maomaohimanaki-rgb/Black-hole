# Kit de início — SINGULARITY (addon de buraco negro + magnetar)

Este zip é tudo o que o projeto novo precisa para começar **do zero e sem esta conversa**: o storyboard do buraco negro, o conceito e o storyboard do magnetar, o desenho do motor, as armadilhas do Bedrock que já conhecemos, os JSONs de especificação, os modelos de arquivo do addon, as fontes e o mapa de estrelas da NASA. **Não tem nenhum arquivo de outro projeto.**

## O que tem aqui

| Pasta / arquivo | Para quê |
|---|---|
| `CLAUDE.md` | Instruções para o agente do ambiente novo (ele lê sozinho ao abrir o repositório). |
| `docs/STORYBOARD.md` | **O filme do buraco negro.** 7 atos, 22 blocos, tick a tick: câmera, efeitos, som, HUD, flash, tremor. |
| `docs/MAGNETAR.md` | **O rival.** SGR 1806-20 e a erupção de 2004: física conferida (com fontes), linguagem e storyboard em 12 blocos. |
| `docs/BEAT_TABLE.md` | Tabela de beats do buraco negro, gerada do JSON (não editar à mão). |
| `docs/ARCHITECTURE.md` | O motor (desenhado para ser escrito do zero), a estrutura do repositório e a técnica de cada elemento. |
| `docs/BEDROCK_PITFALLS.md` | 54 armadilhas do Bedrock medidas em aparelho real. |
| `docs/VISUAL_TECH.md` | Como cada coisa vira pixel: impostor, disco 3D, detritos, jatos, overlays + 10 testes da Fase 0. |
| `docs/AUDIO_DESIGN.md` | Como sintetizar cada som em Python (o chirp do LIGO com a fórmula exata). |
| `docs/ROADMAP.md` | Fases F0 → F8 (buraco negro) e F9 → F11 (magnetar), cada uma com o critério de "pronto". |
| `docs/DECISIONS.md` | O que já foi decidido e as 13 perguntas em aberto (nome, duração, cratera, ferro do jogador…). |
| `spec/*.json` | Os "Borog Johnsons" 😄: storyboard, áudio, geometria/física, paleta, orçamento, projeto (ids e UUIDs) e os esquemas JSON. |
| `tools/` | `build_storyboard_json.py` (gera o storyboard.json), `check_spec.py` (confere tudo e gera a tabela) e `gen_templates.py` (gera os modelos do addon). |
| `templates/` | Esqueleto do addon: manifests com UUIDs novos, item, disco, detritos, partículas, sons e textos EN/PT. São modelos, não testados no jogo. |
| `assets/` | Mapa de estrelas da NASA (35 MB, para o anel de Einstein) e fontes OFL (IBM Plex, Poppins). |

## Como começar no ambiente novo

1. **Crie o repositório** (por exemplo `singularity-bedrock` no GitHub) e abra uma sessão de código nele.
2. **Mande este zip** para a sessão e peça para descompactar na raiz.
3. **Cole esta primeira mensagem:**

> Esse repositório é um addon novo de Minecraft Bedrock, do zero: SINGULARITY, com dois eventos (buraco negro primeiro, magnetar depois). Descompacta o kit na raiz, lê o CLAUDE.md e os docs na ordem que ele manda e roda `python3 tools/check_spec.py`. Começa pela Fase 0 do ROADMAP: monta o addon mínimo a partir de `templates/` e os 10 testes de renderização (`/scriptevent sgx:spike 1…10`). Me entrega o .mcaddon com UUIDs novos e me diz o que olhar em cada teste. Antes, me pergunta as decisões D-01 (nome) e D-02 (duração) do DECISIONS.md.

4. **Teste no tablet e no celular** e mande print ou vídeo de cada spike. É assim que a técnica fica decidida antes de gastar tempo com o filme.

## Antes de começar, vale decidir
- **D-01 · Nome.** Está como "SINGULARITY". Como agora são dois eventos, também servem "Collapse", "Dead Stars / Estrelas Mortas", "Remnants" ou "Event Horizon".
- **D-02 · Duração.** O buraco negro tem 36 s e o magnetar 30 s. Dá para cortar o buraco negro para ~33 s depois de ver o animatic.
