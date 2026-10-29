// v0.3.3 (T-28): o "rig" de âncoras do buraco negro. Medido no S-12 (29/10/2026): o Bedrock só desenha uma
// entidade até ~64 blocos da CÂMERA, seja qual for o visible_bounds, o peso ou a simulação (P-56). As partículas não
// têm esse limite, e o filme põe a câmera a até 150 blocos do buraco negro. Então a entidade nasce PERTO DA CÂMERA
// (≤ maxDist) e a malha vai para o lugar verdadeiro por osso (a raiz deslocada de O − âncora, como os detritos do
// S-04). Quando a câmera se afasta, nasce outra âncora e a anterior apaga no mesmo tick (janela ts/te no Molang).
// O trajeto da câmera é determinístico, então as âncoras e as ticking areas pequenas (1 chunk) saem planejadas
// no começo e são pedidas com antecedência.
// O facing também sai daqui: com a âncora longe de O, q.rotation_to_camera mede o ângulo errado. O script manda o
// yaw de O para a câmera no tick anterior e no atual (y0, y1) e o Molang interpola por q.frame_alpha, igual à
// câmera, que anda com ease linear de 1 tick.

const HYST = 0.6; // graus: só troca de malha se a nova estiver claramente mais perto

// Elevação (graus) da câmera vista de c: + acima do plano do disco, − abaixo.
export function elevation(cam, c) {
  const dx = cam.x - c.x, dy = cam.y - c.y, dz = cam.z - c.z;
  return (Math.atan2(dy, Math.hypot(dx, dz)) * 180) / Math.PI;
}

// Índice do bin mais perto de |e| (prev = bin atual, para a histerese).
export function pickBin(bins, e, prev = -1) {
  const a = Math.abs(e);
  let best = 0, bestD = Infinity;
  for (let i = 0; i < bins.length; i++) {
    const d = Math.abs(bins[i] - a);
    if (d < bestD) (best = i), (bestD = d);
  }
  if (prev >= 0 && prev < bins.length && Math.abs(bins[prev] - a) <= bestD + HYST) return prev;
  return best;
}

// Valor da propriedade singularity:bin: ±(j + 1), negativo com a câmera abaixo do disco (o cliente espelha).
export const binValue = (j, e) => (e < 0 ? -(j + 1) : j + 1);

// Yaw do MC (0 = +Z, 90 = −X) de uma direção horizontal.
export const mcYaw = (v) => (Math.atan2(-v.x, v.z) * 180) / Math.PI;

const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);

// Segmentos [s, e) com uma âncora cada: a câmera fica a ≤ maxDist da âncora durante o segmento.
export function planAnchors(camAt, t0, t1, maxDist = 32) {
  const segs = [];
  let cur = null;
  for (let t = t0; t <= t1; t++) {
    const c = camAt(t);
    if (!cur || dist(c, cur.p) > maxDist) {
      if (cur) cur.e = t;
      // a âncora vai um pouco à frente no caminho, para o segmento durar mais
      let p = c;
      for (let k = 1; k <= 60 && t + k <= t1; k++) {
        const q = camAt(t + k);
        if (dist(q, c) > maxDist) break;
        if (k % 10 === 0) p = { x: (c.x + q.x) / 2, y: (c.y + q.y) / 2, z: (c.z + q.z) / 2 };
      }
      cur = { s: t, e: t1 + 1, p: { x: p.x, y: p.y, z: p.z } };
      segs.push(cur);
    }
  }
  return segs;
}

// Desdobra o yaw para não pular de 180 para −180 (a interpolação do Molang daria a volta inteira).
const unwrap = (prev, y) => (prev == null ? y : prev + ((((y - prev) % 360) + 540) % 360) - 180);

export class BlackHoleRig {
  // roles: [{ key, type, from, to, center(t), bins, extra }] · camAt(t): posição da câmera no tick t
  // filmOffset: tick do filme = t + filmOffset (o S-11 roda o buraco negro já com o disco aceso)
  constructor({ world, dimension, warn = () => {}, camAt, t0, t1, roles, cal = 0, maxDist = 32, lead = 60, areaPrefix = "sgx_an", filmOffset = 0 }) {
    Object.assign(this, { world, dimension, warn, camAt, roles, cal, lead, areaPrefix, filmOffset });
    this.segs = planAnchors(camAt, t0, t1, maxDist);
    this.live = []; // {seg, role, e, bi, y}
    this.areas = new Map(); // seg index → {id, ready}
    this.spawned = new Set();
    this.calls = 0;
  }

  _area(i) {
    if (this.areas.has(i)) return this.areas.get(i);
    const seg = this.segs[i];
    const id = `${this.areaPrefix}_${i}`;
    const a = { id, ready: false };
    this.areas.set(i, a);
    const tam = this.world?.tickingAreaManager;
    if (!tam) {
      a.ready = true;
      return a;
    }
    try {
      const p = { x: Math.floor(seg.p.x), y: Math.floor(seg.p.y), z: Math.floor(seg.p.z) };
      if (tam.hasTickingArea?.(id)) tam.removeTickingArea(id);
      tam.createTickingArea(id, { dimension: this.dimension, from: p, to: p })
        .then(() => (a.ready = true))
        .catch((e) => {
          this.warn(`âncora ${i}: ${e}`);
          a.ready = true; // tenta mesmo assim (o chunk pode estar carregado pelo jogador)
        });
    } catch (e) {
      this.warn(`âncora ${i}: ${e}`);
      a.ready = true;
    }
    return a;
  }

  _dropArea(i) {
    const a = this.areas.get(i);
    if (!a) return;
    try {
      this.world?.tickingAreaManager?.removeTickingArea(a.id);
    } catch {
      // já saiu
    }
    this.areas.delete(i);
  }

  _set(e, k, v) {
    try {
      if (e?.isValid) {
        e.setProperty(`singularity:${k}`, v);
        this.calls++;
      }
    } catch (err) {
      this.warn(`bh ${k}: ${err}`);
    }
  }

  _yaw(role, t) {
    const c = role.center(t), cam = this.camAt(t);
    return mcYaw({ x: cam.x - c.x, z: cam.z - c.z });
  }

  _spawn(i, role, t) {
    const seg = this.segs[i];
    const c = role.center(t);
    const O = role.origin; // a raiz da malha vai para O (A e B somam a órbita no Molang)
    const e0 = elevation(this.camAt(t), c);
    const bi = pickBin(role.bins, e0);
    let y0 = this._yaw(role, Math.max(t - 1, 0)), y1 = unwrap(y0, this._yaw(role, t));
    let ent;
    try {
      ent = this.dimension.spawnEntity(role.type, { ...seg.p });
    } catch (err) {
      this.warn(`bh spawn ${role.key}: ${err}`);
      return;
    }
    const props = {
      t0: (t + this.filmOffset) / 20, cal: this.cal, bin: binValue(bi, e0),
      ts: seg.s + this.filmOffset, te: Math.min(seg.e + this.filmOffset, 4000),
      ox: O.x - seg.p.x, oy: O.y - seg.p.y, oz: O.z - seg.p.z, y0, y1, ...(role.extra ?? {}),
    };
    for (const [k, v] of Object.entries(props)) this._set(ent, k, v); // P-28: tudo no spawn
    this.live.push({ seg: i, role, e: ent, bi, y: y1, bin: props.bin });
  }

  tick(t) {
    // ticking areas com antecedência; spawn 3 ticks antes do segmento (o cliente esconde até ts)
    for (let i = 0; i < this.segs.length; i++) {
      const seg = this.segs[i];
      if (t < seg.s - this.lead || t >= seg.e) continue;
      const a = this._area(i);
      if (t < seg.s - 3 || this.spawned.has(i) || (!a.ready && t < seg.s)) continue;
      this.spawned.add(i);
      for (const role of this.roles) if (seg.e > role.from && seg.s <= role.to) this._spawn(i, role, t);
    }
    // yaw (tick anterior → atual) e bin, só para as entidades vivas
    for (const x of this.live) {
      const yPrev = x.y;
      const yNow = unwrap(yPrev, this._yaw(x.role, t));
      this._set(x.e, "y0", yPrev);
      this._set(x.e, "y1", yNow);
      x.y = yNow;
      const c = x.role.center(t);
      const el = elevation(this.camAt(t), c);
      x.bi = pickBin(x.role.bins, el, x.bi);
      const v = binValue(x.bi, el);
      if (v !== x.bin) this._set(x.e, "bin", (x.bin = v));
    }
    // fim do segmento (ou do papel): remove a entidade e a área
    for (const x of [...this.live]) {
      const seg = this.segs[x.seg];
      if (t > seg.e || t > x.role.to + 2) {
        try {
          if (x.e?.isValid) x.e.remove();
        } catch {
          // já sumiu
        }
        this.live.splice(this.live.indexOf(x), 1);
      }
    }
    for (const i of [...this.areas.keys()]) if (t > this.segs[i].e + 20) this._dropArea(i);
  }

  stop() {
    for (const x of this.live.splice(0)) {
      try {
        if (x.e?.isValid) x.e.remove();
      } catch {
        // já sumiu
      }
    }
    for (const i of [...this.areas.keys()]) this._dropArea(i);
  }
}
