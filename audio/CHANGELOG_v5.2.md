# Dooms Day áudio v5.2 · 25/10/2026 · o horizonte vira parede + corte

**Por quê:** o usuário mandou o clipe do *time stop* do ZA WARUDO para estudo. Medido: não é desacelerar. É uma parede de volume constante que aperta por dentro (um grave subindo, metal, um apito que sobe, o estéreo fechando) e é CORTADA (−20 dB em menos de 10 ms), com um "tin" e um resto escuro.

## O que mudou
- Fase nova do diretor, `wall`: volume constante, o mundo sobe 3 semitons (o azul de quem cai), o estéreo fecha até 6 % (o anel do universo de fora vira uma linha), o pente aperta e, no `cut`, o mundo some em 5 ms. Substitui a contorção (`warp`) no horizonte.
- Horizonte (`sgx_horizon`): golpe no 540; o chirp da fusão volta como ar subindo; ar no agudo; o coração empurra a parede (*sidechain*); corte no 583,4 (o coração do 584 cai no vazio); "tin" do último fóton no 590; resto grave escuro até o preto do 600. Saíram a foto congelada e o disco arranhado (a parede é a própria trilha).
- `psycho.py`: medidas da parede (plana, o estéreo fecha, o corte apaga o mundo) no lugar das da contorção.
- Calibrador: zona morta 0,03 → 0,07.
- Docs: `docs/SOUND_DIRECTION.md` §12.

## Conferido
Ida e volta 18/18 · ouvido automático aprovado (parede plana 4,3 dB, estéreo fecha 13 dB, corte de 95 dB no agudo, golpe do horizonte +11 dB, respiração 15 dB). Lado a lado com o clipe: mesma anatomia.
