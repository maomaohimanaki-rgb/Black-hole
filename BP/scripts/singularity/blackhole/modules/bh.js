// v0.3.1 (F3, T-25): o buraco negro é ENTIDADE com geometria (tools/bake/bh_model.py), não sprite. O usuário
// vetou o impostor de partícula da 0.3.0: "tem que ser objeto, JSON e Molang". Quase tudo roda no cliente:
//  - a malha que a lente dobra, virada para a câmera a cada quadro (q.rotation_to_camera);
//  - o giro do disco (uv_anim por anel, Kepler) e o tempo liso por quadro (q.frame_alpha, como o creeper carregado);
//  - a escala, o ringdown, a ignição dos anéis de fora para dentro e o fim (Molang gerado do spec);
//  - a órbita de A e B (a mesma fórmula do binary_math.js, então o chirp continua em sincronia).
// O script só cria as entidades (com t0 = segundos de filme), escolhe o bin de elevação da câmera e manda
// quando ele muda (setProperty, ~1 chamada a cada vários ticks; P-01), e remove no fim.

export const ID = "singularity:sgx_bh";
export const ID_SMALL = "singularity:sgx_bh_small";
export const BH_TYPES = [ID, ID_SMALL];
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

// Remove as entidades do buraco negro que sobraram (crash no meio do filme, /reload).
export function cleanupBlackHoles(dimension) {
  let n = 0;
  for (const type of BH_TYPES) {
    let list = [];
    try {
      list = dimension.getEntities({ type });
    } catch {
      list = [];
    }
    for (const e of list) {
      try {
        e.remove();
        n++;
      } catch {
        // já sumiu
      }
    }
  }
  return n;
}

export default {
  name: "bh",
  setup(ctx) {
    const { layout: L, data, dimension } = ctx;
    const { O, F } = L;
    const bins = data.lens.bins, binsSmall = data.lens.smallBins;
    const cal = Math.max(0, Math.min(3, Math.floor(ctx.options.cal ?? 0)));
    const fyaw = mcYaw(F);
    let main = null;
    const pair = [];
    let cur = -1, curS = -1, sentMain = 0, sentSmall = 0;

    const set = (e, k, v) => {
      try {
        if (e?.isValid) e.setProperty(`singularity:${k}`, v);
      } catch (err) {
        ctx.warn(`bh ${k}: ${err}`);
      }
    };
    const spawn = (type, props) => {
      try {
        const e = dimension.spawnEntity(type, { ...O });
        for (const [k, v] of Object.entries(props)) set(e, k, v); // P-28: tudo escrito no spawn
        return e;
      } catch (err) {
        ctx.warn(`bh spawn: ${err}`);
        return null;
      }
    };
    const drop = (e) => {
      try {
        if (e?.isValid) e.remove();
      } catch {
        // já sumiu
      }
    };

    ctx.hook("bh", (t) => {
      const cam = ctx.pose?.p ?? { x: O.x - F.x * 100, y: O.y + 26, z: O.z - F.z * 100 };
      const e = elevation(cam, O);
      cur = pickBin(bins, e, cur);
      curS = pickBin(binsSmall, e, curS);
      const vMain = binValue(cur, e), vSmall = binValue(curS, e);
      if (!main && t < 700) {
        // o cliente esconde tudo até a hora (v.t), então nasce já no começo: sem atraso de spawn no 240
        main = spawn(ID, { t0: t / 20, cal, bin: vMain });
        sentMain = vMain;
        if (t < 239) {
          for (const side of [1, 2]) pair.push(spawn(ID_SMALL, { t0: t / 20, cal, bin: vSmall, side, fyaw }));
          sentSmall = vSmall;
        }
      }
      if (vMain !== sentMain) set(main, "bin", (sentMain = vMain));
      if (pair.length && vSmall !== sentSmall) {
        sentSmall = vSmall;
        for (const p of pair) set(p, "bin", vSmall);
      }
      if (t >= 242 && pair.length) {
        for (const p of pair.splice(0)) drop(p);
      }
      if (t >= 702 && main) {
        drop(main);
        main = null;
      }
    }, { win: [0, 703], prio: "critical" });

    ctx.onTeardown(() => {
      for (const p of pair.splice(0)) drop(p);
      drop(main);
      main = null;
    });
  },
};
