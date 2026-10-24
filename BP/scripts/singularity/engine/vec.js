// Vetores simples {x, y, z}. Sem dependência do jogo (o motor roda no Node nos testes).

export const v3 = (x = 0, y = 0, z = 0) => ({ x, y, z });
export const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
export const sub = (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
export const mul = (a, s) => ({ x: a.x * s, y: a.y * s, z: a.z * s });
export const dot = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;
export const cross = (a, b) => ({ x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x });
export const len = (a) => Math.sqrt(dot(a, a));
export const norm = (a) => {
  const l = len(a);
  return l > 1e-9 ? mul(a, 1 / l) : v3(0, 0, 1);
};
export const lerpV = (a, b, u) => ({ x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u, z: a.z + (b.z - a.z) * u });
// Soma de termos: madd(O, [R, 3], [U, 2]) = O + 3R + 2U.
export const madd = (o, ...terms) => terms.reduce((acc, [d, s]) => add(acc, mul(d, s)), o);

const DEG = 180 / Math.PI;

// Convenção do motor (= setCamera do Bedrock): pitch positivo olha para baixo; yaw 0 = +Z,
// yaw 90 = −X.
export function dirToRot(d) {
  const h = Math.sqrt(d.x * d.x + d.z * d.z);
  return { pitch: -Math.atan2(d.y, h) * DEG, yaw: Math.atan2(-d.x, d.z) * DEG };
}

export function rotToDir({ pitch, yaw }) {
  const p = pitch / DEG, y = yaw / DEG;
  return { x: -Math.sin(y) * Math.cos(p), y: -Math.sin(p), z: Math.cos(y) * Math.cos(p) };
}
