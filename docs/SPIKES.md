# Testes de renderização da Fase 0 (spikes)

Cada teste é um `/scriptevent sgx:spike <n>`. Ele monta a cena **na frente do jogador**, escreve no chat o que olhar e se desfaz sozinho (`/scriptevent sgx:stop` para no meio). Pergunta, montagem e plano B de cada um: `docs/VISUAL_TECH.md` §10.

**Como testar:** mundo plano ou campo aberto, de noite fica mais fácil de ver. Fique em pé olhando para o horizonte (os testes usam a direção do seu olhar). Mande print ou vídeo de cada um, no **tablet** e no **celular**.

| ID | Pergunta | Tablet | Celular | Decisão |
|---|---|---|---|---|
| S-01 | Disco 3D na frente da sombra e a sombra na frente do lado de trás do disco? | ✅ | ✅ | Disco 3D + impostor funcionam juntos (a sombra cobre o lado de trás, os anéis passam na frente). Kepler visível. Fica a técnica do VISUAL_TECH §2.5. |
| S-02 | `q.camera_rotation` / `q.rotation_to_camera` seguem a câmera da cutscene? | ⚠️ | ⚠️ | **Só `q.rotation_to_camera` segue a câmera da cutscene**; `q.camera_rotation` fica parada. Billboard de entidade: usar `rotation_to_camera`. |
| S-03 | Cubos de 0,1 unidade + `entity_emissive` renderizam? | ✅ | ✅ | Cubos de 0,1 unidade + `entity_emissive` ok nos dois aparelhos. |
| S-04 | Detrito com osso deslocado 30 blocos continua visível com a origem fora da tela? | ✅ | ✅ | Espiral + esticamento para o centro ok; nada sumiu com a origem fora da tela. |
| S-05 | Som 2D estéreo toca estéreo (esquerda → direita)? | ✅ | ✅ | Estéreo L→R ok no alto-falante e no fone: o pan do Doppler fica. |
| S-06 | Partícula escolhe a linha do atlas por variável (`v.incl`) e anima por idade? | ✅ | ✅ | Linha do atlas por `v.incl` + quadro por idade ok, sempre virado para a câmera: **impostor com 1 id e várias inclinações num atlas**. |
| S-07 | `poly_mesh` em geometria de entidade funciona? | ✅ | ✅ | `poly_mesh` funciona: o disco pode ser liso (decidir na F5 entre cubos e mesh). |
| S-08 | Letterbox em 3,2:1 e fechamento total no 20:9, sem vazar nas bordas? | ✅ | ✅ | Letterbox até fechar e os 5 flashes ok no 20:9. |
| S-09 | FOV respirando ±5° a cada 3 ticks fica liso? | ✅ | ✅ | Liso com 3 e com 6 ticks: fica o de 3 (B08). |
| S-10 | `applyImpulse` a cada 4 ticks puxa as vacas liso, sem "teleporte"? | ✅ | ✅ | Puxão liso em qualquer direção (até do céu): fica a cada 4 ticks. |
| S-12 | (v0.3.2) Por que a entidade grande some de longe? Placas 1–7: caixa 16/64/120/130/256, placa pesada (60 mil vértices), 6 render controllers, e o buraco negro | ⏳ | ⏳ | O número que some diz a causa. |
| S-11 | (v0.3.1) O buraco negro em malha vira para a câmera do jeito certo, a textura gira sozinha (uv_anim) e espelha por baixo? | ⏳ | ⏳ | Se a frente do disco ficar atrás da sombra: `sgx:cal 1`. Se a textura girar junto com a câmera: somar 2. |

Legenda: ✅ funcionou · ❌ não funcionou (aplicar o plano B) · ⚠️ funcionou com ressalva · ⏳ falta testar.

## O que cada teste mostra

- **S-01** · Disco de acreção (5 anéis numerados, 1 = o de dentro) a 30 blocos, 10 acima do chão, com uma partícula preta (a "sombra") no centro. A câmera dá uma volta em 12 s, 5 blocos acima do plano do disco. **Certo:** a parte da frente dos anéis passa **na frente** do disco preto, e a de trás fica **escondida** por ele.
- **S-02** · Duas placas com seta amarela, e a câmera orbitando. A de cima usa `q.camera_rotation` e a de baixo usa `q.rotation_to_camera`. **Certo:** a placa **gira junto** com a câmera, mesmo que fique de costas (o sinal a gente ajusta). Se ficar parada, o query não enxerga a câmera da cutscene e os billboards vão por partícula.
- **S-03** · Só o anel de fora do disco (anel 5), parado, por 15 s. Ande em volta. **Certo:** anel inteiro, aceso, sem buracos e sem sumir de lado.
- **S-04** · 20 blocos numerados (00–15) caem em espiral para um ponto 14 blocos acima do chão e esticam. A entidade está no chão e só os ossos se mexem. **Certo:** nenhum some quando você vira a câmera para longe do centro, e o comprido aponta para o centro (se não apontar, a gente ajusta a rotação).
- **S-05** · Um bipe que anda da **esquerda para a direita** em 4 s, duas vezes. Escute no alto-falante **e** no fone.
- **S-06** · Quatro placas lado a lado (I0 vermelha, I1 verde, I2 azul, I3 amarela) trocando F0 → F3 a cada 0,5 s, e em cima um "buraco negro" de teste girando o ponteiro (F0 → F7). **Certo:** cada placa mostra a própria cor/linha.
- **S-07** · Um anel laranja liso escrito "MESH", girando. **Certo:** ele aparece. Se não aparecer, o disco fica nos cubos.
- **S-08** · As barras pretas varrem 16:9 → 2,39 → 3,2 → fecham (tela preta) → abrem. Depois vêm 5 flashes: branco, branco-gelo, quente, violeta e preto. **Certo:** barras retas e limpas e nada do título aparecendo como texto. **Atenção (P-54):** listra na borda do celular pode ser a margem de tela do jogo. Antes de chamar de bug, confira em Configurações → Vídeo.
- **S-09** · Câmera parada, FOV oscilando 65 ↔ 75 a cada 3 ticks por 6 s, depois a cada 6 ticks por 6 s. Diga qual dos dois fica melhor.
- **S-10** · 10 vacas em roda são puxadas para o marcador dourado por 8 s e depois somem. **Certo:** movimento contínuo, sem pulos.
- **S-12** · (v0.3.2) Sete placas numeradas lado a lado a 90 blocos e o buraco negro acima delas. Fase 1: a sua câmera; fase 2: câmera livre a 30 blocos das placas (o corpo fica lá atrás); fase 3: câmera livre no seu lugar. **Anote os números que aparecem em cada fase.** Placa 1 = caixa de 16, 2 = 64, 3 = 120, 4 = 130, 5 = 256, 6 = pesada (60 mil vértices, caixa 64), 7 = 6 render controllers (caixa 64).
- **S-11** · (v0.3.1) O buraco negro final (entidade `sgx_bh`, todos os anéis acesos) a 100 blocos. A câmera dá uma volta 17 blocos acima do disco e outra 17 abaixo. **Certo:** (1) a parte da frente do disco passa na frente da sombra e o lado de trás dobrado sobe por cima dela; (2) a esquerda (o lado que vem para a câmera) fica mais azul e mais forte; (3) a textura anda sozinha e não gira junto com a câmera; (4) por baixo a imagem espelha. O 1 e o 3 dependem de convenções do Bedrock que não deu para medir daqui: `/scriptevent sgx:cal <0–3>` acerta sem build novo (bit 0 vira a malha 180°, bit 1 inverte a compensação da textura).

## Resultados

### 24/10/2026 · build 0.1.0 teste-1 · tablet + celular 20:9
- Todos os 10 rodaram. Única falha geral: no fim do **S-01 e do S-02 a câmera ficou presa** (o jogador não voltava para a própria câmera até rodar outro teste ou reabrir o mundo). Causa: o `clear()` saía no mesmo tick do último `setCamera` com ease, e o ease terminava depois. **Corrigido na 0.1.1** (`releaseCamera`: solta de novo 3 e 10 ticks depois), com teste.
- Animatic do buraco negro: **ritmo de câmera aprovado** ("ficou bem bom"), nenhuma câmera apontando para lugar errado. Erros no chat em 535–539: o FOV de 120 do B16–B18 passa do máximo do jogo (110). **Corrigido na 0.1.1** (FOV preso em 30–110), com teste.
- Desempenho no aparelho: 741 ticks, 0 pulados, script 5,3 ms média / 25 ms pico (meta: ≤ 8 típico).
- **F0 concluída:** nenhum plano B foi necessário.

### 24/10/2026 · build 0.1.1 teste-1
- S-01 e S-02: a câmera volta sozinha para o jogador no fim (bug da 0.1.0 resolvido).
- Animatic inteiro sem nenhum erro no chat: 741 ticks, 0 pulados, script 4,5 ms média / 14 ms pico.
- S-02 de novo, mesmo resultado (esperado): `q.camera_rotation` parada e `q.rotation_to_camera` seguindo. O `camera_rotation` lê a câmera do **jogador** (o corpo, que fica parado durante a cutscene) e não a câmera livre do `setCamera`. Por isso ele não serve para billboard em cutscene.
