# Changelog — Dooms Day

Formato: versão · data · o que mudou e **por quê**. Builds de teste saem em `dist/DoomsDay_<versão>_teste-<n>.mcaddon`, cada um com UUIDs novos.

## Ferramenta: motor 华音 Huayin 1.0.0 · out/2026 — instrumentos clássicos chineses (pasta `huayin/`)

**Por quê:** pedido do usuário: um motor em Python que simule instrumentos chineses clássicos (a começar pelo pipa da dinastia Tang) o mais fiel possível, com tudo que um motor de música precisa e um tutorial para acrescentar coisas. É independente do addon (não entra no `.mcaddon`), mas exporta `.ogg` mono/estéreo que servem de matéria-prima para os sons do filme.

- **Síntese física, sem samples:** guia de onda para cordas (seda, aço-náilon, aço; rigidez, duas polarizações, ponto de dedilhado, atrito do dedo deslizando, ressonância simpática), corda friccionada de McIntyre–Schumacher–Woodhouse para o erhu, jato de ar (dizi/xiao) com a membrana 笛膜, palheta dupla cônica (suona) e cilíndrica (guanzi), palheta livre (sheng), síntese modal para sinos, pedras, gongos, pratos e tambores.
- **41 instrumentos + 7 variantes, 119 técnicas** (轮指, 推拉, 吟猱, 泛音, 滑音, 花舌, 刮奏, 马嘶, 当心画…), com nomes em pinyin, chinês e português. O 编钟 tem os dois tons por sino (正鼓/侧鼓); o 小锣 sobe e o 大锣 desce de altura depois do golpe, como medido por Jossic et al. (JASA 2018).
- **Motor de música:** Musica/Faixa, andamento com rampas, afinações históricas (三分损益, justa, igual de 朱载堉), tons e modos, leitor de 简谱 (`.jp`), JSON, MIDI ida e volta, automação, humanização reproduzível, efeitos (reverbs de palácio Tang, templo, gruta de Dunhuang; EQ, compressor, limitador, eco, chorus), loudness BS.1770, stems e CLI (`python3 -m huayin`).
- **Docs:** `huayin/README.md` (manual), `docs/TUTORIAL.md` (inclui criar instrumento, técnica, corpo, material, afinação e efeito), `docs/PARTITURA.md`, `docs/FIDELIDADE.md` (o que é medido × estimado, fontes) e `docs/INSTRUMENTOS.md` (gerado).
- **Testes:** 39 (`cd huayin && python3 -m unittest discover -s tests -t tests`), travando a afinação de cada modelo físico (corda ±3 cents, erhu e dizi ±8), o sentido do glissando dos gongos, os dois tons do 编钟, o leitor de 简谱, JSON/MIDI e o loudness.

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
