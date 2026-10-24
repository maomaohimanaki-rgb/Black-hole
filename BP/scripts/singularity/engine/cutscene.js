// O orquestrador (ARCHITECTURE §4.9). Não importa @minecraft/server: system, world e os enums
// entram por injeção (mc), para o harness do Node rodar o filme inteiro (princípio 7).

import { TickScheduler, MasterClock } from "./clock.js";
import { Arbiter } from "./arbiter.js";
import { UiBus, BUS_CLEAR } from "./ui_bus.js";
import { Fx } from "./fx.js";
import * as safety from "./safety.js";

// Prioridade padrão por nome de módulo (o módulo pode sobrescrever no hook).
const DEFAULT_PRIO = { camera: "critical", screen: "critical", audio: "critical", hud: "critical", gizmos: "normal" };

let current = null;
export const activeFilm = () => current;

// startFilm({ system, world, mc, player, layout, data, modules, options })
//   modules: [{name, setup(ctx)}], na ordem (a câmera antes de quem usa ctx.pose).
export function startFilm({ system, world, mc, player, layout, data, modules, options = {}, now = () => Date.now() }) {
  if (current) return { error: "busy" };
  if (player.hasTag?.(safety.BUSY_TAG)) return { error: "busy" };

  const from = Math.max(0, Math.floor(options.from ?? 0));
  const endTick = data.meta.filmTicks + data.meta.outroTicks;
  const scheduler = new TickScheduler();
  const arbiter = new Arbiter({ now, budgetMs: options.budgetMs ?? 14 });
  const ui = new UiBus({
    send: (text, stay) => player.onScreenDisplay.setTitle(text, { stayDuration: stay, fadeInDuration: 0, fadeOutDuration: 0 }),
  });
  const fx = new Fx({ dimension: player.dimension, MolangVariableMap: mc.MolangVariableMap });
  const teardowns = [];
  const stats = { ticks: 0, msSum: 0, msPeak: 0, particlesPeak: 0 };

  const ctx = {
    system, world, mc, player, dimension: player.dimension, layout, data, options, ui, fx, arbiter, scheduler,
    pose: null,
    at: (tick, fn, o) => scheduler.at(tick, fn, o),
    hook: (name, fn, { win, prio } = {}) => arbiter.add(fn, { win, prio: prio ?? DEFAULT_PRIO[name] ?? "normal", name }),
    onTeardown: (fn) => teardowns.push(fn),
    warn: (m) => console.warn(`[SGX] ${m}`),
  };

  for (const m of modules) {
    const before = arbiter.hooks.length;
    m.setup(ctx);
    for (const h of arbiter.hooks.slice(before)) h.name = `${m.name}.${h.name}`;
  }

  safety.engage({ world, player, mc, F: layout.F, night: options.night !== false });

  let intervalId = null;
  const clock = new MasterClock({
    now,
    scheduler,
    startTick: from,
    endTick,
    onTick: (t) => {
      const t0 = now();
      fx.tickCalls = 0;
      arbiter.run(t);
      ui.flush(t);
      const ms = now() - t0;
      stats.ticks++;
      stats.msSum += ms;
      stats.msPeak = Math.max(stats.msPeak, ms);
      stats.particlesPeak = Math.max(stats.particlesPeak, fx.tickCalls);
    },
    onStop: (reason) => {
      if (intervalId != null) system.clearRun(intervalId);
      for (let i = teardowns.length - 1; i >= 0; i--) {
        try {
          teardowns[i](reason);
        } catch (e) {
          ctx.warn(`teardown: ${e}`);
        }
      }
      try {
        ui.clear();
        player.onScreenDisplay.setTitle(BUS_CLEAR, { stayDuration: 1, fadeInDuration: 0, fadeOutDuration: 0 });
        player.onScreenDisplay.clearTitle?.();
        player.onScreenDisplay.setActionBar("");
      } catch {}
      safety.restore({ world, player, mc, system });
      const report = {
        reason,
        ticks: stats.ticks,
        skipped: clock.lag.skippedFrames,
        msAvg: stats.ticks ? stats.msSum / stats.ticks : 0,
        msPeak: stats.msPeak,
        particlesPeak: stats.particlesPeak,
        particles: fx.calls,
        cueErrors: scheduler.errors,
        hookErrors: arbiter.errors,
      };
      current = null;
      options.onEnd?.(report);
    },
  });

  current = { clock, ctx, stop: (r = "stop") => clock.stop(r) };
  clock.start();
  if (!clock.stopped) intervalId = system.runInterval(() => clock.tick(), 1);
  return { film: current };
}

export function stopFilm(reason = "stop") {
  if (!current) return false;
  current.stop(reason);
  return true;
}
