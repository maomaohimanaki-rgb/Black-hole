# Áudio — como fazer o som de um buraco negro

No espaço não tem som, então o filme tem que **inventar um som que pareça verdade**. A regra é: cada som nasce de um fenômeno real, transposto para o ouvido. O caso mais forte é o **chirp**, que não precisa de tradução: a onda gravitacional que o LIGO mediu em 14/09/2015 (GW150914) já estava na faixa audível, subindo de 35 para ~250 Hz em 0,2 s. A gente só estica o tempo.

Todo o som é **sintetizado em Python** a partir de `spec/audio_cues.json`. Nenhum sample de terceiros é usado, então não há direitos para creditar além da referência científica (LIGO, NASA).

---

## 1. Pipeline

```
spec/audio_cues.json  (+ spec/layout.json para o chirp)
  └─ tools/synth/render.py         → build/stems/<id>.wav (44,1 kHz, float32; estéreo e mono)
  └─ tools/synth/master.py         → normaliza (−16 LUFS integrado, pico −1 dBFS), exporta .ogg (Vorbis q6)
                                     RP/sounds/singularity/<id>.ogg (2D estéreo) e <id>_m.ogg (mono, posicional)
  └─ tools/synth/analyze.py        → build/timeline.json (spec/schemas/timeline.schema.json)
                                     + build/report.md (onsets pedidos × detectados, espectrograma PNG por som)
  └─ tools/synth/mixdown.py        → build/singularity_mix.wav: o filme inteiro (36 s) para ouvir no celular ANTES do jogo
  └─ tools/build_timeline.py       → BP/scripts/singularity/timeline_data.js
  └─ tools/gen_assets.py           → RP/sounds/sound_definitions.json (2D e 3D)
```

Dependências: `numpy`, `scipy`, `soundfile` (com libsndfile que grava Vorbis) ou `ffmpeg`, e `pyloudnorm`. Instale com `pip install --break-system-packages` se o ambiente pedir.

**Regra de ida e volta (falha o build):** o `analyze.py` re-detecta os onsets do áudio renderizado (fluxo espectral + envelope RMS a 20 fps). Cada `onsets_intended` tem que aparecer a **±0,5 tick** com `rms_norm` a ±0,15 do pedido. Isso garante que o som e o storyboard batem sem ninguém conferir à mão.

---

## 2. Esquema do `timeline.json`

O `tools/build_timeline.py` lê estes campos e gera o `timeline_data.js` (`SOUND_CUES`, `ONSETS`, `ENVELOPE`). Esquema em `spec/schemas/timeline.schema.json`:

```jsonc
{
  "meta": { "name": "singularity_timeline", "tick_rate": 20, "audio_end_tick": 760, "sources": {...} },
  "events": [
    { "id": 1, "sound": "sgx_void_in", "file": "sgx_void_in.ogg", "tick": 0, "end_tick": 40,
      "volume": 0.9, "pitch": 1.0, "mode": "both", "heard_in_cutscene": true, "heard_outside_cutscene": true,
      "analysis_ref": "sgx_void_in.ogg",
      "onsets_abs": [ { "tick": 0.0, "time_s": 0.0, "strength": 0.4, "rms_norm": 0.2 }, ... ] }
  ],
  "audio_library": {
    "sgx_void_in.ogg": { "duration_s": 2.0, "sample_rate": 44100, "rms_peak": ..., "dominant_hz": ..., "spectral_centroid_hz": ...,
      "onsets": [ { "t_local_s": ..., "strength": ..., "rms_norm": ..., "dominant_hz": ... } ],
      "envelope_rms_norm_20fps": [...], "envelope_dominant_hz_20fps": [...], "envelope_centroid_hz_20fps": [...] }
  }
}
```
`mode` é `"both"`, `"cutscene"` ou `"outside"`, derivado dos dois booleanos.

---

## 3. Receitas (uma por som)

Os números de tempo estão em `spec/audio_cues.json`. Aqui está **como** soar.

### `sgx_void_in` (0–40) · o ar sendo sugado
Ruído rosa → passa-baixa varrendo 400 → 1 500 Hz → reverb longo, **invertido** (o som cresce para dentro em vez de decair). No 12, uma **queda de sub** de 55 para 32 Hz em 0,4 s, com 2º e 3º harmônicos para o celular ouvir. Corta quase a zero no 19, como quem prende a respiração.

### `sgx_point` (20) e `sgx_twin` (40) · nascer de um ponto
- **Brilho:** sino inarmônico (parciais em 2,1 / 3,4 / 5,7 kHz, razões não inteiras), ataque de 2 ms e decaimento de 0,4 s.
- **Soco:** seno de 40 Hz com envelope de 80 ms, saturado (tanh) para gerar harmônicos.
- **Pings:** o brilho repetido a −6, −8 e −9 dB nos onsets seguintes.
- O `sgx_twin` é a mesma receita **um tom abaixo** (×0,85 na frequência, não no tempo).

### `sgx_chirp` (60–240) · o coração do filme

A fase é a **mesma** da órbita visual (`spec/layout.json → binary`):
```
τ(t)     = (240 − t_ticks) / 20                     segundos até a fusão
f_gw(τ)  = 35 · (τ / 9)^(−3/8)                       Hz  (35 no 60 → ~245 no 239)
Φ_gw(τ)  = Φ_c − 2π · 35 · 9^(3/8) · (8/5) · τ^(5/8)   fase da onda (integral fechada de f)
A(τ)     = A_0 · (f_gw / 35)^(2/3)                  amplitude (cresce com a frequência)
h(t)     = A · cos(Φ_gw)
```
**A órbita visual é a mesma fase dividida por 2S** (S = 24): uma meia-órbita é quando `Φ_gw/(2S)` cruza múltiplos de π. É daí que saem os 19 ticks de `half_orbit_ticks` (74 … 236).

**Fazendo o celular ouvir** (P-48): o alto-falante de celular corta abaixo de ~150 Hz, e os primeiros 6 segundos do chirp ficam entre 35 e 60 Hz. Por isso:
1. a fundamental real fica (fone e TV tocam);
2. **saturação suave** (`tanh(3h)/tanh(3)`) gera o 2º e o 3º harmônico, e o cérebro reconstrói a fundamental;
3. uma camada com fase `4·Φ_gw` a −12 dB (140 → 980 Hz) carrega o "desenho" do chirp;
4. **acento** em cada meia-órbita: um clique filtrado (passa-banda 2–4 kHz, 6 ms) com volume = `rms_norm` pedido.

O som **termina seco no tick 240**: nada de rabo, porque o `sgx_merge` assume. Os últimos 30 ms podem ter um fade de 2 ms para não estalar.

### `sgx_merge` (232–252) · a fusão
Pré-roll de 232 a 240: prato sintetizado (ruído filtrado com ressonâncias metálicas) **invertido**, mais ruído subindo. No 240, boom de sub (45 Hz, saturado), estouro de ruído branco de 30 ms e um "tape crunch" (bitcrush curtinho). **O pico tem que cair no tick 240**, conferido pelo analisador.

### `sgx_ringdown` (241–280) · o sino se apagando
Senoide amortecida de 250 Hz com τ de 0,6 s. O ringdown real tem τ ≈ 4 ms; aqui ele está esticado 150×. Por cima, um eco com chorus lento (shimmer) e um parcial a 1,5× bem baixo. A partir do 268, rms < 0,05 (quase-silêncio).

### `sgx_disk_ignite` (280–310) · o disco acendendo
Ruído marrom num passa-banda que varre 300 → 4 000 Hz em 1,5 s: **o centroide sobe junto com a temperatura da cor**. Em cada anel (280, 286, 292, 298, 304), um "whoomp" (ruído com envelope rápido e passa-baixa abrindo) com o volume pedido. Estalos esparsos (granular, 30–80 por segundo) por cima.

### `sgx_disk_loop` (310–420, cutscene) e `sgx_disk_loop_ext` (310–620, fora)
O mesmo rugido, estável. **Doppler:** modulação de amplitude de 1 Hz (a matéria do lado que se aproxima passa uma vez por segundo) e, só no mix 2D estéreo, pan L↔R na mesma fase. A versão `_ext` é mono, mais longa e sem pan, para quem está fora da cutscene: para eles o disco continua lá enquanto o invocador "cai".

### `sgx_jet` (358–400)
Assobio de pré-carga (seno subindo 400 → 3 000 Hz em 2 ticks), **explosão** no 360 (ruído largo com envelope rápido, sub e saturação) e zumbido de **síncrotron**: dente-de-serra de 90 Hz com banda limitada, filtro passa-banda com ressonância varrendo devagar e decaimento até o 400.

### `sgx_pad` (400–460, só cutscene)
Coral sintetizado: síntese por formantes de um "ah" (filtros em 700, 1 220 e 2 600 Hz sobre um trem de pulsos), acorde menor grave (Lá1–Mi2–Dó3), vibrato lento e entrada e saída suaves. É o único momento "musical".

### `sgx_tidal` (420–460)
Estalos: impulsos curtos em filtros ressonantes (madeira 180–600 Hz, pedra 80–300 Hz, Q alto), **esticados 4×** por granulação (o rangido fica longo e grave). Por baixo, ronco contínuo de 30–60 Hz saturado. Os onsets aceleram (420, 430, 438, 446, 452, 457).

### `sgx_fall` (460–540, só cutscene)
Vento: ruído com passa-banda cuja frequência central acompanha a velocidade do pedaço-herói (a mesma curva da câmera). **No 500, whoosh Doppler**: ruído com pan e frequência subindo e descendo rápido, pico no 500. ~~Dilatação a partir do 510: a taxa cai de 1,0 para 0,5 até o 539.~~ **v0.4.0:** o tempo é do diretor (`spec/dramaturgy.json → M2_horizonte`, `docs/SOUND_DIRECTION.md`): soluços em 470/500/518/531, inspiração (o mundo acelera e perde o grave) e vácuo antes do 540. A sala do golpe do 540, de trás pra frente, cresce até o começo do vácuo.

### `sgx_horizon` (540–600, só cutscene)
~~A "mistura" passando por uma parada de fita: taxa 0,5 → 0,05.~~ **v0.4.0:** o ZA WARUDO do filme, em fases (`docs/SOUND_DIRECTION.md` §7): golpe em camadas no 540 (TÁ e o BOOM no tick seguinte), contorção (o relógio do mundo despenca, ricocheteia e balança), suspensão assintótica e escura, a foto congelada e o disco arranhado nas poses da câmera. O coração (552, 566, 584) fica seco e fora do relógio do mundo: dois relógios discordando. **Termina em silêncio digital exato no tick 600** (o analisador confere < −90 dBFS de 600 a 619).

### `sgx_hawking` (620–700)
Ambiente quase inaudível (ruído rosa a −50 dB). Brilhos: senos de 6–14 kHz de 15–40 ms, posições aleatórias com densidade crescendo (Poisson com taxa subindo), mais os 6 onsets marcados mais fortes. A partir do 660, um seno subindo de 2 para 8 kHz bem baixo: a temperatura de Hawking subindo.

### `sgx_burst` (700–760)
Acorde **maior com 9ª** (Ré maior: Ré–Fá♯–Lá–Mi), ataque de vidro (sinos inarmônicos suaves) mais pad que abre, decaimento de 3 s que entra no outro. **Sem sub-grave violento**: é o branco de paz.

---

## 4. Mix e entrega

- **Dois mixes** (PITFALLS P-45):
  - **cutscene:** `singularity:sgx2d_<id>`, `is3D: false`, `stream: false`, categoria `ui`, **estéreo** (confirmar no S-05);
  - **fora:** `singularity:<id>`, posicional em O, **mono**, alcance 256, só para quem não está na cutscene, nos mesmos ticks.
- **Volumes** vêm de `audio_cues.json → volume`. A normalização de loudness é por arquivo, e o `volume` faz o balanço no jogo.
- **Pré-decodificar** (P-46): toque cada som 2D com volume 0,0001 quando o menu do `singularity:core` abrir.
- **Silêncios são parte do som:** 268–279 (rms < 0,05) e 600–619 (nada). O `check_spec.py` falha se algum som de cutscene estiver ativo em 600–619.

---

## 5. Créditos científicos (para o LEIA-ME)
- **LIGO Scientific Collaboration & Virgo:** GW150914, a forma do chirp (frequência, amplitude, massas 36 + 29 → 62 M☉, 3 M☉ irradiados, spin 0,67).
- **NASA:** sonificações de buracos negros (Perseus, M87) como referência de estética, não como material. O mapa de estrelas "Deep Star Maps 2020" (NASA SVS) é usado no anel de Einstein.
