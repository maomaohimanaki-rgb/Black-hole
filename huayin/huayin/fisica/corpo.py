"""Corpo ressonante (caixa, pele, tubo) como banco de modos + equalização de radiação.

Como o corpo é linear e igual para todas as notas, ele é aplicado UMA vez na soma da
faixa do instrumento (síntese "comutada", Smith 1993). Isso é exato para um sistema
linear e economiza muito processamento.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import oaconvolve

from ..dsp import filtros as F


@dataclass
class Corpo:
    nome: str
    modos: list = field(default_factory=list)   # [(Hz, T60 s, ganho)]
    direto: float = 0.3                         # parte que sai sem passar pelo corpo
    passa_alta: float = 40.0                    # Hz
    passa_baixa: float = 16000.0                # Hz
    eq: list = field(default_factory=list)      # [(tipo, Hz, Q, dB)]
    descricao: str = ""

    def aplicar(self, x: np.ndarray, sr: int, mistura: float = 1.0) -> np.ndarray:
        """mistura: 0 = corda pura (sem corpo), 1 = corpo completo."""
        if mistura <= 0 or not self.modos:
            y = x
        else:
            # v1.0: convolução com a resposta ao impulso do banco (idêntico ao banco de filtros,
            # já que tudo é linear, e ~30× mais rápido em faixas longas). A resposta é normalizada
            # pela energia: ruído branco entra e sai com o mesmo RMS, trocar de corpo não muda o volume.
            h = self._ir(sr)
            y_c = (oaconvolve(x, h[None, :], axes=-1) if x.ndim > 1 else oaconvolve(x, h))[..., :x.shape[-1]]
            y = (1 - mistura) * x + mistura * y_c
        if self.passa_alta:
            y = F.passa_alta(y, self.passa_alta, sr)
        if self.passa_baixa and self.passa_baixa < 0.45 * sr:
            y = F.passa_baixa(y, self.passa_baixa, sr)
        for tipo, f, q, db in self.eq:
            y = F.filtrar(y, F.biquad(tipo, f, sr, q, db))
        return y

    def _ir(self, sr: int) -> np.ndarray:
        cache = self.__dict__.setdefault("_cache_ir", {})
        if sr not in cache:
            t60 = max((m[1] for m in self.modos), default=0.1)
            imp = np.zeros(int(min(max(t60 * 1.6, 0.05), 2.0) * sr))
            imp[0] = 1.0
            h = F.banco_modal(imp, sr, self.modos, direto=self.direto)
            h /= float(np.sqrt(np.sum(h * h))) or 1.0
            cache[sr] = h
        return cache[sr]

    def resposta(self, sr: int, n: int = 8192) -> tuple[np.ndarray, np.ndarray]:
        """(freqs, dB) da resposta ao impulso — útil para conferir/ajustar um corpo novo."""
        imp = np.zeros(n)
        imp[0] = 1.0
        h = self.aplicar(imp, sr)
        H = np.abs(np.fft.rfft(h))
        return np.fft.rfftfreq(n, 1 / sr), 20 * np.log10(H + 1e-12)


# v1.0: os modos abaixo são estimativas guiadas pela física de caixas de madeira (placa de
# paulównia 桐木 sobre fundo de madeira dura), pela literatura citada em docs/FIDELIDADE.md
# e pelo ouvido. Não são medições de um exemplar. Ajuste à vontade (veja o tutorial).
CORPOS: dict[str, Corpo] = {
    "pipa": Corpo("pipa", [
        (210, 0.09, 0.55), (365, 0.07, 1.0), (540, 0.06, 0.8), (790, 0.05, 0.75),
        (1120, 0.04, 0.65), (1580, 0.035, 0.55), (2250, 0.03, 0.5), (3150, 0.022, 0.4),
        (4400, 0.016, 0.3), (6000, 0.012, 0.18)], direto=0.35, passa_alta=60,
        descricao="caixa em pera, tampo de paulównia sem boca: médios fortes e ataque seco"),
    "pipa_tang": Corpo("pipa_tang", [
        (150, 0.12, 0.7), (260, 0.09, 1.0), (400, 0.07, 0.85), (590, 0.06, 0.75),
        (860, 0.05, 0.6), (1250, 0.04, 0.5), (1800, 0.03, 0.42), (2600, 0.025, 0.32),
        (3700, 0.02, 0.22)], direto=0.3, passa_alta=45, passa_baixa=11000,
        eq=[("pico", 2800, 1.2, -2.0)],
        descricao="pipa de pescoço curvo 曲项, caixa maior e mais funda, bocas em lua crescente"),
    "guqin": Corpo("guqin", [
        (88, 0.16, 0.75), (140, 0.13, 0.7), (215, 0.1, 0.95), (310, 0.08, 0.85),
        (450, 0.06, 0.7), (650, 0.05, 0.55), (930, 0.035, 0.42), (1350, 0.028, 0.32),
        (2000, 0.02, 0.22)], direto=0.22, passa_alta=35, passa_baixa=7000,
        descricao="caixa longa (~120 cm) de paulównia e catalpa, bocas 龙池/凤沼 embaixo: grave e escuro"),
    "guzheng": Corpo("guzheng", [
        (105, 0.15, 0.7), (170, 0.12, 0.8), (250, 0.1, 0.9), (360, 0.08, 0.85),
        (510, 0.06, 0.75), (730, 0.05, 0.65), (1040, 0.04, 0.55), (1480, 0.03, 0.45),
        (2150, 0.025, 0.38), (3100, 0.02, 0.3), (4500, 0.014, 0.2)], direto=0.3, passa_alta=40,
        descricao="caixa de 163 cm com tampo arqueado: ressonância longa e cheia"),
    "konghou": Corpo("konghou", [
        (140, 0.1, 0.7), (230, 0.09, 0.9), (360, 0.07, 0.85), (540, 0.06, 0.7),
        (800, 0.045, 0.6), (1200, 0.035, 0.45), (1800, 0.028, 0.35), (2700, 0.02, 0.25)],
        direto=0.3, passa_alta=50, passa_baixa=10000,
        descricao="harpa angular Tang (reconstrução): caixa de ressonância vertical"),
    "ruan": Corpo("ruan", [
        (125, 0.14, 0.9), (240, 0.1, 0.8), (380, 0.08, 0.85), (560, 0.06, 0.7),
        (820, 0.05, 0.6), (1200, 0.04, 0.5), (1750, 0.03, 0.4), (2600, 0.022, 0.3)],
        direto=0.3, passa_alta=50,
        descricao="caixa redonda com duas bocas: Helmholtz grave, som de 'violão chinês'"),
    "liuqin": Corpo("liuqin", [
        (280, 0.07, 0.7), (480, 0.06, 1.0), (720, 0.05, 0.85), (1050, 0.04, 0.75),
        (1500, 0.035, 0.65), (2200, 0.028, 0.55), (3200, 0.02, 0.45), (4600, 0.015, 0.3)],
        direto=0.4, passa_alta=120,
        descricao="pera pequena: brilhante e cortante"),
    "sanxian": Corpo("sanxian", [
        (300, 0.05, 0.6), (620, 0.05, 0.9), (950, 0.04, 0.8), (1400, 0.035, 0.9),
        (2100, 0.03, 0.8), (3000, 0.025, 0.6), (4200, 0.018, 0.45)],
        direto=0.25, passa_alta=70,
        descricao="caixa pequena coberta de pele de cobra: ataque de banjo, médios nasais"),
    "yangqin": Corpo("yangqin", [
        (115, 0.15, 0.7), (190, 0.12, 0.8), (290, 0.1, 0.9), (430, 0.08, 0.85),
        (620, 0.06, 0.75), (890, 0.05, 0.65), (1280, 0.04, 0.55), (1850, 0.03, 0.45),
        (2700, 0.022, 0.35), (3900, 0.016, 0.25)], direto=0.35, passa_alta=50,
        descricao="caixa trapezoidal com pontes de duas fileiras"),
    "erhu": Corpo("erhu", [
        (330, 0.04, 0.35), (660, 0.05, 1.0), (920, 0.04, 0.55), (1450, 0.035, 0.6),
        (2000, 0.04, 0.9), (2650, 0.03, 0.6), (3300, 0.03, 0.5), (4200, 0.02, 0.32),
        (5300, 0.015, 0.2)], direto=0.12, passa_alta=150,
        descricao="ressonador hexagonal coberto de pele de píton: tubo fechado (modos ímpares) "
                  "acoplado à membrana (~2 kHz) — o som 'nasal' do erhu"),
    "gaohu": Corpo("gaohu", [
        (520, 0.04, 0.6), (950, 0.04, 1.0), (1500, 0.035, 0.7), (2300, 0.035, 0.9),
        (3200, 0.03, 0.7), (4400, 0.02, 0.45), (6000, 0.015, 0.25)], direto=0.12, passa_alta=250,
        descricao="ressonador menor que o do erhu, tocado entre os joelhos: agudo e brilhante"),
    "zhonghu": Corpo("zhonghu", [
        (220, 0.05, 0.6), (440, 0.05, 1.0), (700, 0.04, 0.6), (1100, 0.035, 0.6),
        (1600, 0.035, 0.75), (2300, 0.03, 0.55), (3100, 0.025, 0.4), (4200, 0.018, 0.25)],
        direto=0.12, passa_alta=90, descricao="erhu contralto, caixa maior"),
    "banhu": Corpo("banhu", [
        (480, 0.03, 0.5), (900, 0.035, 0.8), (1300, 0.035, 1.0), (1900, 0.03, 0.85),
        (2600, 0.03, 1.0), (3500, 0.025, 0.75), (4700, 0.018, 0.5), (6200, 0.012, 0.3)],
        direto=0.15, passa_alta=220,
        descricao="casca de coco com tampo de madeira (sem pele): agudo, penetrante, da ópera do norte"),
    "sopro_bambu": Corpo("sopro_bambu", [], direto=1.0, passa_alta=180, passa_baixa=14000,
                         eq=[("prateleira_alta", 3500, 0.7, 1.5)],
                         descricao="radiação de tubo de bambu aberto (passa-alta suave)"),
    "suona": Corpo("suona", [
        (900, 0.02, 0.6), (1800, 0.025, 0.8), (2900, 0.02, 0.7), (4100, 0.015, 0.5)],
        direto=0.8, passa_alta=250, passa_baixa=15000,
        eq=[("prateleira_alta", 2500, 0.7, 4.0)],
        descricao="campana de cobre 碗: radiação forte dos agudos — o instrumento mais alto da China"),
}
