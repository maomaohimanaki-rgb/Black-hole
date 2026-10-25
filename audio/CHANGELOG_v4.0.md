# Dooms Day áudio v4.0 (v0.4.0 do áudio) · 25/10/2026 · dramaturgia

**Por quê:** retorno do usuário sobre o v3.0: "a ciência tem que ser gramática, não lei universal". De 12 a 22 s o ritmo estava legal, mas o drop dos 11–12 s e a dilatação (21–30 s) eram "bonitos no papel e broxantes no ouvido". Medido: os dois golpes ficavam **abaixo** do build (−3,3 dB na fusão, −1,1 dB no horizonte), o grave **sumia** no golpe da fusão e a dilatação eram três rampas lineares sem relógio comum.

## O que mudou
- **Nova camada: a dramaturgia** (`spec/dramaturgy.json` + `tools/synth/director.py`). Não cria som, dirige o que existe: papéis (mundo / sinal / evento), fader de tensão, e os momentos escritos em fases (soluço, inspiração, vácuo, golpe, contorção). A teoria, o processo e os botões estão em `docs/SOUND_DIRECTION.md`.
- **O ouvido automático** (`tools/synth/psycho.py`): mede o mix como o corpo sente e reprova o build. Golpe acima do build, grave que volta, celular ouvindo o golpe, ataque mais nítido, relógio não-linear, respiração do filme.
- **Fusão (240):** soluços em 202 e 216, o grave sugado enquanto o chirp sobe sozinho, 90 ms de vácuo e golpe em camadas.
- **Horizonte (540), o ZA WARUDO:** soluços cada vez mais fundos, inspiração (o mundo acelera e perde o grave), 80 ms de vácuo, TÁ-BOOM, contorção (0,2 → 0,74 → balanço de 3,4 Hz), suspensão assintótica e escura, coração seco fora do relógio do mundo.
- **Chirp:** saiu o morph do v0.3.2, que fazia a frequência descer até ≈ 40 Hz antes da fusão (o riser murchava antes do drop), saía de fase com a órbita e reprovava a ida e volta em 202 e 216.
- **Golpes não são mais normalizados a −16 LUFS** (régua de cama): pico em −1 dBFS. Era isso que deixava o golpe sem espaço.
- Saíram as três rampas lineares (vento 1,0 → 0,5, trilha 1,0 → 0,25 e horizonte 1,0 → 0,35) e o abaixa-volume do 540 na trilha. Tudo isso agora vem de um relógio só.
- `spec/rhythm.json`: os golpes de morph do 540 em diante saíram (a contorção faz isso). O tique-taque do Ato VI agora é regular no tempo do mundo, e o relógio do diretor é que o desacelera.

## Medidas (antes → depois)
Golpe da fusão −3,3 → +2,2 dB · grave no golpe da fusão −4,8 → +18 dB · golpe do horizonte −1,1 → +7,5 dB · celular no horizonte 0,0 → +13,5 dB · respiração do filme 12,1 → 14,2 dB. Ida e volta: 20/20 (o v3.0 reprovava o chirp).
