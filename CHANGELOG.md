# Changelog — Dooms Day

Formato: versão · data · o que mudou e **por quê**. Builds de teste saem em `dist/DoomsDay_<versão>_teste-<n>.mcaddon`, cada um com UUIDs novos.

## Áudio v5.2 (pacote em `audio/`) · 25/10/2026 — o horizonte vira parede + corte

**Por quê:** o usuário mandou o clipe do *time stop* do ZA WARUDO para estudo. Medido: o tempo parar não é desacelerar. É uma parede de volume constante que aperta por dentro e é CORTADA, com um "tin" e um resto escuro.

- O horizonte (27–30 s) deixou de desacelerar. Agora é parede: o mundo sobe de tom (o azul de quem cai), o estéreo fecha (o anel do universo de fora vira uma linha), o chirp da fusão volta como ar e o coração empurra a parede. Corte no 583,4, o coração do 584 no vazio e o "tin" do último fóton no 590 (T-19).
- Conferido: ida e volta 18/18, ouvido automático aprovado com as medidas novas da parede.

## Áudio v5.1 (pacote em `audio/`) · 25/10/2026 — a música manda no mix

**Por quê:** retorno do usuário: "o mix não parece a mesma música; os SFX matam; o fim parece toque de celular de 2010; a música sozinha dá uns engasgos".

- A música virou a referência do mix: medido, os efeitos ficavam 10–20 dB ACIMA da trilha (a maré +14, o horizonte +13). Agora os efeitos de cama ficam abaixo dela (T-18).
- Os sinos de senoide pura (o "toque de celular") viraram tubos do mesmo órgão, na mesma sala; os estalos de articulação viraram sopro de ar.
- A música ficou sem engasgos: legato de organista, a música renasce no 280 (antes havia 1,7 s de buraco depois da fusão) e os soluços de tempo saíram.
- Conferido: ida e volta 18/18, ouvido automático aprovado, e a música só tem os 4 cortes de propósito.

## Áudio v5.0 (pacote em `audio/`, fora do .mcaddon por enquanto) · 25/10/2026 — trilha nova, do zero

**Por quê:** o usuário achou complicado demais consertar a trilha antiga e pediu para "zerar só a música e manter as ferramentas", com o ofício de Interestelar como referência: órgão de 32 pés com o efeito resultante, ostinato e o relógio.

- Trilha nova em `audio/spec/music.json` + `music.py` + `organ.py`: órgão de tubos aditivo, coral por formantes e o tique do relógio, numa grade de 80 BPM (15 ticks por tempo) com a fusão, os jatos, a maré e o horizonte nos tempos fortes (T-17).
- **32' resultante:** 16' + 10⅔' fazem o ouvido ouvir um Ré0 (18,35 Hz) que nenhum tubo toca. `check_organ.py` prova isso antes de cada render, inclusive depois do corte de 150 Hz do celular.
- `sgx_score_*` e `sgx_rhythm_*` viraram `sgx_music_a/b`. Saíram `score.py`, `rhythm.py` e os specs deles. Diretor, ouvido automático, ida e volta, `act7` e efeitos ficaram.
- Conferido: ida e volta 18/18, ouvido automático aprovado (golpe da fusão +2,2 dB, do horizonte +7,8 dB, respiração do filme 14,5 dB).

## Áudio v4.0 (pacote em `audio/`, fora do .mcaddon por enquanto) · 25/10/2026 — dramaturgia do som

**Por quê:** retorno do usuário sobre o áudio v3.0, ouvido fora do jogo: "a ciência tem que ser gramática, não lei universal". O trecho de 12 a 22 s estava bom, mas o drop dos 11–12 s e a dilatação (21–30 s) eram "bonitos no papel e broxantes no ouvido". Medido: os dois golpes ficavam **abaixo** do build (−3,3 dB na fusão e −1,1 dB no horizonte), o grave sumia no golpe da fusão e a dilatação eram três rampas lineares sem relógio comum.

- O pacote de áudio entra no repositório em `audio/`, primeiro como veio (v3.0) e depois com as mudanças, para o diff mostrar só o que mudou. Ele fica isolado porque o spec dele está em escala B (D-14).
- **Camada de dramaturgia:** `audio/spec/dramaturgy.json` + `director.py` (aplica) + `psycho.py` (mede e reprova o build). Teoria, processo e botões em `audio/docs/SOUND_DIRECTION.md` (T-16).
- **Fusão:** soluços de prenúncio, grave sugado, 90 ms de vácuo e golpe em camadas. **Horizonte:** inspiração, 80 ms de vácuo, TÁ-BOOM, o relógio do mundo despencando, ricocheteando e balançando, suspensão assintótica, coração seco fora do relógio.
- O morph do chirp do v3.0 saiu: a frequência descia até ≈ 40 Hz antes da fusão e reprovava a ida e volta.
- Antes → depois: golpe da fusão −3,3 → +2,2 dB, golpe do horizonte −1,1 → +7,5 dB, grave no golpe da fusão −4,8 → +18 dB, respiração do filme 12,1 → 14,2 dB. Ida e volta 20/20.

## 0.1.1 (em teste) · out/2026 — correções do primeiro teste no aparelho

**Por quê:** o retorno do teste-1 (vídeo, relatos e print do chat) aprovou os 10 spikes e o ritmo da câmera, mas mostrou dois bugs.

- **Câmera presa no fim do S-01 e do S-02:** o `clear()` saía no mesmo tick do último `setCamera` com ease de 0,05 s, e o ease terminava depois religando a câmera livre. Agora a câmera é solta de novo 3 e 10 ticks depois (`releaseCamera`), também no fim do filme e no `sgx:stop`.
- **Erros `camera.pose @535…539` no chat:** o B16–B18 pede FOV 120 e o jogo só aceita até 110. O FOV fica preso em 30–110 (T-14). As mensagens de erro agora trazem o texto do erro, não só a linha (no QuickJS o stack vem sem a mensagem).
- **Menu sem mira válida:** em vez de recusar ("Perto demais…" 4 vezes no print), usa o chão 60 blocos à frente e avisa.
- **F0 concluída:** resultados em `docs/SPIKES.md` e decisões T-13 a T-15.
- Testes: o jogo falso agora recusa FOV fora de 30–110 como o de verdade, e os spikes precisam soltar a câmera depois do último ease (os dois testes ficam vermelhos sem a correção). 54 testes.

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
