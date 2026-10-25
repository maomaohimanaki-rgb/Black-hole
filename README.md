# Dooms Day

Addon de Minecraft Bedrock com dois eventos cinematográficos sobre objetos compactos extremos, com destruição real: o **buraco negro** (par em órbita com o chirp do LIGO, fusão, disco, jatos e a queda pelo horizonte) e depois o **magnetar** (SGR 1806-20).

**Estado:** 0.1.0 em teste. São os 10 testes de renderização da F0 e o animatic do buraco negro em caixas cinzas (F1). Ver `CHANGELOG.md` e `docs/ROADMAP.md`.

## Instalar (teste)
Abra `dist/DoomsDay_<versão>_teste-<n>.mcaddon` no aparelho (cada build tem UUIDs novos) e ative os dois pacotes no mundo. Jogo 1.26.50 ou mais novo.

## Comandos
| Comando | O quê |
|---|---|
| `/give @s singularity:core` | o item que abre o menu |
| `/scriptevent sgx:play blackhole` | animatic do buraco negro (mira no chão a 40–128 blocos; sem mira, usa 60 blocos à frente) |
| `/scriptevent sgx:from <tick>` | começa o animatic no meio (ex.: `sgx:from 460`) |
| `/scriptevent sgx:stop` | para filme ou teste e restaura o mundo |
| `/scriptevent sgx:spike <1–10>` | testes de renderização da F0 (`docs/SPIKES.md`) |
| `/scriptevent sgx:trace on\|off` | bloco e tick na actionbar |

## Desenvolvimento
```
python3 tools/build_all.py        # todos os geradores (spec → BP/RP)
node --test tests/*.test.mjs      # testes
python3 tools/package.py          # dist/*.mcaddon com UUIDs novos
```
Leia primeiro o `CLAUDE.md`. Ele diz a ordem dos docs e o que nunca se edita à mão.

## Motor de instrumentos chineses (`huayin/`)
Ferramenta Python à parte, independente do addon: **华音 Huayin** sintetiza por modelagem física 41 instrumentos clássicos chineses (pipa da dinastia Tang, guqin, guzheng, erhu, dizi, suona, sheng, 编钟, gongos da ópera…), com técnicas, 简谱, MIDI, mixer e exportação `.ogg`. Manual em [`huayin/README.md`](huayin/README.md).
