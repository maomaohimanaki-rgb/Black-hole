# BEAT TABLE — gerado de spec/storyboard.json + spec/audio_cues.json

Gerado por `python3 tools/check_spec.py`. Não edite à mão: mude o JSON e rode de novo.

## Ato I — ANOMALIA (ticks 0–79)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B01** O SILÊNCIO ERRADO | 0–19 | sgx_void_in (0, 12, 19) | `ANOMALY DETECTED`@4; `GRAV. GRADIENT +0.003 g`@8 | — | 1@12 |
| **B02** O PONTO | 20–39 | sgx_point (20, 24, 28, 32) | `SINGULARITY · A`@20; `MASS 36 M☉`@22 | N2@20 | 2@20, 1@24 |
| **B03** O GÊMEO | 40–59 | sgx_twin (40, 44, 48) | `SECOND BODY · 29 M☉`@40; `BINARY LOCKED`@50 | N2@40 | 2@40 |
| **B04** A DANÇA COMEÇA | 60–79 | sgx_chirp (74) | `INSPIRAL · f 35 Hz · d 8.0`@60 | — | 1@60 |

## Ato II — INSPIRAL (ticks 80–239)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B05** ESPIRAL | 80–139 | sgx_chirp (87, 99, 112, 124, 135) | `f 37 Hz · d 7.8`@80; `f 39 Hz · d 7.5`@100; `f 41 Hz · d 7.2`@120 | — | 1@80, 2@120 |
| **B06** ACELERAÇÃO | 140–199 | sgx_chirp (146, 156, 166, 176, 185, 194) | `f 44 Hz · d 6.9`@140; `f 50 Hz · d 6.3`@170 | — | 2@140, 3@180 |
| **B07** O GRITO | 200–239 | sgx_chirp (202, 209, 216, 222, 227, 232, 236, 239); sgx_merge | `f 62 Hz · d 5.5`@200; `f 103 Hz · d 3.9`@230; `f 146 Hz · d 3.1`@236; `f 245 Hz`@239 | N1@202, N1@209, N1@216, N1@222, N1@227, N1@232, N1@236, N1@239 | 3@200, 4@222, 5@232, 6@236 |

## Ato III — FUSÃO (ticks 240–279)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B08** FUSÃO / RINGDOWN | 240–259 | sgx_merge (240, 241); sgx_ringdown (241) | `THEY BECAME ONE`@241; `MERGER · 62 M☉`@241; `ΔM = 3.0 M☉ → GRAVITATIONAL WAVES`@246 | N4@240, N3@242 | 10@241, 6@247, 3@250 |
| **B09** O VAZIO RESPIRA | 260–279 | sgx_ringdown | — | — | — |

## Ato IV — DISCO (ticks 280–419)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B10** IGNIÇÃO DO DISCO | 280–309 | sgx_disk_ignite (280, 286, 292, 298, 304) | `ACCRETION`@280; `T 10⁷ K`@300 | N3@304 | 2@280, 3@292, 4@304 |
| **B11** O ANEL | 310–349 | sgx_disk_loop (310) | `SPIN a* = 0.67`@315; `ISCO 3 r_s`@330 | — | — |
| **B12** JATOS | 350–389 | sgx_jet (360, 362) | `RELATIVISTIC JETS`@362; `v = 0.99 c`@365 | N4@360, N3@361 | 10@360, 6@362, 3@366 |
| **B13** O OLHO DO MUNDO | 390–419 | sgx_jet; sgx_disk_loop; sgx_pad (400) | — | — | 1@390 |

## Ato V — O PUXÃO (ticks 420–539)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B14** MARÉ | 420–459 | sgx_tidal (420, 430, 438, 446, 452, 457) | `TIDAL FORCES`@420; `STRAIN 10⁹ g`@430 | N1@446, N1@452, N2@457 | 3@420, 4@430, 5@438, 6@446, 7@452, 8@457 |
| **B15** ESPAGUETE | 460–499 | sgx_fall (460) | `r = 6 r_s`@470; `r = 3 r_s`@485; `r = 1.5 r_s · PHOTON SPHERE`@495 | — | 4@460, 6@480, 7@495 |
| **B16** A QUEDA | 500–539 | sgx_fall (500) | `r → r_s`@505; `z = 9.0`@525 | N3@500 | 7@500, 5@515, 3@530 |

## Ato VI — HORIZONTE (ticks 540–619)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B17** O ÚLTIMO OLHAR | 540–579 | sgx_horizon (540, 552, 566) | `t → ∞`@545; `SIGNAL LOST`@560; `3`@560 | — | 2@540, 1@560 |
| **B18** CRUZAMENTO | 580–599 | sgx_horizon (584) | — | — | — |
| **B19** SILÊNCIO ABSOLUTO | 600–619 | **silêncio** | — | — | — |

## Ato VII — EVAPORAÇÃO (ticks 620–719)

| Bloco | Ticks | Áudio (onsets) | HUD | Flash | Shake |
|---|---|---|---|---|---|
| **B20** DE FORA | 620–659 | sgx_hawking | — | — | — |
| **B21** HAWKING | 660–699 | sgx_hawking (660, 672, 682, 690, 696, 699) | — | N1@660, N1@672, N1@682, N2@690, N2@696, N2@699 | — |
| **B22** O ÚLTIMO CLARÃO | 700–719 | sgx_burst (700) | `SINGULARITY`@704; `黑洞`@706 | N4@700 | — |

## Letterbox (razão de aspecto alvo)

1.78@0 → 1.78@47 → 2.39@79 → 2.39@240 → 2.7@242 → 2.39@246 → 2.39@459 → 2.8@499 → 3.2@539 → 3.2@580 → closed@590 → closed@619 → closed@620 → 1.78@630 → 1.78@719

## Desvio para o vermelho (overlay)

0.0@0 → 0.0@509 → 0.5@539 → 0.95@579 → 1.0@599 → 0.0@600
