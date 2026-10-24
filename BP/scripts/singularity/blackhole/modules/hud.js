// HUD de texto PROVISÓRIO (F1): legenda (SB), linha técnica (HD) e título (TT/TT2) pela actionbar,
// sempre por chave de tradução (P-50). Na F3 vira PNG assado pelo barramento (P-25).
// Com o trace ligado, mostra também o bloco e o tick (para o retorno do animatic: "no B07, tick 214…").

const TEXT_CH = ["TT", "TT2", "SB", "HD"];

// Estado do HUD no tick t: {SB: key, HD: key, …} (o mais recente que ainda não foi limpo).
export function hudState(events, t) {
  const s = {};
  for (const e of events) {
    if (e.t > t) break;
    if (!e.key) continue;
    if (e.clear != null && t > e.clear) {
      if (s[e.ch] === e.key) delete s[e.ch];
      continue;
    }
    s[e.ch] = e.key;
  }
  return s;
}

export default {
  name: "hud",
  setup(ctx) {
    const { data, player } = ctx;
    const events = data.blocks.flatMap((b) => b.hud).sort((a, b) => a.t - b.t);
    const blockAt = (t) => data.blocks.find((b) => t >= b.ticks[0] && t <= b.ticks[1]);
    let last = "";
    let lastSent = -99;

    ctx.hook("text", (t) => {
      const s = hudState(events, t);
      const parts = [];
      if (ctx.options.trace !== false) {
        const b = blockAt(t);
        parts.push({ text: `§8${b ? b.id : "--"} · ${t - (t % 5)}§r   ` });
      }
      for (const ch of TEXT_CH) {
        if (!s[ch]) continue;
        const style = ch === "TT" ? "§l§f" : ch === "SB" ? "§f" : "§7";
        parts.push({ text: style }, { translate: s[ch] }, { text: "§r   " });
      }
      const sig = JSON.stringify(parts);
      if (sig !== last || t - lastSent >= 30) {
        player.onScreenDisplay.setActionBar(parts.length ? { rawtext: parts } : "");
        last = sig;
        lastSent = t;
      }
    }, { win: [0, data.meta.filmTicks + data.meta.outroTicks - 1] });
  },
};
