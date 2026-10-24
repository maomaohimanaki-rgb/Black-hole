// Tela pelo barramento (VISUAL_TECH §8): letterbox (LB), desvio para o vermelho (RS),
// flashes (FL) e impacto negativo (IN). Todo flash < 0,4 s vai por overlay (P-08).

import { sampleCurve } from "../../engine/easing.js";

const FULL_VIS = 0.5625; // 16:9

// Altura visível (fração da largura) → código LB (1–98; 99 = fechado). Ver tools/gen_ui.py.
export function lbCode(vis) {
  if (vis <= 0.0005) return 99;
  return Math.min(98, Math.max(1, Math.round(99 - (vis / FULL_VIS) * 98)));
}

// Alfas (1–9) do flash por nível, tick a tick.
const FLASH_SEQ = { N1: [4, 2], N2: [6, 3, 1], N3: [9, 9, 5, 2], N4: [9, 9, 9, 6, 3, 1] };

// Lista de {t, code} já resolvida (o último que cobre o tick vence).
export function buildFlashTrack(blocks) {
  const fl = [], imp = [];
  for (const b of blocks) {
    for (const f of b.flash) {
      if (f.kind === "impact_negative") {
        imp.push([f.t, f.t + (f.dur ?? 2) - 1]);
        continue;
      }
      const seq = FLASH_SEQ[f.level] ?? FLASH_SEQ.N2;
      const color = f.kind === "negative_micro" ? 4 : f.color;
      seq.forEach((a, i) => fl.push({ t: f.t + i, code: color * 10 + a }));
    }
  }
  return { fl, imp };
}

export default {
  name: "screen",
  setup(ctx) {
    const { data, ui } = ctx;
    const end = data.meta.filmTicks;
    const { fl, imp } = buildFlashTrack(data.blocks);
    const flAt = new Map();
    for (const f of fl) flAt.set(f.t, f.code);

    ctx.hook("letterbox", (t) => {
      ui.set("LB", lbCode(sampleCurve(data.letterbox, "vis", t)));
    }, { win: [0, end - 1] });

    ctx.hook("grade", (t) => {
      ui.set("RS", Math.round(sampleCurve(data.grade, "redshift", t) * 20));
    }, { win: [0, end - 1] });

    ctx.hook("flash", (t) => {
      // O impacto negativo é o único quadro da tela: nenhum flash por cima dele.
      const inImpact = imp.some(([a, z]) => t >= a && t <= z);
      ui.set("IN", inImpact ? 1 : 0);
      ui.set("FL", inImpact ? 0 : flAt.get(t) ?? 0);
    }, { win: [0, end - 1] });

    // Saída (outro): tela limpa.
    ctx.at(end, () => {
      for (const c of ["LB", "RS", "FL", "IN"]) ui.set(c, 0);
    }, { tag: "screen.outro" });
  },
};
