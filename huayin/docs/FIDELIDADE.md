# Fidelidade: a física, a pesquisa e os limites

O objetivo do Huayin é soar **o mais perto possível** dos instrumentos reais usando só física e
processamento de sinal, sem gravações. Este documento diz, instrumento por instrumento, **o que é
simulado**, **de onde veio cada número** e **onde a aproximação fica fraca**. Legenda:

- **[medido]** — valor tirado de medição publicada ou de um padrão (afinação, norma).
- **[física]** — consequência direta do modelo físico (não foi "ajustado").
- **[estimado]** — escolhido a partir da física típica de instrumentos parecidos e do ouvido.
- **[calibrado]** — ajustado medindo a saída do próprio motor (os testes travam o valor).

---

## 1. Os modelos físicos

### 1.1 Corda (pipa, guqin, guzheng, ruan, liuqin, yueqin, sanxian, konghou, se, yangqin)

Guia de onda digital de laço único (Karplus-Strong estendido; Jaffe & Smith 1983, Välimäki et al.
1996, o mesmo tipo de modelo usado para o guqin por Penttinen et al., JASA 2006):

- **Atraso fracionário variável por amostra** (Lagrange cúbica): bends, vibratos e slides mudam o
  comprimento da corda de verdade, então as parciais acompanham juntas. **[física]**
- **Filtro de perda** projetado a partir de dois pontos de T60 do material com σ(f) = b₁ + b₃f²
  (Chaigne & Askenfelt 1994; Bensa et al. 2003). Seda: agudos morrem rápido; aço: quase nada. **[estimado]**
- **Rigidez** por passa-tudos de dispersão: parciais fₙ = n·f₀·√(1+Bn²); o coeficiente é buscado
  numericamente para bater as 16 primeiras parciais. Ao apertar a corda, B cresce com (f/f_solta)²
  porque B ∝ 1/L². **[física]** (valores de B **[estimado]**)
- **Ponto de dedilhado**: a força na ponte de uma corda pinçada é uma onda retangular com ciclo igual
  ao ponto β, coeficientes ∝ sin(nπβ)/n — perto da ponte soa metálico, no meio soa redondo. **[física]**
- **Largura do contato** (polpa × unha × palheta) e **força** filtram a excitação: pinçada forte é mais
  brilhante, como nas cordas reais. **[física]** + **[estimado]**
- **Duas polarizações** (vertical acopla mais com o tampo e morre antes; horizontal sustenta) com
  ~0,8 cent de diferença: dá a "dupla queda" e o batimento lento das cordas reais. **[física]**
- **Modulação de tensão**: dedilhado forte começa agudo e assenta (forte na seda frouxa do guqin). **[física]**
- **Corte por corda**: um novo golpe na mesma corda abafa o anterior (o dedo/palheta para a corda);
  baquetas do yangqin **não** abafam — os golpes são somados na mesma corda (exato, porque a corda é
  linear). **[física]**
- **Atrito do dedo deslizando** (guqin, pipa, sanxian): ruído filtrado cuja ressonância = velocidade
  do dedo × enrolamentos por metro, a mesma ideia do modelo de Penttinen et al. 2006 para o guqin. **[física]**
  (enrolamentos/m **[estimado]**)
- **Harmônicos (泛音)**: o dedo no nó 1/n deixa só a série n·f₀ da corda inteira. **[física]**
- **Corda percutida (yangqin)**: pulso de contato do martelo, espectro ∝ sin(nπβ)·H(f) sem o 1/n da
  pinçada; contato mais curto em golpes fortes (Hall 1986). Cursos de 2–4 cordas levemente
  desafinadas (batimento e queda em dois estágios). **[física]**
- **Ressonância simpática**: cordas soltas como pentes realimentados excitados pela soma. **[física]**
- **Choque não linear** (绞弦 do pipa, 煞音, chiado de pele do sanxian): limitador suave dentro da malha. **[estimado]**

**Afinação medida pelos testes:** fundamental a menos de 3 cents em seda, aço-náilon e aço de 65 Hz a
880 Hz (`tests/test_afinacao_fisica.py`). **[calibrado]**

### 1.2 Corpo

Banco de ressonadores modais (Hz, T60, ganho) aplicado à soma da faixa (síntese "comutada", Smith
1993; exato para sistema linear). Os modos de cada caixa são **[estimado]**: guiados pela física de
caixas de paulównia/madeira dura, pelos tamanhos dos instrumentos e pela literatura abaixo, mas **não**
são medições de um exemplar. É o maior ponto de melhoria possível (ver §4).

- **Erhu:** o ressonador se comporta como um tubo fechado de um lado pela pele (modos ímpares 1:3:5) e
  a membrana divide cada modo em fase/antifase com o ar; a literatura citada pela página de acústica
  do erhu da UBC aponta o 1º modo da membrana em ~2 kHz. Os modos do corpo `erhu` foram montados assim
  (tubo ~660 Hz + membrana ~2 kHz). **[estimado a partir de fonte secundária]**

### 1.3 Arco (erhu, gaohu, zhonghu, banhu, jinghu)

Corda friccionada de McIntyre, Schumacher & Woodhouse (1983) na forma de guia de onda de Smith/STK:
curva de atrito hiperbólica (grudar-escorregar), dois trechos de corda (pestana e ponte), filtro na
ponte. O que sai "de graça" da física: movimento de Helmholtz, transiente de ataque, **troca de arco**
(a velocidade passa por zero e inverte), ruído de crina e o som "assobiado" com pouca pressão. **[física]**

Detalhe importante: o erhu não tem espelho e o arco fica parado enquanto o dedo encurta a corda, então
o **ponto relativo do arco sobe com a nota** (β = β₀·f/f_solta). Sem isso o modelo pulava de modo nas
notas agudas — com isso, fica estável de ré4 a lá6 (medido). **[física]** **[calibrado]**: ±5 cents.

### 1.4 Sopros

- **Dizi/xiao:** modelo de jato de Cook/STK (jato oscilando sobre a borda, não linearidade x³ − x,
  tubo com reflexão filtrada, ruído de sopro). Como no STK, o tubo é ajustado para 2/3 da nota (o jato
  alimenta o modo cuja fase fecha com meio período de trânsito) e uma tabela de correção mede e
  compensa o resto. **[física]** + **[calibrado]** (±8 cents de ré4 a dó7).
  **Limite:** abaixo de ~290 Hz o modelo pula de modo (o motor avisa).
- **笛膜 (membrana do dizi):** oscilador de Duffing amortecido excitado pela pressão do tubo. Tsai
  (2003, tese "The Chinese Membrane Flute (Dizi): Physics and Perception of its Tones") mostra que a
  membrana reforça os harmônicos altos e que as **rugas reduzem a não linearidade** (evitando saltos);
  daí o amortecimento alto e a não linearidade moderada. Frequência de ressonância **[estimado]**.
- **Suona:** palheta dupla + tubo cônico (duas linhas de atraso, forma "Saxofony" do STK) e radiação
  forte de agudos da campana de cobre. Estável sem pular oitava com pressão 0,45–0,75 e posição 0,4
  (medido). **[física]** + **[calibrado]**
- **Guanzi/bili:** palheta + tubo cilíndrico (forma "Clarinet" do STK): quase só harmônicos ímpares. **[física]**
- **Sheng, hulusi, bawu (palheta livre):** a lingueta de latão passa pela fenda e solta pulsos curtos
  de ar; a radiação é a derivada do fluxo; o tubo acima reforça os seus harmônicos; sopro forte sobe a
  afinação alguns cents (comportamento real de palhetas livres). **[física]** (forma do pulso **[estimado]**)
- **Xun:** ressonador de Helmholtz (quase senoidal) + muito ar. **[física]** simplificada.

### 1.5 Idiofones e membranas (síntese modal)

Cada modo é uma senoide amortecida com amplitude dependente do **ponto de golpe** e filtrada pela
**dureza da baqueta e força** (golpe forte = contato curto = mais agudos). **[física]**

- **编钟 bianzhong:** sinos de seção amendoada dão **dois tons**: golpe no centro (正鼓, modos "a") e
  na lateral (侧鼓, modos "b"), separados por terça menor ou maior. Rossing mediu os 65 sinos do
  Marquês Yi de Zeng (~433 a.C.): intervalos em volta de 300 e 400 cents (de ~210 a ~490). O motor usa
  300/400 alternados (ou fixos, `terca=`). **[medido]** As razões das parciais altas e os T60 são
  **[estimado]** (curtos, como os sinos com 枚 projetados para melodia).
- **大锣 / 小锣 (gongos da ópera):** a não linearidade geométrica faz a altura **mudar depois do golpe**:
  o 小锣 sobe, outros gongos descem, e o sentido depende da curvatura/espessura do centro (Jossic,
  Thomas, Chomette, Mamou-Mani et al., JASA 2017 e 2018: modelo de Duffing para o modo fundamental).
  Implementado como desvio ∝ energia restante (Δf ∝ amplitude²), proporcional a vel². Sentido
  **[medido]**; tamanho do glissando (−320 / +260 cents) **[estimado]**.
- **抄锣 (tam-tam):** cascata de energia para os modos agudos ("florescer"). **[física]** aproximada.
- **Tambores:** modos de membrana circular (zeros de Bessel; com carga de ar para dois couros),
  queda de altura no ataque (modulação de tensão), borda × centro, aro de madeira. **[física]**
- **编磬:** barra livre (1 : 2,756 : 5,404 : 8,933), com desdobramento pela forma em L. **[física]** + **[estimado]**
- **Pratos:** centenas de modos aleatórios + ruído, segundo contato entre os dois pratos. **[estimado]**

### 1.6 Reverb e mixagem

FDN 8×8 (Jot/Stautner-Puckette) com absorção dependente da frequência, difusão de entrada e primeiras
reflexões por sala. As salas (palácio Tang, templo, gruta de Dunhuang…) são **[estimado]**. Loudness
pelo algoritmo ITU-R BS.1770-4 **[medido/norma]** (o teste confere −3,01 LUFS no seno de referência).

---

## 2. Afinações e história

- **三分损益:** gerado por quintas puras (perde um terço / ganha um terço do tubo), como nos textos
  Guanzi e Lüshi Chunqiu. O ciclo não fecha (仲吕 ~23,5 cents acima do 4/3: o "黄钟不能还原"). **[medido]**
- **朱载堉 (1584):** temperamento igual calculado com 25 dígitos (新法密率). **[medido]**
- **Justa:** razões 5-limite. **[medido]**
- **Altura absoluta do 黄钟:** variou por dinastia; o padrão C4 é convenção moderna. **[estimado]**
- **Lá do gagaku (herdeiro da corte Tang):** 430 Hz (Stanford Gagaku). **[medido]**

### O pipa Tang 曲项琵琶

- **4 cordas, 4 trastes:** o gakubiwa japonês, descendente direto, tem 4 trastes com solto→1º traste
  = segunda maior e os seguintes em semitons (Stanford Gagaku) → `TRASTES = [0, 2, 3, 4, 5]`. **[medido]**
- **Palheta de madeira:** golpe para baixo sempre forte e para cima fraco (gagaku), e a palheta bate no
  protetor de couro (捍拨) — por isso a camada `batida`. **[medido]** + **[estimado]**
- **Afinações** (`yiyue` 壹越调, `pingdiao` 平调…): **reconstruções** por analogia com o gakubiwa
  (afinação muda com o modo da peça). As alturas exatas das fontes Tang (partituras de Dunhuang
  P.3808, de 933 d.C., estudadas por 林谦三, 叶栋, 陈应时, 席臻贯, 饶宗颐, 何昌林, Picken/Nickson,
  Rockwell; gravadas recentemente por Wu Man) continuam em discussão. **[estimado]**
- **Técnicas do 琵琶行 (白居易, 816):** 抹 e 挑 são golpes de palheta para baixo/cima; 拢 e 捻 são
  técnicas da mão esquerda cujo gesto exato é **interpretação** (aqui: empurrar de leve e esfregar em
  vibrato); 当心画 é o risco final pelas quatro cordas ("como seda rasgando"). **[estimado]**

### Afinações modernas usadas

pipa A2-D3-E3-A3 · guqin 正调 C2-D2-F2-G2-A2-C3-D3 · guzheng pentatônica de 21 cordas em ré (D2–D6) ·
zhongruan G2-D3-G3-D4 · liuqin G3-D4-G4-D5 · erhu D4-A4 · gaohu G4-D5 · zhonghu G3-D4 ·
yangqin 402 cromático G2–A6 · 徽 do guqin nas frações 1/8, 1/6, 1/5, 1/4, 1/3, 2/5, 1/2, 3/5, 2/3,
3/4, 4/5, 5/6, 7/8. **[medido/padrão]**

---

## 3. Onde a aproximação é mais fraca (honestamente)

1. **Corpos:** os modos são estimados. Uma medição de resposta ao impulso de cada instrumento (batendo
   no cavalete e gravando) daria o maior salto de realismo — o motor já aceita (`Corpo(modos=…)`).
2. **Afinações Tang:** reconstruções; a altura e a afinação exatas são debate acadêmico.
3. **Flauta abaixo de ~290 Hz** instável; a membrana do dizi é um oscilador simples, não uma placa.
4. **Palheta livre e xun** são modelos de fonte-filtro simplificados (não um oscilador acoplado completo).
5. **Pratos e tam-tam:** caos não linear real é aproximado por modos aleatórios + "florescer".
6. **Expressão humana:** técnicas são gestos idealizados com variação aleatória; um músico real muda
   tudo continuamente. Para chegar perto, use curvas (`CurvaAltura`), automação e humanização.
7. **Arco:** a troca de corda dentro de uma frase usa uma corda só por frase (o ponto do arco não pode
   pular no meio sem estalo).

---

## 4. Como melhorar a fidelidade com dados reais

- **Corpo medido:** grave a resposta do instrumento a uma batidinha no cavalete; tire os picos do
  espectro (freq., largura de banda → T60 = 6,91/(π·largura), ganho) e crie um `Corpo`.
- **T60 do material:** grave uma nota solta grave e uma aguda e meça o tempo de −60 dB; ponha nos
  dois pontos de `Material`.
- **Inarmonicidade:** meça as parciais de uma nota solta e ajuste `B_ref` até bater.
- **Gongo:** meça a altura no começo e depois de 1 s num golpe forte → `GLIDE`.
- **Compare** sempre no mesmo espectrograma (a mesma nota, a mesma força).

---

## 5. Fontes

- T. D. Rossing, sinos chineses de dois tons, ASA (133º e 138º encontros): https://acoustics.org/pressroom/httpdocs/133rd/2pmu1.html · https://acoustics.org/pressroom/httpdocs/138th/rossing1.htm
- Bianzhong (visão geral, dois tons por sino): https://en.wikipedia.org/wiki/Bianzhong
- M. Jossic et al., "Effects of internal resonances in the pitch glide of Chinese gongs", JASA 144(1), 431–442 (2018), DOI 10.1121/1.5038114 — https://hal.archives-ouvertes.fr/hal-01862794 ; tese de Jossic (2017): https://hal.sorbonne-universite.fr/tel-01713349v1
- C.-G. Tsai, "The Chinese Membrane Flute (Dizi): Physics and Perception of its Tones" (tese, 2003).
- H. Penttinen, J. Pakarinen, V. Välimäki, M. Laurson, H. Li, M. Leman, "Model-Based Sound Synthesis of the Guqin", JASA 120(6), 4052–4063 (2006): https://research.aalto.fi/en/publications/model-based-sound-synthesis-of-the-guqin/
- "Analysis and synthesis of the guqin", Canadian Acoustics: https://jcaa.caa-aca.ca/index.php/jcaa/article/view/1658
- Análise espectral de cordas de seda do qin (informal): https://silkqin.com/08anal/spectral.htm
- Acústica do erhu (UBC PHYS341): https://wiki.ubc.ca/Course:PHYS341/Archive/2016wTerm2/Erhu_Acoustics
- Inarmonicidade em cordas de pipa (UBC PHYS341): https://wiki.ubc.ca/Course:PHYS341/Inharmonicity_in_Pipa_Strings
- Biwa do gagaku (trastes, palheta, lá = 430): https://gagaku.stanford.edu/en/strings/biwa
- Partituras de Dunhuang e Wu Man: https://symposium.music.org/volume-65-no-2/audio-reviews/wu-man.html ; transcrição automática (IRCAM): https://medias.ircam.fr/person/Weiping-Wang ; L. Picken: https://stephenjones.blog/2017/02/10/laurence-picken/
- M. E. McIntyre, R. T. Schumacher, J. Woodhouse, "On the oscillations of musical instruments", JASA 74 (1983).
- J. O. Smith III, *Physical Audio Signal Processing* (guias de onda, síntese comutada); P. Cook e G. Scavone, *The Synthesis ToolKit (STK)* (modelos Flute, Bowed, Saxofony, Clarinet).
- V. Välimäki, J. Huopaniemi, M. Karjalainen, Z. Jánosy, "Physical modeling of plucked string instruments with application to real-time sound synthesis", JAES 44(5) (1996).
- A. Chaigne, A. Askenfelt, "Numerical simulations of piano strings", JASA 95 (1994); D. E. Hall, "Piano string excitation", JASA (1986).
- N. Fletcher, T. Rossing, *The Physics of Musical Instruments* (Springer, 1998).
- J.-M. Jot, A. Chaigne, "Digital delay networks for designing artificial reverberators" (AES 1991).
- ITU-R BS.1770-4 (loudness).
- 白居易, 《琵琶行》 (816).
