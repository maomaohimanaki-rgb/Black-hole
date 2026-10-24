// Caixas cinzas do animatic (F1): tudo que o filme vai ter, em partícula simples, no lugar e no
// tempo certos. Some na F4–F7, quando cada módulo de verdade entra.
//  - A e B: sombra preta + halo prata, na órbita certa (binary_math.js), 20–239
//  - ondulações no chão nas 19 meias-órbitas + a onda gravitacional no 240
//  - buraco final com o ringdown e a curva de escala, 240–699
//  - disco: 5 anéis de pontos keplerianos acendendo de fora para dentro, 280–619
//  - jatos (1 partícula persistente para cima e 1 para baixo), 360–419
//  - pedaço-herói, 460–539 · faíscas de Hawking, 620–699 · clarão final, 700

import { madd } from "../../engine/vec.js";
import { hexToRgb } from "../../engine/fx.js";

const ID = "singularity:sgx_gizmo";
const ADD = "singularity:sgx_gizmo_add";
const C = {
  silver: hexToRgb("#D8E2F0"),
  ring: hexToRgb("#FFE7B0"),
  black: [0, 0, 0],
  jet: hexToRgb("#8FA8FF"),
  chunk: hexToRgb("#B8A48C"),
  ice: hexToRgb("#E8FBFF"),
  rings: ["#DCE4FF", "#FFF4EA", "#FFB46B", "#FF8A3D", "#FF6A1E"].map(hexToRgb),
};
const SHADOW_A = 1.21, SHADOW_B = 0.97, SHADOW_F = 2.08;
const POINTS_PER_RING = 12;

export default {
  name: "gizmos",
  setup(ctx) {
    const { fx, layout: L, data } = ctx;
    const { O, G, U } = L;
    const life2 = { lf: [0.12, 0.01, 0.01] };

    // Par A/B
    ctx.hook("binary", (t) => {
      const b = L.binary(t);
      if (t >= 20) {
        fx.spawn(ID, b.A, { ...life2, s: SHADOW_A, c0: C.black });
        fx.spawn(ADD, b.A, { ...life2, s: SHADOW_A * 1.5, c0: C.silver, a: 0.5 });
      }
      if (t >= 40) {
        fx.spawn(ID, b.B, { ...life2, s: SHADOW_B, c0: C.black });
        fx.spawn(ADD, b.B, { ...life2, s: SHADOW_B * 1.5, c0: C.silver, a: 0.5 });
      }
    }, { win: [20, 239] });

    // Ondulações (1 chamada cada; a curva está no Molang da sgx_p_ripple)
    const ground = madd(G, [U, 0.15]);
    for (const t of data.halfOrbits) {
      ctx.at(t, () => fx.spawn("singularity:sgx_p_ripple", ground, { lf: [1.2, 0.05, 0.6], s: [2, 18, 0], c0: C.silver, a: 0.8 }), { tag: "gizmos.ripple" });
    }
    ctx.at(data.gwShell.t0, () => {
      const life = data.gwShell.max_radius / data.gwShell.speed_blocks_per_tick / 20;
      fx.spawn("singularity:sgx_p_ripple", ground, { lf: [life, 0.02, life * 0.5], s: [2, data.gwShell.max_radius, 0], c0: C.silver, a: 1 });
    }, { tag: "gizmos.gw" });

    // Buraco final (a cada 2 ticks, vida de 3)
    ctx.hook("hole", (t) => {
      if (t % 2) return;
      const s = SHADOW_F * L.scaleAt(t);
      if (s <= 0.01) return;
      fx.spawn(ID, O, { lf: [0.16, 0.01, 0.02], s, c0: C.black });
      fx.spawn(ADD, O, { lf: [0.16, 0.01, 0.02], s: s * 1.35, c0: C.ring, a: 0.7 });
    }, { win: [240, 699] });

    // Disco: um anel por tick (rodízio), 12 pontos, vida de 6 ticks. ω ∝ r^-3/2 (Kepler).
    const rings = data.disk.rings;
    const ignite = [data.disk.ignite.ring1, data.disk.ignite.ring2, data.disk.ignite.ring3, data.disk.ignite.ring4, data.disk.ignite.ring5];
    ctx.hook("disk", (t) => {
      const k = t % 5;
      if (t < ignite[k]) return;
      const [r0, r1] = rings[k];
      const r = (r0 + r1) / 2;
      const w = 180 * Math.pow(r / rings[0][0], -1.5); // °/s
      const base = ((w * t) / 20) * (Math.PI / 180);
      for (let i = 0; i < POINTS_PER_RING; i++) {
        const a = base + (2 * Math.PI * i) / POINTS_PER_RING;
        const p = L.toWorld(O, Math.sin(a) * r, Math.cos(a) * r, 0);
        fx.spawn(ADD, p, { lf: [0.3, 0.02, 0.1], s: 0.35 + 0.1 * k, c0: C.rings[k], a: 0.9 });
      }
    }, { win: [280, 619] });

    // Jatos: 2 partículas persistentes (centro no MEIO do jato, tamanho = meia-largura/meia-altura, P-23)
    ctx.at(data.jets.tOn, () => {
      const life = (data.jets.tFade[1] - data.jets.tOn) / 20;
      const up = data.jets.up / 2;
      fx.spawn("singularity:sgx_p_jet_core", madd(O, [U, up]), { lf: [life, 0.05, 1.0], s: [0.6, up, 0], c0: C.jet, a: 1 });
      const down = (O.y - (G.y - 28)) / 2;
      fx.spawn("singularity:sgx_p_jet_core", madd(O, [U, -down]), { lf: [life, 0.05, 1.0], s: [0.6, down, 0], c0: C.jet, a: 1 });
    }, { tag: "gizmos.jets" });

    // Pedaço-herói
    ctx.hook("hero", (t) => {
      fx.spawn(ID, L.heroChunk(t), { ...life2, s: 0.6, c0: C.chunk });
    }, { win: [460, 539] });

    // Hawking: faíscas branco-gelo em volta do remanescente
    ctx.hook("hawking", (t) => {
      if (t % 3) return;
      const s = SHADOW_F * L.scaleAt(t);
      for (let i = 0; i < 3; i++) {
        const a = t * 1.7 + i * 2.1, e = Math.sin(t * 0.9 + i);
        const p = L.toWorld(O, Math.cos(a) * (s + 0.6), Math.sin(a) * (s + 0.6), e * (s + 0.3));
        fx.spawn(ADD, p, { lf: [0.4, 0.02, 0.3], s: 0.25, c0: C.ice, a: 1 });
      }
    }, { win: [620, 699] });

    ctx.at(700, () => fx.spawn(ADD, O, { lf: [1.5, 0.05, 1.2], s: 30, c0: C.ice, a: 0.8 }), { tag: "gizmos.burst" });
  },
};
