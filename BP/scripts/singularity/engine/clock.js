// Relógio único do filme (ARCHITECTURE §4.1). Todo efeito é "dispare quando t ≥ N".
// Nada de runTimeout encadeado: ele acumula erro (P-03).

export class TickScheduler {
  constructor() {
    this.cues = [];
    this.sealed = false;
    this.errors = [];
    this._seq = 0;
    this._next = 0; // índice do próximo cue a disparar (a lista é ordenada no seal)
  }

  // Tick fracionário arredonda. order desempata no mesmo tick (menor primeiro).
  at(tick, fn, { order = 0, tag = "" } = {}) {
    if (this.sealed) throw new Error(`scheduler selado: cue '${tag}' em ${tick} chegou tarde`);
    this.cues.push({ tick: Math.round(tick), order, seq: this._seq++, fn, tag });
  }

  seal() {
    if (this.sealed) return;
    this.cues.sort((a, b) => a.tick - b.tick || a.order - b.order || a.seq - b.seq);
    this.sealed = true;
  }

  // Dispara em ordem tudo com tick ≤ t. Um cue com erro não derruba o filme.
  advanceTo(t) {
    if (!this.sealed) this.seal();
    let fired = 0;
    while (this._next < this.cues.length && this.cues[this._next].tick <= t) {
      const c = this.cues[this._next++];
      try {
        c.fn(c.tick);
      } catch (e) {
        this.errors.push({ tick: c.tick, tag: c.tag, error: String(e?.stack ?? e) });
      }
      fired++;
    }
    return fired;
  }

  // Preview "from <t>": descarta sem executar o que vem antes de t.
  skipBefore(t) {
    if (!this.sealed) this.seal();
    while (this._next < this.cues.length && this.cues[this._next].tick < t) this._next++;
  }

  get pending() {
    return this.cues.length - this._next;
  }
}

// t vem do relógio de parede (o áudio toca em tempo real), mas:
//  - nunca volta;
//  - nunca fica atrás dos ticks do servidor;
//  - nunca passa mais de MAX_LEAD ticks na frente deles;
//  - pausa > REANCHOR_MS entre ticks (menu, app em segundo plano) reancora em vez de pular.
export const MAX_LEAD = 40;
export const REANCHOR_MS = 2500;

export class MasterClock {
  constructor({ now, scheduler, startTick = 0, endTick = Infinity, onTick, onStop } = {}) {
    this.now = now ?? (() => Date.now());
    this.scheduler = scheduler;
    this.startTick = startTick;
    this.endTick = endTick;
    this.onTick = onTick;
    this.onStop = onStop;
    this.t = startTick - 1;
    this.serverTicks = 0;
    this.running = false;
    this.stopped = false;
    this.stopReason = null;
    this.lag = { skippedFrames: 0, maxSkip: 0, reanchors: 0 };
  }

  // O tick inicial dispara NA MESMA chamada do start: o som do tick 0 não atrasa.
  start() {
    if (this.running || this.stopped) return;
    this.running = true;
    if (this.startTick > 0) this.scheduler.skipBefore(this.startTick);
    this._anchorMs = this.now();
    this._anchorTick = this.startTick;
    this._lastMs = this._anchorMs;
    this._step(this.startTick);
  }

  // Chamado uma vez por tick do servidor.
  tick() {
    if (!this.running) return;
    this.serverTicks++;
    const ms = this.now();
    if (ms - this._lastMs > REANCHOR_MS) {
      // Reancora: continua de onde parou, como se a pausa não tivesse existido.
      this._anchorMs = ms;
      this._anchorTick = this.t + 1;
      this.lag.reanchors++;
    }
    this._lastMs = ms;
    const wall = this._anchorTick + Math.floor((ms - this._anchorMs) / 50);
    const floor = this.startTick + this.serverTicks; // nunca atrás do servidor
    const ceil = floor + MAX_LEAD; // nunca muito na frente
    let target = Math.min(Math.max(wall, floor, this.t + 1), ceil);
    if (target <= this.t) target = this.t + 1;
    const skip = target - this.t - 1;
    if (skip > 0) {
      this.lag.skippedFrames += skip;
      this.lag.maxSkip = Math.max(this.lag.maxSkip, skip);
    }
    this._step(target);
  }

  _step(target) {
    this.t = Math.min(target, this.endTick);
    this.scheduler.advanceTo(this.t);
    if (this.onTick) this.onTick(this.t);
    if (this.t >= this.endTick) this.stop("end");
  }

  stop(reason = "stop") {
    if (this.stopped) return;
    this.stopped = true;
    this.running = false;
    this.stopReason = reason;
    if (this.onStop) this.onStop(reason);
  }
}
