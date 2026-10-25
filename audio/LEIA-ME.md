# Dooms Day: só o áudio do filme do buraco negro (36 s), versão 0.2.7

Tudo que gera o som: 20 arquivos (16 efeitos + trilha em 2 partes + camada rítmica em 2 partes), sintetizados do zero em Python, sem nenhum sample.

## Rodar
```
pip install --break-system-packages -r tools/requirements.txt     # numpy, scipy, pyloudnorm, matplotlib (+ ffmpeg com libvorbis no sistema)
python3 tools/synth/render.py            # gera tudo (~1 min); --quick pula os espectrogramas
python3 tools/build_timeline.py          # opcional: gera o timeline_data.js que o jogo lê
```
**Saídas:**
- `RP/sounds/singularity/*.ogg`: os sons do jogo. `<id>.ogg` é o estéreo 2D da cutscene e `<id>_m.ogg` é o mono posicional, para quem está fora.
- `build/singularity_mix.wav` / `.mp3`: o mixdown do filme inteiro, como se ouve na cutscene.
- `build/stems/<id>.wav`: cada som separado. `build/report.md` traz os onsets pedidos × medidos e o volume.

O render **falha** se a "ida e volta" não bater: cada onset de `spec/audio_cues.json` tem que ser re-detectado no áudio a ±0,5 tick e com o rms pedido ±0,15, e 600–619 tem que ser silêncio digital. Para ver por que um som falhou: `python3 tools/synth/diagnose.py sgx_jet`.

## A ordem (o que roda, de onde vem)
1. **`spec/audio_cues.json`**: QUAIS sons existem, QUANDO tocam (tick de 1/20 s), o volume no jogo e os onsets que cada um tem que ter.
2. **`spec/score.json`**: a TRILHA como dado (pedal, órgão, coral, dinâmicas, relógio, Shepard–Risset, reverb, os trechos de silêncio e o `act7`, que é o Ato VII pelo ponto de audição).
3. **`spec/rhythm.json`**: a CAMADA RÍTMICA (baixo, tom, shaker, poeira, tique-taque, subidas) na grade do filme.
4. **`spec/layout.json`**: a física de que o som depende (as 19 meias-órbitas, que são o relógio do chirp e do ritmo).
5. **`tools/synth/render.py`**: para cada som do `audio_cues`, chama a receita → calibra os ganhos → masteriza (−16 LUFS, pico −1 dBFS) → exporta → analisa → monta o mixdown.

## Os scripts
| Arquivo | O quê |
|---|---|
| `tools/synth/dsp.py` | primitivas: ruídos, filtros, envelopes, saturação, a catedral (reverb), estéreo compatível com mono |
| `tools/synth/gw.py` | **a identidade**: o gesto GW150914 (fusão / nascimento invertido), o gesto como ar, o congelamento espectral e o stutter |
| `tools/synth/recipes.py` | as receitas dos 16 efeitos + as entradas da trilha e do ritmo |
| `tools/synth/score.py` | a trilha a partir do `score.json` |
| `tools/synth/rhythm.py` | a camada rítmica a partir do `rhythm.json` |
| `tools/synth/act7.py` | Ato VII: zumbido, mundo abafado, drop-out, estéreo abrindo |
| `tools/synth/analyze.py` | a ida e volta (rms por tick, detecção de onsets em 4 bandas) |
| `tools/synth/render.py` | o maestro (ver "A ordem") |
| `tools/synth/diagnose.py` | por que um onset falhou |
| `tools/build_timeline.py` | `build/timeline.json` → `BP/.../timeline_data.js` |
| `jogo/audio.js` | como o jogo toca: cada som no seu tick (2D para quem assiste, posicional em O para os outros) |
| `docs/AUDIO_DESIGN.md` | o desenho original de cada som (a versão atual está nos comentários das receitas) |

Os ticks seguem o storyboard: 0–79 Ato I, 80–239 Inspiral, 240 a fusão, 280–419 Disco, 420–539 Maré e queda, 540–599 Horizonte, 600–619 silêncio absoluto, 620–759 Evaporação.
