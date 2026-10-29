// v0.3.0 (F3): o impostor do buraco negro (VISUAL_TECH §2, camada L1). No lugar da bolinha preta + halo do
// animatic: uma partícula lookat_xyz com o quadro do atlas assado por tools/bake/bh_engine.py (sombra, anel de
// fótons e o disco dobrado pela lente). O eixo do buraco é vertical (U) e a câmera não tem roll (P-09), então a
// imagem certa só depende da inclinação da câmera: 90° = de lado, no plano do disco; negativo = câmera abaixo.
//  - A e B (20–239): o atlas pequeno (sgx_p_bh_small, disquinho de poeira) pela inclinação de cada um
//  - buraco final (240–699): "bare" (só sombra + anel) até o disco acender e na evaporação; o quadro do disco
//    pela inclinação de 280 a 619, entrando por tinta (preto → cor) enquanto os anéis acendem
// Uma partícula a cada 2 ticks com vida de 3,2 (a de antes ainda cobre a troca), como os gizmos (P-26).

const ID = "singularity:sgx_p_bh";
const ID_SMALL = "singularity:sgx_p_bh_small";
const LIFE = [0.16, 0.01, 0.02];
const HYST = 1.5; // graus: só troca de quadro se o novo estiver claramente mais perto (sem pisca-pisca na borda)

// Inclinação (graus) da câmera vista do centro c: 90 − |elevação|, com o sinal da elevação.
export function inclination(cam, c) {
  const dx = cam.x - c.x, dy = cam.y - c.y, dz = cam.z - c.z;
  const e = (Math.atan2(dy, Math.hypot(dx, dz)) * 180) / Math.PI;
  return e < 0 ? -(90 + e) : 90 - e;
}

// Índice do quadro "disk" mais perto da inclinação (prev = quadro atual, para a histerese).
export function pickCell(cells, incl, prev = -1) {
  let best = -1, bestD = Infinity;
  for (let i = 0; i < cells.length; i++) {
    if (cells[i].kind !== "disk") continue;
    const d = Math.abs(cells[i].incl - incl);
    if (d < bestD) (best = i), (bestD = d);
  }
  if (prev >= 0 && cells[prev]?.kind === "disk" && Math.abs(cells[prev].incl - incl) <= bestD + HYST) return prev;
  return best;
}

export default {
  name: "impostor",
  setup(ctx) {
    const { fx, layout: L, data } = ctx;
    const { O, F } = L;
    const cells = data.impostor.cells;
    const small = data.impostor.small;
    const BARE = cells.findIndex((c) => c.kind === "bare");
    const { shadowA, shadowB, shadowF } = data.scene;
    const ign = data.disk.ignite;
    const T_ON = ign.ring5, T_FULL = ign.ring1 + 6; // o disco entra junto com os anéis (de fora para dentro)
    const T_OFF = 619;
    let cur = -1;
    const curAB = [-1, -1];
    // sem câmera (sgx:from sem pose ainda): a vista de 75°, de onde o jogador olha
    const cam = () => ctx.pose?.p ?? { x: O.x - F.x * 100, y: O.y + 26, z: O.z - F.z * 100 };
    const spawn = (pos, cell, half, tint = 1) =>
      fx.spawn(ID, pos, { lf: LIFE, s: half * cells[cell].hw, c0: [tint, tint, tint], incl: cell });

    const spawnSmall = (pos, i, shadow) => {
      curAB[i] = pickCell(small.cells, inclination(cam(), pos), curAB[i]);
      fx.spawn(ID_SMALL, pos, { lf: LIFE, s: shadow * small.hw, c0: [1, 1, 1], incl: curAB[i] });
    };

    ctx.hook("bh.pair", (t) => {
      if (t % 2) return;
      const b = L.binary(t);
      if (t >= 20) spawnSmall(b.A, 0, shadowA);
      if (t >= 40) spawnSmall(b.B, 1, shadowB);
    }, { win: [20, 239] });

    ctx.hook("bh.hole", (t) => {
      if (t % 2) return;
      const s = shadowF * L.scaleAt(t);
      if (s <= 0.01) return;
      const disk = t >= T_ON && t <= T_OFF;
      const fade = Math.min(1, Math.max(0, (t - T_ON) / (T_FULL - T_ON)));
      if (!disk || fade < 1) {
        // por baixo do disco durante a entrada: um pouco atrás (longe da câmera) para a ordem não piscar
        const p = cam(), d = Math.hypot(O.x - p.x, O.y - p.y, O.z - p.z) || 1;
        const back = disk ? 0.05 : 0;
        spawn({ x: O.x + ((O.x - p.x) / d) * back, y: O.y + ((O.y - p.y) / d) * back, z: O.z + ((O.z - p.z) / d) * back }, BARE, s);
      }
      if (!disk) return;
      cur = pickCell(cells, inclination(cam(), O), cur);
      spawn(O, cur, s, fade);
    }, { win: [240, 699] });
  },
};
