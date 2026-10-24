// Áudio do filme: cópia 2D para quem está na cutscene (P-45) e posicional em O para os outros
// jogadores por perto, nos MESMOS ticks. Na F1 os .ogg são bipes provisórios (tools/synth/placeholder.py).

export const sound2d = (id) => `singularity:sgx2d_${id.slice(4)}`;
export const sound3d = (id) => `singularity:${id}`;

// P-46: a primeira reprodução atrasa. Toca tudo bem baixinho quando o menu abre.
export function precache(player, sounds) {
  for (const s of sounds) {
    if (!s.cutscene) continue;
    try {
      player.playSound(sound2d(s.id), { volume: 0.0001 });
    } catch {}
  }
}

export default {
  name: "audio",
  setup(ctx) {
    const { data, player, layout, world } = ctx;
    for (const s of data.sounds) {
      if (s.tick < (ctx.options.from ?? 0)) continue;
      ctx.at(s.tick, () => {
        if (s.cutscene) player.playSound(sound2d(s.id), { volume: s.volume });
        if (s.outside) {
          for (const p of world.getPlayers()) {
            if (p.id === player.id || p.dimension.id !== player.dimension.id) continue;
            p.playSound(sound3d(s.id), { location: layout.O, volume: s.volume });
          }
        }
      }, { order: -10, tag: `audio.${s.id}` });
    }
  },
};
