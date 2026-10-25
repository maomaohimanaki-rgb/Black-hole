// Áudio do filme: cópia 2D para quem está na cutscene (P-45) e posicional em O para os outros
// jogadores por perto, nos MESMOS ticks.
// v0.2.0: os sons vêm do motor de áudio (tools/synth/render.py) e a lista de SOUND_CUES do
// timeline_data.js gerado a partir dele (o áudio conferido na ida e volta é o que toca).

import { SOUND_CUES } from "../timeline_data.js";

export const sound2d = (id) => `singularity:sgx2d_${id.slice(4)}`;
export const sound3d = (id) => `singularity:${id}`;

// P-46: a primeira reprodução atrasa. Toca tudo bem baixinho quando o menu abre.
export function precache(player, sounds = SOUND_CUES) {
  for (const s of sounds) {
    if (s.mode === "outside") continue;
    try {
      player.playSound(sound2d(s.sound), { volume: 0.0001 });
    } catch {}
  }
}

export default {
  name: "audio",
  setup(ctx) {
    const { player, layout, world } = ctx;
    for (const s of SOUND_CUES) {
      if (s.tick < (ctx.options.from ?? 0)) continue;
      ctx.at(s.tick, () => {
        if (s.mode !== "outside") player.playSound(sound2d(s.sound), { volume: s.volume });
        if (s.mode !== "cutscene") {
          for (const p of world.getPlayers()) {
            if (p.id === player.id || p.dimension.id !== player.dimension.id) continue;
            p.playSound(sound3d(s.sound), { location: layout.O, volume: s.volume });
          }
        }
      }, { order: -10, tag: `audio.${s.sound}` });
    }
  },
};
