// HUD por título (ARCHITECTURE §4.6): vários canais de 2 letras com valor 00–99 num título só,
// "SGXB;FL=12;LB=11;". O RP/ui/hud_screen.json (gerado) esconde o título (P-13) e liga os
// controles por substring. Envia só quando muda, com reenvio a cada 100 ticks (P-18).

export const BUS_PREFIX = "SGXB";
export const BUS_CLEAR = "SGX_CLEAR";
export const RESEND_TICKS = 100;
export const STAY_TICKS = 160;

export function encodeBus(channels) {
  const keys = Object.keys(channels).filter((k) => channels[k] > 0).sort();
  return BUS_PREFIX + ";" + keys.map((k) => `${k}=${String(channels[k]).padStart(2, "0")};`).join("");
}

export class UiBus {
  // send(text, stayTicks) vira player.onScreenDisplay.setTitle(text, {stayDuration, fadeIn 0, fadeOut 0}).
  constructor({ send }) {
    this.send = send;
    this.ch = {};
    this.lastText = null;
    this.lastSent = -Infinity;
    this.packets = 0;
  }

  set(channel, value) {
    if (!/^[A-Z][A-Z0-9]$/.test(channel)) throw new Error(`canal inválido: ${channel}`);
    const v = Math.max(0, Math.min(99, Math.round(value)));
    if (v === 0) delete this.ch[channel];
    else this.ch[channel] = v;
  }

  get(channel) {
    return this.ch[channel] ?? 0;
  }

  // Uma vez por tick, no fim (hook final do cutscene.js).
  flush(t) {
    const text = encodeBus(this.ch);
    if (text !== this.lastText || t - this.lastSent >= RESEND_TICKS) {
      this.send(text, STAY_TICKS);
      this.lastText = text;
      this.lastSent = t;
      this.packets++;
    }
  }

  clear() {
    this.ch = {};
    this.send(BUS_CLEAR, 1);
    this.lastText = null;
    this.packets++;
  }
}
