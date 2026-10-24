# Fontes

- `starmap_2020_4k.exr`: **NASA Scientific Visualization Studio, "Deep Star Maps 2020"** (SVS 4851), https://svs.gsfc.nasa.gov/4851/ . Mapa equiretangular em coordenadas celestes (Ascensão Reta 12h no centro, crescendo para a esquerda). Dados Gaia DR2, Hipparcos e Tycho-2. Imagens da NASA são de domínio público; dê o crédito no LEIA-ME.
- Tratamento que funcionou (para escrever o `tools/bake/sky_engine.py` deste addon):
  - **difuso**: filtro de mediana no mapa, para tirar as estrelas e sobrar só a Via Láctea;
  - **catálogo de estrelas**: picos locais do mapa, deduplicados a 0,22°, redesenhados como pontos nítidos com magnitude 1–8,3 e cor pela razão R/B (assim não sai "farinha" de milhões de pixels);
  - **níveis**: preto em 0,020, pé de 1,7, ganho de 8 no difuso;
  - **tonemap**: `1 − e^(−1,15x)` com gama 1,12, e dither só onde tem luz.
