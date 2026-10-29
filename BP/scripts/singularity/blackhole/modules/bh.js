// v0.3.1 (F3, T-25): o buraco negro é ENTIDADE com geometria (tools/bake/bh_model.py), não sprite. O usuário
// vetou o impostor de partícula da 0.3.0: "tem que ser objeto, JSON e Molang". Quase tudo roda no cliente:
//  - a malha que a lente dobra, virada para a câmera a cada quadro;
//  - o giro do disco (uv_anim por anel, Kepler) e o tempo liso por quadro (q.frame_alpha, como o creeper carregado);
//  - a escala, o ringdown, a ignição dos anéis de fora para dentro e o fim (Molang gerado do spec);
//  - a órbita de A e B (a mesma fórmula do binary_math.js, então o chirp continua em sincronia).
// v0.3.3 (T-28): o jogo só desenha entidade até ~64 blocos da câmera (S-12, P-56), então quem cria e move as
// entidades é o rig de âncoras (rig.js): elas nascem perto da câmera e a malha vai para O por osso.

import { BlackHoleRig, elevation, pickBin, binValue, mcYaw } from "../rig.js";

export { elevation, pickBin, binValue, mcYaw };
export const ID = "singularity:sgx_bh";
export const ID_SMALL = "singularity:sgx_bh_small";
export const BH_TYPES = [ID, ID_SMALL];

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

// Os três papéis do filme: o par A/B até a fusão e o buraco final de 240 a 700.
export function filmRoles(L, data) {
  const fyaw = mcYaw(L.F);
  const pair = (side) => ({
    key: side === 1 ? "A" : "B", type: ID_SMALL, from: 0, to: 241, origin: L.O, bins: data.lens.smallBins,
    center: (t) => L.binary(Math.min(t, 239))[side === 1 ? "A" : "B"], extra: { side, fyaw },
  });
  return [
    pair(1), pair(2),
    { key: "main", type: ID, from: 238, to: 702, origin: L.O, center: () => L.O, bins: data.lens.bins },
  ];
}

export default {
  name: "bh",
  setup(ctx) {
    const { layout: L, data, dimension, world } = ctx;
    const last = data.meta.filmTicks - 1;
    const track = ctx.cameraTrack;
    const camAt = track ? (t) => track.sample(Math.min(Math.max(t, 0), last)).p
      : () => ({ x: L.O.x - L.F.x * 100, y: L.O.y + 26, z: L.O.z - L.F.z * 100 });
    const from = Math.max(0, Math.floor(ctx.options.from ?? 0));
    const rig = new BlackHoleRig({
      world, dimension, warn: ctx.warn, camAt, t0: from, t1: 703, roles: filmRoles(L, data),
      cal: Math.max(0, Math.min(15, Math.floor(ctx.options.cal ?? 0))),
    });
    ctx.bhRig = rig;
    ctx.hook("bh", (t) => rig.tick(t), { win: [0, 704], prio: "critical" });
    ctx.onTeardown(() => rig.stop());
  },
};
