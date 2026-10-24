// Ajudante de partículas: monta o MolangVariableMap com a convenção das partículas sgx_*
// (Vector3 v.lf = vida/entrada/saída, v.s = tamanho, v.a = alfa, v.c0 = cor; P-26) e conta chamadas
// nativas para o profiler (P-01).

const vec = (a, d = [0, 0, 0]) => {
  const x = Array.isArray(a) ? a : [a, a, a];
  return { x: x[0] ?? d[0], y: x[1] ?? d[1], z: x[2] ?? d[2] };
};

export class Fx {
  constructor({ dimension, MolangVariableMap }) {
    this.dimension = dimension;
    this.MVM = MolangVariableMap;
    this.calls = 0; // total
    this.tickCalls = 0; // no tick atual (zerado pelo cutscene)
    this.errors = 0;
  }

  // vars: {lf:[vida, entrada, saída], s:[...], a, c0:[r,g,b] (0–1), incl}
  spawn(id, pos, vars = {}) {
    const m = new this.MVM();
    m.setVector3("variable.lf", vec(vars.lf ?? [1, 0.05, 0.05]));
    m.setVector3("variable.s", vec(vars.s ?? [1, 1, 1]));
    m.setVector3("variable.a", vec(vars.a ?? 1));
    m.setVector3("variable.c0", vec(vars.c0 ?? [1, 1, 1]));
    if (vars.incl != null) m.setVector3("variable.incl", vec(vars.incl));
    this.calls++;
    this.tickCalls++;
    try {
      this.dimension.spawnParticle(id, pos, m);
    } catch {
      // Fora do mundo carregado: o jogo lança erro. Não derruba o filme.
      this.errors++;
    }
  }
}

export const hexToRgb = (h) => {
  h = h.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
};
