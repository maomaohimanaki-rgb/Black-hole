# Testes de renderização da Fase 0 (spikes)

Cada teste é um `/scriptevent sgx:spike <n>`. Ele monta a cena **na frente do jogador**, escreve no chat o que olhar e se desfaz sozinho (`/scriptevent sgx:stop` para no meio). Pergunta, montagem e plano B de cada um: `docs/VISUAL_TECH.md` §10.

**Como testar:** mundo plano ou campo aberto, de noite fica mais fácil de ver. Fique em pé olhando para o horizonte (os testes usam a direção do seu olhar). Mande print ou vídeo de cada um, no **tablet** e no **celular**.

| ID | Pergunta | Tablet | Celular | Decisão |
|---|---|---|---|---|
| S-01 | Disco 3D na frente da sombra e a sombra na frente do lado de trás do disco? | ⏳ | ⏳ | |
| S-02 | `q.camera_rotation` / `q.rotation_to_camera` seguem a câmera da cutscene? | ⏳ | ⏳ | |
| S-03 | Cubos de 0,1 unidade + `entity_emissive` renderizam? | ⏳ | ⏳ | |
| S-04 | Detrito com osso deslocado 30 blocos continua visível com a origem fora da tela? | ⏳ | ⏳ | |
| S-05 | Som 2D estéreo toca estéreo (esquerda → direita)? | ⏳ | ⏳ | |
| S-06 | Partícula escolhe a linha do atlas por variável (`v.incl`) e anima por idade? | ⏳ | ⏳ | |
| S-07 | `poly_mesh` em geometria de entidade funciona? | ⏳ | ⏳ | |
| S-08 | Letterbox em 3,2:1 e fechamento total no 20:9, sem vazar nas bordas? | ⏳ | ⏳ | |
| S-09 | FOV respirando ±5° a cada 3 ticks fica liso? | ⏳ | ⏳ | |
| S-10 | `applyImpulse` a cada 4 ticks puxa as vacas liso, sem "teleporte"? | ⏳ | ⏳ | |

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

## Resultados

(preencher com data, aparelho e o que foi visto; anexar print/vídeo no chat)
