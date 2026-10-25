# Dooms Day áudio v5.0 · 25/10/2026 · trilha nova, do zero

**Por quê:** consertar a trilha antiga ficou complicado demais. O usuário pediu para "zerar só a música e manter as ferramentas", com o ofício de Interestelar como referência: órgão de 32 pés com o efeito resultante, ostinato e o relógio.

## O que mudou
- **Trilha nova** (`spec/music.json`, `tools/synth/music.py`, `tools/synth/organ.py`): órgão de tubos aditivo (registros 32'–1', mistura, palhetas, fala e chiff de tubo, caixa expressiva), coral por formantes e o tique do relógio. Grade de 80 BPM (15 ticks por tempo), com a fusão, os jatos, a maré e o horizonte nos tempos fortes.
- **32' resultante** de verdade: 16' + 10⅔' fazem o ouvido ouvir um Ré0 (18,35 Hz) que nenhum tubo toca. Provado por `check_organ.py` (periodicidade de 18,35 Hz, e 18,34 Hz depois do corte de 150 Hz do celular), que roda antes de cada render.
- `sgx_score_a/b` e `sgx_rhythm_a/b` viraram `sgx_music_a/b` (2 arquivos em vez de 4).
- Saíram `score.py`, `score.json`, `rhythm.py` e `rhythm.json`. A sala e o `act7` foram para o `music.json`.
- Dramaturgia ajustada à música nova: sem soluços na fusão (a grade já acelera por subdivisão); os soluços do horizonte caem nos tempos fortes; o tutti do 540 é ouvido inteiro antes de o tempo ceder.
- Calibrador: a receita pode sugerir o ganho inicial (`parts.hints`) e a correção tem uma zona morta de 0,03. Sem isso, o horizonte caía num mínimo ruim.
- Teoria e a forma compasso a compasso: `docs/SOUND_DIRECTION.md` §10.

## Conferido
Ida e volta 18/18 · ouvido automático aprovado (golpe da fusão +2,2 dB e do horizonte +7,8 dB acima do build; grave voltando 12,6 e 51 dB; respiração do filme 14,5 dB) · silêncio digital em 600–619.
