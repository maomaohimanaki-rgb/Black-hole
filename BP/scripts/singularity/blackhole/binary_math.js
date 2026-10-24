// Par A/B em órbita (spec/layout.json → binary). A MESMA fórmula roda no Molang do cliente
// e no sintetizador do chirp: som e órbita sincronizados por construção (T-05).

export const BIN = {
  mA: 36,
  mB: 29,
  tStart: 60,
  tMerge: 240,
  tau0: 9, // s
  S: 24, // desaceleração visual
  f0: 35, // Hz no tick 60
  d0: 8, // blocos no tick 60
};

// τ(t) = (240 − t)/20 s
export const tau = (t) => Math.max((BIN.tMerge - t) / 20, 1e-6);

// f(t) = 35 · (τ/τ0)^(−3/8) Hz
export const fGw = (t) => BIN.f0 * Math.pow(tau(t) / BIN.tau0, -0.375);

// d(t) = 8 · (τ/τ0)^(1/4) blocos
export const separation = (t) => BIN.d0 * Math.pow(tau(t) / BIN.tau0, 0.25);

// φ(t) = 2π · (35/(2S)) · τ0^(3/8) · (8/5) · (τ0^(5/8) − τ^(5/8)), em radianos (φ0 = 0).
export function phase(t) {
  const { f0, S, tau0 } = BIN;
  return 2 * Math.PI * (f0 / (2 * S)) * Math.pow(tau0, 0.375) * 1.6 * (Math.pow(tau0, 0.625) - Math.pow(tau(t), 0.625));
}

// Offsets de A e B em relação a O, no plano (R, F): A = −d·mB/M·ê, B = +d·mA/M·ê.
export function offsets(t) {
  const M = BIN.mA + BIN.mB;
  const d = separation(t), ph = phase(t);
  const c = Math.cos(ph), s = Math.sin(ph);
  const a = (d * BIN.mB) / M, b = (d * BIN.mA) / M;
  return { A: { r: -a * c, f: -a * s }, B: { r: b * c, f: b * s }, d, phi: ph };
}

// Ticks (fracionários) em que φ cruza kπ, entre o início da órbita e a fusão.
export function halfOrbitCrossings() {
  const out = [];
  const end = BIN.tMerge - 1e-6;
  for (let k = 1; ; k++) {
    const target = k * Math.PI;
    if (phase(end) < target) break;
    let lo = BIN.tStart, hi = end;
    for (let i = 0; i < 60; i++) {
      const mid = (lo + hi) / 2;
      if (phase(mid) < target) lo = mid;
      else hi = mid;
    }
    out.push(hi);
  }
  return out;
}

// Meias-órbitas usadas pelas ondulações e pelos acentos do chirp: arredondadas e com
// espaçamento ≥ 4 ticks (as que ficam mais perto da anterior caem).
export function halfOrbitTicks(minGap = 4) {
  const out = [];
  for (const x of halfOrbitCrossings()) {
    const t = Math.round(x);
    if (!out.length || t - out[out.length - 1] >= minGap) out.push(t);
  }
  return out;
}
