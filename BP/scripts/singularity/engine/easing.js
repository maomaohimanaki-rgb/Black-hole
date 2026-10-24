// Easings do camera_engine e das curvas do spec (letterbox, grade, escala).
// v0.1.0: nomes iguais aos de spec/storyboard.json (check_spec.py confere a lista).
// u em [0, 1] → valor em [0, 1] (outBack passa um pouco de 1, de propósito).

const PI = Math.PI;

const outBounce = (u) => {
  const n = 7.5625, d = 2.75;
  if (u < 1 / d) return n * u * u;
  if (u < 2 / d) return n * (u -= 1.5 / d) * u + 0.75;
  if (u < 2.5 / d) return n * (u -= 2.25 / d) * u + 0.9375;
  return n * (u -= 2.625 / d) * u + 0.984375;
};

export const EASES = {
  linear: (u) => u,
  // step: segura o valor anterior até o tick do keyframe (chegada seca).
  step: (u) => (u >= 1 ? 1 : 0),
  inQuad: (u) => u * u,
  outQuad: (u) => 1 - (1 - u) * (1 - u),
  inOutQuad: (u) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2),
  inCubic: (u) => u * u * u,
  outCubic: (u) => 1 - Math.pow(1 - u, 3),
  inOutCubic: (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2),
  inExpo: (u) => (u <= 0 ? 0 : Math.pow(2, 10 * u - 10)),
  outExpo: (u) => (u >= 1 ? 1 : 1 - Math.pow(2, -10 * u)),
  inSine: (u) => 1 - Math.cos((u * PI) / 2),
  outSine: (u) => Math.sin((u * PI) / 2),
  inOutSine: (u) => -(Math.cos(PI * u) - 1) / 2,
  outBack: (u) => {
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2);
  },
  outBounce,
};

export function ease(name, u) {
  const f = EASES[name ?? "linear"];
  if (!f) throw new Error(`easing desconhecido: ${name}`);
  return f(Math.min(1, Math.max(0, u)));
}

export const lerp = (a, b, u) => a + (b - a) * u;

// Ângulo em graus pelo caminho mais curto.
export function lerpAngle(a, b, u) {
  let d = ((b - a) % 360 + 540) % 360 - 180;
  return a + d * u;
}

// Curva por keyframes [{t, <campo>, ease?}] → valor no tick t. O ease do keyframe diz
// como se CHEGA nele (mesma convenção da câmera).
export function sampleCurve(keys, field, t) {
  if (t <= keys[0].t) return keys[0][field];
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (t <= k.t) {
      const p = keys[i - 1];
      const a = p[field], b = k[field];
      if (typeof a !== "number" || typeof b !== "number") return t >= k.t ? b : a;
      const span = k.t - p.t;
      const u = span <= 0 ? 1 : (t - p.t) / span;
      return lerp(a, b, ease(k.ease ?? "linear", u));
    }
  }
  return keys[keys.length - 1][field];
}
