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
