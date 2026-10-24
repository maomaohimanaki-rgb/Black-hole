# templates/ — esqueleto do addon (gerado por `tools/gen_templates.py`)

**Modelos, não arquivos testados no jogo.** Os formatos são os que já funcionaram em aparelho real (out/2026), e os ids e UUIDs vêm de `spec/project.json`. Na F0, copie `templates/BP` e `templates/RP` para a raiz do repositório novo e valide nos dois aparelhos (os testes S-01 … S-10 de `docs/VISUAL_TECH.md`). Este README é copiado de `tools/templates_README.md` a cada geração.

| Arquivo | O que é | Observação |
|---|---|---|
| `BP/manifest.json`, `RP/manifest.json` | pacotes com os UUIDs **estáveis** | o `package.py` troca por UUIDs novos em cada build de teste (P-49) |
| `*/texts/*.lang` | nome, descrição, item e chaves do menu em EN/PT | o nome do item vem de `item.singularity:core` (P-50) |
| `BP/items/sgx_core.json` | o item que abre o menu | sem `display_name` literal |
| `sgx_disk` (BP + RP: entidade, geometria, animação, render controller) | disco de acreção: 5 anéis × 32 cubos de 0,1 unidade (P-30) | `lit` (0–5) acende de fora para dentro: lit = 1 mostra o anel 5, lit = 5 mostra todos. Rotação kepleriana no Molang (`v.ang`) |
| `sgx_debris` (BP + RP) | detrito com espiral e esticamento no Molang | propriedades escritas no SPAWN (P-28); `visible_bounds` 64 (P-31); o evento `singularity:despawn` remove |
| `RP/particles/sgx_p_impostor.json` | impostor (sombra + anel + disco dobrado), flipbook de 8 quadros num atlas 2048×1024 | se a textura não puder variar por variável (S-06), faça um id por inclinação (`sgx_p_impostor_00…08`). Variáveis `Vector3`: `v.lf` (vida, entrada, saída), `v.s` (tamanho), `v.a` (alfa), `v.c0` (cor) |
| `RP/particles/sgx_p_ripple.json` | ondulação no chão (`direction_z`, normal 0, 1, 0,02) | cresce de `v.s.x` a `v.s.y` blocos (meia-largura, P-23) |
| `RP/particles/sgx_p_jet_core.json` | núcleo do jato (`lookat_y`) | o centro da partícula fica no MEIO do jato |
| `RP/particles/sgx_spike_shadow.json` | disco preto para o teste S-01 | — |
| `RP/sounds/sound_definitions.json` | 2D da cutscene (`singularity:sgx2d_<nome sem "sgx_">`) e posicional para quem está fora (`singularity:<id>`, arquivo `_m` mono) | 2D com `is3D: false`, `stream: false`, categoria `ui` (P-45, P-47) |
| `BP/scripts/main.js` | mínimo para o pacote carregar na F0 | o motor entra na F1 |

Texturas e sons **não** estão aqui: saem dos motores Python nas fases F2 e F3. Para a F0, use texturas de teste com números grandes nos quadros.
