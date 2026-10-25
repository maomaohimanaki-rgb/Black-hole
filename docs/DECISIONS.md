# Decisões — tomadas e em aberto (Dooms Day)

Cada decisão tem um ID. Quando o usuário decidir uma em aberto, mova para "Tomadas", com a data e o que mudou no `spec/`.

## Tomadas (out/2026)

- **T-01 · Addon novo, do zero e independente.** Nenhum arquivo, timeline, código ou dependência de outro projeto. Ícone, textos, nome, pacotes, namespace e UUIDs próprios. Só o **conhecimento** de projetos anteriores entra, em forma de regras (`docs/BEDROCK_PITFALLS.md`).
- **T-02 · Focado em objetos compactos extremos.** Dois eventos: **buraco negro** (primeiro) e **magnetar** (o rival, depois).
- **T-03 · Roteiro primeiro, depois áudio sintetizado em Python, depois imagem.**
- **T-04 · Técnica híbrida.** O principal em ossos e Molang (o cliente anima) e em texturas assadas em Python (lente, disco, linhas de campo, overlays).
- **T-05 · O chirp do LIGO como coração do som do buraco negro**, com fase única para som e órbita.
- **T-06 · Destruição real e permanente, opcional.** Desligar, proteger contêineres e jogadores, dano às criaturas.
- **T-07 · i18n EN/PT desde o primeiro dia**, com 3 perfis de qualidade (alto, equilíbrio, leve) no lançamento.
- **D-01 → T-08 · Nome: Dooms Day** (24/10/2026). "Doom" é o destino inevitável, a palavra que se associa a buracos negros, e cobre os dois eventos. Mudou: `spec/project.json` (`title`, `title_note`), nomes dos pacotes e do menu (`tools/gen_templates.py`). **Ficaram:** os ids internos (`singularity:`, `sgx:`, `SGXB`, `sgx_`), o item "Singularity Core / Núcleo da Singularidade" e o título do filme do buraco negro ("SINGULARITY", B22). Trocar o título do filme é só mexer no `events.blackhole.title` e no B22.
- **D-02 → T-09 · Duração: 36 s** (720 ticks), sem corte por enquanto (24/10/2026). Revisitar só se o animatic parecer longo.
- **T-10 · Versões do jogo** (24/10/2026): o usuário está no 1.26.52. `@minecraft/server` 2.10.0 e `@minecraft/server-ui` 2.2.0 são as estáveis dessa versão (conferido no npm).
- **T-11 · Fonte Poppins completa** (24/10/2026): a do kit é um subconjunto (16 KB). Baixar a completa (OFL, Google Fonts) na F3, antes do título assado.
- **T-12 · `.mcaddon` no chat e em `dist/` no repositório** (24/10/2026).
- **T-13 · Resultado da F0** (24/10/2026, `docs/SPIKES.md`): as 10 técnicas passaram, nenhum plano B. Billboard de entidade usa `q.rotation_to_camera` (o `q.camera_rotation` não segue a câmera da cutscene). Impostor = 1 id de partícula com as inclinações em linhas do atlas (`v.incl`). Estéreo 2D vale (pan do Doppler fica). `poly_mesh` disponível.
- **T-14 · FOV máximo 110** (24/10/2026). O storyboard pede 120 no fim do B16 e no B17; o jogo só aceita 30–110. O motor prende em 110. *Divergência JSON × jogo:* o efeito de "lente olho de peixe" do 120 vai precisar vir de overlay (anel de aberração, canal `AB`) na F6.
- **T-15 · Ritmo de câmera do animatic aprovado** (24/10/2026). A duração de 36 s fica (D-02/T-09 confirmado).
- **T-16 · Ciência como gramática, não como lei** (25/10/2026, pedido do usuário). A física dá as condições de contorno (o chirp sobe até a fusão, o desvio para o vermelho afina e desacelera junto, a taxa tende a zero no horizonte). A **forma** (antecipação, vácuo, golpe, contorção, prenúncios) é direção, escrita em `audio/spec/dramaturgy.json` e cobrada pelo ouvido automático (`audio/tools/synth/psycho.py`). Teoria e processo: `audio/docs/SOUND_DIRECTION.md`. Primeira aplicação: a fusão (240) e o horizonte (540). *Divergência registrada:* o storyboard pedia, no B16–B17, rampas de reprodução (1,0 → 0,5 e 0,5 → 0,05). Os ticks continuam valendo, mas a forma agora é a curva do diretor (o texto vence na intenção: "o tempo parando").

## Em aberto (decidir antes ou durante a fase indicada)

- **D-03 · Tamanho da cratera.** Esfera de raio 30 (~60 blocos de largura, ~28 de fundo). Maior que isso pesa no motor do mundo (P-06). *Quando: F6.*
- **D-04 · O que acontece com o jogador.** Proposta: o corpo fica onde estava (mira a ≥ 40 blocos). Alternativa mais dramática: o jogador também é puxado (só dentro do raio, e com "Proteger jogadores" desligado). *Quando: F6.*
- **D-05 · Anel de Einstein com estrelas da NASA.** É bonito, mas não casa com o céu do Minecraft atrás. Proposta: fraco e só perto da sombra, no B11. Alternativa: uma casca de céu da NASA só durante o B11. *Quando: F3/F5.*
- **D-06 · O que fica depois do filme.** Proposta: nada além da cratera com a borda brilhando por ~60 s. Alternativa: um "eco" leve e permanente sobre a cratera, que o jogador liga ou desliga. *Quando: F7.*
- **D-07 · Mira em água ou oceano.** A cratera no mar faz o motor simular fluido (P-37). Proposta: vedar a água num raio de 32 antes do corte e avisar no LEIA-ME. Alternativa: recusar mirar na água. *Quando: F6.*
- **D-08 · Spline nativa no horizonte.** O stutter do B17 é natural no modo tick e estranho na spline. Proposta: o B17–B19 sempre em modo tick, mesmo com a spline ligada. *Quando: F6.*
- **D-09 · Ícone e identidade visual.** O ícone do pacote e o do item (`singularity:core`) são do addon, feitos do zero: sombra com anel de fótons e disco dobrado (o próprio impostor) e uma variante azul-elétrica para o magnetar. *Quando: F3.*
- **D-10 · Créditos.** LIGO/Virgo (forma do chirp, GW150914), NASA SVS (mapa de estrelas), artigos do flare de 2004 (magnetar) e fontes OFL (IBM Plex, Poppins). *Quando: F8.*
- **D-11 · Magnetar e o ferro do jogador.** A armadura de ferro do jogador e dos outros também é puxada? Proposta: só visualmente (partículas), nunca tirar item de ninguém. *Quando: F9.*
- **D-12 · Magnetar e redstone.** Piscar lâmpadas de redstone no clarão seria lindo, mas mexe na máquina dos outros. Proposta: não mexer. *Quando: F9.*
- **D-13 · Duelo.** Um terceiro evento, "magnetar caindo no buraco negro", depois dos dois prontos. *Quando: depois da v2.0.*
- **D-14 · Reconciliar o pacote de áudio com o jogo.** O pacote em `audio/` veio de uma linha paralela: `spec/layout.json` em escala B (O a 49 blocos, mira mínima 60, cratera de raio 45) e `spec/audio_cues.json` com a trilha e o ritmo como sons (`sgx_score_*`, `sgx_rhythm_*`). O jogo no repositório continua na escala A com o áudio provisório. Proposta: quando o mixdown for aprovado no tablet e no celular, levar a escala B e os sons para o `spec/` do jogo numa fase só (F2), com o `check_spec.py`. *Quando: fim da F2.*
