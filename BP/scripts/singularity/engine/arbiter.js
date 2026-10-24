// Orçamento por tick (ARCHITECTURE §4.2). Hooks com janela e prioridade; tarefas de fundo
// fatiadas nas sobras de ms (P-04, P-05).

// v0.1.1: no QuickJS o stack não traz a mensagem do erro; junta os dois.
const errText = (e) => `${e}${e?.stack ? "\n" + e.stack : ""}`;

export const PRIO = { critical: 0, normal: 1, optional: 2 };

export class Arbiter {
  // budgetMs: orçamento do perfil (spec/budgets.json). optionalFrac: optional só roda abaixo disto.
  constructor({ now, budgetMs = 14, optionalFrac = 0.6 } = {}) {
    this.now = now ?? (() => Date.now());
    this.budgetMs = budgetMs;
    this.optionalFrac = optionalFrac;
    this.hooks = [];
    this.jobs = [];
    this.errors = [];
    this.stats = { skipped: 0, forced: 0, ran: 0 };
  }

  // fn(t) com win = [de, até]. Hook sem janela é erro: rodaria o filme inteiro (P-05).
  add(fn, { win, prio = "normal", name = fn.name || "hook" } = {}) {
    win = win ?? fn.win;
    if (!Array.isArray(win) || win.length !== 2) throw new Error(`hook '${name}' sem janela (P-05)`);
    prio = fn.prio ?? prio;
    if (!(prio in PRIO)) throw new Error(`hook '${name}': prioridade '${prio}' inválida`);
    this.hooks.push({ fn, win, prio, name, starved: false });
    this.hooks.sort((a, b) => PRIO[a.prio] - PRIO[b.prio]);
  }

  // Gerador que anda nas sobras. finish(name) completa na hora.
  addJob(name, gen) {
    this.jobs.push({ name, gen, done: false, value: undefined });
  }

  finish(name) {
    const j = this.jobs.find((x) => x.name === name);
    if (!j) return undefined;
    while (!j.done) this._stepJob(j);
    return j.value;
  }

  _stepJob(j) {
    try {
      const r = j.gen.next();
      if (r.done) {
        j.done = true;
        j.value = r.value;
      }
    } catch (e) {
      j.done = true;
      this.errors.push({ job: j.name, error: errText(e) });
    }
  }

  run(t, budgetMs = this.budgetMs) {
    const t0 = this.now();
    const spent = () => this.now() - t0;
    for (const h of this.hooks) {
      if (t < h.win[0] || t > h.win[1]) continue;
      let go = h.prio === "critical" || h.starved;
      if (!go) {
        const limit = h.prio === "optional" ? budgetMs * this.optionalFrac : budgetMs;
        go = spent() < limit;
      }
      if (!go) {
        // Não-inanição: quem ficou de fora roda obrigatoriamente no próximo tick.
        h.starved = true;
        this.stats.skipped++;
        continue;
      }
      if (h.starved) this.stats.forced++;
      h.starved = false;
      try {
        h.fn(t);
      } catch (e) {
        this.errors.push({ t, hook: h.name, error: errText(e) });
      }
      this.stats.ran++;
    }
    for (const j of this.jobs) {
      if (j.done) continue;
      while (!j.done && spent() < budgetMs) this._stepJob(j);
    }
    return spent();
  }
}
