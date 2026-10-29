// Caixas cinzas do animatic (F1): tudo que o filme vai ter, em partícula simples, no lugar e no
// tempo certos. Some na F4–F7, quando cada módulo de verdade entra.
//  - (v0.3.0: A, B e o buraco final viraram o impostor, modules/impostor.js)
//  - ondulações no chão nas 19 meias-órbitas + a onda gravitacional no 240
//  - disco: 5 anéis de pontos keplerianos acendendo de fora para dentro, 280–329 (a ignição)
//  - jatos (1 partícula persistente para cima e 1 para baixo), 360–419
//  - pedaço-herói, 460–539 · faíscas de Hawking, 620–699 · clarão final, 700

import { madd } from "../../engine/vec.js";
import { hexToRgb } from "../../engine/fx.js";

const ID = "singularity:sgx_gizmo";
const ADD = "singularity:sgx_gizmo_add";
const C = {
  silver: hexToRgb("#D8E2F0"),
  jet: hexToRgb("#8FA8FF"),
  chunk: hexToRgb("#B8A48C"),
  ice: hexToRgb("#E8FBFF"),
  rings: ["#DCE4FF", "#FFF4EA", "#FFB46B", "#FF8A3D", "#FF6A1E"].map(hexToRgb),
};
const POINTS_PER_RING = 16;

export default {
  name: "gizmos",
  setup(ctx) {
    const { fx, layout: L, data } = ctx;
    const { O, G, U, K } = L;
    const { shadowF: SHADOW_F } = data.scene; // v0.2.4: do spec (escala B)
    const life2 = { lf: [0.12, 0.01, 0.01] };

    // v0.3.0: o par A/B e o buraco final saíram daqui: agora são o impostor (modules/impostor.js).

    // Ondulações (1 chamada cada; a curva está no Molang da sgx_p_ripple)
    const ground = madd(G, [U, 0.15]);
    for (const t of data.halfOrbits) {
      ctx.at(t, () => fx.spawn("singularity:sgx_p_ripple", ground, { lf: [1.2, 0.05, 0.6], s: [2 * K, 18 * K, 0], c0: C.silver, a: 0.8 }), { tag: "gizmos.ripple" });
    }
    ctx.at(data.gwShell.t0, () => {
      const life = data.gwShell.max_radius / data.gwShell.speed_blocks_per_tick / 20;
      fx.spawn("singularity:sgx_p_ripple", ground, { lf: [life, 0.02, life * 0.5], s: [2, data.gwShell.max_radius, 0], c0: C.silver, a: 1 });
    }, { tag: "gizmos.gw" });

    // Disco: um anel por tick (rodízio), 16 pontos, vida de 6 ticks. ω ∝ r^-3/2 (Kepler).
    // v0.3.0: o disco de verdade agora é a imagem do impostor; os pontos ficam só na ignição (os anéis
    // acendendo de fora para dentro, 280–304) e apagam até o 330.
    const rings = data.disk.rings;
    const ignite = [data.disk.ignite.ring1, data.disk.ignite.ring2, data.disk.ignite.ring3, data.disk.ignite.ring4, data.disk.ignite.ring5];
    ctx.hook("disk", (t) => {
      const k = t % 5;
      if (t < ignite[k]) return;
      const fade = Math.min(1, (330 - t) / 16);
      const [r0, r1] = rings[k];
      const r = (r0 + r1) / 2;
      const w = data.disk.omega * Math.pow(r / rings[0][0], -1.5); // °/s
      const base = ((w * t) / 20) * (Math.PI / 180);
      for (let i = 0; i < POINTS_PER_RING; i++) {
        const a = base + (2 * Math.PI * i) / POINTS_PER_RING;
        const p = L.toWorld(O, Math.sin(a) * r, Math.cos(a) * r, 0);
        fx.spawn(ADD, p, { lf: [0.3, 0.02, 0.1], s: (0.35 + 0.1 * k) * K, c0: C.rings[k], a: 0.9 * fade });
      }
    }, { win: [280, 329] });

    // Jatos: 2 partículas persistentes (centro no MEIO do jato, tamanho = meia-largura/meia-altura, P-23)
    ctx.at(data.jets.tOn, () => {
      const life = (data.jets.tFade[1] - data.jets.tOn) / 20;
      const up = data.jets.up / 2;
      fx.spawn("singularity:sgx_p_jet_core", madd(O, [U, up]), { lf: [life, 0.05, 1.0], s: [0.6 * K, up, 0], c0: C.jet, a: 1 });
      const down = (O.y - (G.y - data.scene.craterDepth)) / 2;
      fx.spawn("singularity:sgx_p_jet_core", madd(O, [U, -down]), { lf: [life, 0.05, 1.0], s: [0.6 * K, down, 0], c0: C.jet, a: 1 });
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
        const p = L.toWorld(O, Math.cos(a) * (s + 0.6 * K), Math.sin(a) * (s + 0.6 * K), e * (s + 0.3 * K));
        fx.spawn(ADD, p, { lf: [0.4, 0.02, 0.3], s: 0.25 * K, c0: C.ice, a: 1 });
      }
    }, { win: [620, 699] });

    ctx.at(700, () => fx.spawn(ADD, O, { lf: [1.5, 0.05, 1.2], s: 30 * K, c0: C.ice, a: 0.8 }), { tag: "gizmos.burst" });
  },
};
