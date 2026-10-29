// F0: os 10 testes de renderização (VISUAL_TECH §10). /scriptevent sgx:spike <1–11>
// v0.3.1: S-11 = a entidade do buraco negro (malha + lente + uv_anim) com a câmera passando por cima e por baixo.
// Cada teste monta a cena na frente do jogador, explica no chat o que olhar e se desfaz sozinho.
// Resultado vai para docs/SPIKES.md.

import { v3, add, mul, norm, cross, madd, sub, dirToRot } from "../engine/vec.js";
import { UiBus } from "../engine/ui_bus.js";
import { lbCode } from "../blackhole/modules/screen.js";
import { releaseCamera } from "../engine/safety.js";
import { openStage, closeStage } from "../engine/stage.js";
import { ID as BH_ID, elevation, pickBin, binValue } from "../blackhole/modules/bh.js";
import { DATA } from "../blackhole/storyboard_data.js";

const SPIKE_AREA = "sgx_spike";

const NS = "singularity";
let running = null;

export const spikeRunning = () => running != null;

function frame(player) {
  const P = player.location;
  const d = player.getViewDirection();
  const F = norm(v3(d.x, 0, d.z));
  const U = v3(0, 1, 0);
  const R = cross(F, U);
  const eye = add(P, v3(0, 1.62, 0));
  return { P, F, R, U, eye };
}

function groundAt(dim, p) {
  try {
    const b = dim.getTopmostBlock({ x: Math.floor(p.x), z: Math.floor(p.z) });
    if (b) return v3(p.x, b.location.y + 1, p.z);
  } catch {}
  return v3(p.x, p.y, p.z);
}

function lookCam(env, pos, target, easeIt = true) {
  const r = dirToRot(sub(target, pos));
  const o = { location: pos, rotation: { x: r.pitch, y: r.yaw } };
  if (easeIt) o.easeOptions = { easeTime: 0.05, easeType: env.mc.EasingType.Linear };
  env.player.camera.setCamera("minecraft:free", o);
}

function orbit(env, center, radius, height, seconds) {
  return (t) => {
    const a = (2 * Math.PI * t) / (seconds * 20);
    const pos = madd(center, [env.F, -Math.cos(a) * radius], [env.R, Math.sin(a) * radius], [env.U, height]);
    lookCam(env, pos, center, t > 0);
  };
}

function spawnFx(env, id, pos, props = {}) {
  const e = env.dim.spawnEntity(id, pos);
  for (const [k, v] of Object.entries(props)) e.setProperty(`${NS}:${k}`, v); // P-28: no spawn
  env.cleanup.push(() => {
    try {
      if (e.isValid) e.remove();
    } catch {}
  });
  return e;
}

function particle(env, id, pos, vars) {
  const m = new env.mc.MolangVariableMap();
  const V = (a) => ({ x: a[0], y: a[1] ?? a[0], z: a[2] ?? a[0] });
  m.setVector3("variable.lf", V(vars.lf));
  m.setVector3("variable.s", V(vars.s ?? [1]));
  m.setVector3("variable.a", V([vars.a ?? 1]));
  m.setVector3("variable.c0", V(vars.c0 ?? [1, 1, 1]));
  if (vars.incl != null) m.setVector3("variable.incl", V([vars.incl]));
  env.dim.spawnParticle(id, pos, m);
}

// Cada teste: {ticks, setup(env) → tick(t)}
const SPIKES = {
  1: {
    ticks: 240,
    stage: (env) => madd(env.P, [env.F, 100], [env.U, 30]),
    setup(env) {
      // v0.2.4: escala B, o disco tem 42 blocos de raio
      const O = madd(env.P, [env.F, 100], [env.U, 30]);
      spawnFx(env, `${NS}:sgx_disk`, O, { lit: 5, heat: 1.0, scale: 1.0 });
      const cam = orbit(env, O, 90, 18, 12);
      return (t) => {
        cam(t);
        if (t % 10 === 0) particle(env, `${NS}:sgx_spike_shadow`, O, { lf: [0.6, 0.01, 0.01], s: [9.1] });
      };
    },
  },
  2: {
    ticks: 240,
    setup(env) {
      const C = madd(env.P, [env.F, 10], [env.U, 1]);
      spawnFx(env, `${NS}:sgx_spike_bb_cam`, madd(C, [env.U, 2.5]));
      spawnFx(env, `${NS}:sgx_spike_bb_rot`, madd(C, [env.U, -0.5]));
      return orbit(env, madd(C, [env.U, 2.5]), 9, 2, 12);
    },
  },
  3: {
    ticks: 300,
    stage: (env) => madd(env.P, [env.F, 70], [env.U, 20]),
    setup(env) {
      spawnFx(env, `${NS}:sgx_disk`, madd(env.P, [env.F, 70], [env.U, 20]), { lit: 1, heat: 1.0, scale: 1.0 });
      return () => {};
    },
  },
  4: {
    ticks: 160,
    setup(env) {
      const G = groundAt(env.dim, madd(env.P, [env.F, 25]));
      for (let i = 0; i < 20; i++) {
        spawnFx(env, `${NS}:sgx_debris`, G, {
          r0: 8 + (22 * i) / 19,
          phi0: (i * 137.5) % 360 - 180,
          y0: 0.0,
          tc: 4 + (i % 5) * 0.4,
          spin: (i % 2 ? 1 : -1) * 360,
          kind: i % 16,
        });
      }
      return () => {};
    },
  },
  5: {
    ticks: 180,
    setup(env) {
      env.player.playSound(`${NS}:sgx2d_spike_pan`, { volume: 1 });
      return () => {};
    },
  },
  6: {
    ticks: 220,
    setup(env) {
      const C = madd(env.P, [env.F, 9], [env.U, 2]);
      for (let i = 0; i < 4; i++) {
        particle(env, `${NS}:sgx_spike_atlas`, madd(C, [env.R, (i - 1.5) * 3]), { lf: [10, 0.1, 0.3], s: [1.4], incl: i });
      }
      particle(env, `${NS}:sgx_p_impostor`, madd(C, [env.U, 4]), { lf: [10, 0.1, 0.3], s: [2.5] });
      return () => {};
    },
  },
  7: {
    ticks: 300,
    setup(env) {
      spawnFx(env, `${NS}:sgx_spike_mesh`, madd(env.P, [env.F, 12], [env.U, 3]));
      return () => {};
    },
  },
  8: {
    ticks: 300,
    setup(env) {
      const ui = new UiBus({
        send: (text, stay) => env.player.onScreenDisplay.setTitle(text, { stayDuration: stay, fadeInDuration: 0, fadeOutDuration: 0 }),
      });
      env.cleanup.push(() => ui.clear());
      // 0–160: 16:9 → 2,39 → 3,2 → fechado → abre. 170–290: flashes (cor 0–4, 6 ticks cada).
      const vis = (t) => {
        if (t < 30) return 1 / 1.78;
        if (t < 60) return 1 / (1.78 + (2.39 - 1.78) * ((t - 30) / 30));
        if (t < 90) return 1 / (2.39 + (3.2 - 2.39) * ((t - 60) / 30));
        if (t < 120) return (1 / 3.2) * (1 - (t - 90) / 30);
        if (t < 140) return 0;
        return 1 / 1.78;
      };
      return (t) => {
        ui.set("LB", t < 160 ? lbCode(vis(t)) : 0);
        const f = t - 170;
        ui.set("FL", f >= 0 && f < 120 && f % 24 < 6 ? Math.floor(f / 24) * 10 + 9 : 0);
        ui.flush(t);
      };
    },
  },
  9: {
    ticks: 240,
    setup(env) {
      const pos = env.eye, target = madd(env.eye, [env.F, 10]);
      lookCam(env, pos, target, false);
      const Linear = env.mc.EasingType.Linear;
      return (t) => {
        const period = t < 120 ? 3 : 6;
        if (t % period) return;
        const fov = Math.floor(t / period) % 2 ? 75 : 65;
        env.player.camera.setFov({ fov, easeOptions: { easeTime: 0.05, easeType: Linear } });
      };
    },
  },
  10: {
    ticks: 180,
    setup(env) {
      const T = groundAt(env.dim, madd(env.P, [env.F, 14]));
      const cows = [];
      for (let i = 0; i < 10; i++) {
        const a = (2 * Math.PI * i) / 10;
        cows.push(spawnFx(env, "minecraft:cow", groundAt(env.dim, madd(T, [env.F, Math.cos(a) * 9], [env.R, Math.sin(a) * 9]))));
      }
      env.cleanup.push(() => env.player.sendMessage({ translate: "sgx.spike.10.after" }));
      return (t) => {
        if (t % 4) return;
        particle(env, `${NS}:sgx_gizmo_add`, madd(T, [env.U, 0.5]), { lf: [0.25, 0.01, 0.05], s: [0.6], c0: [1, 0.8, 0.2] });
        if (t >= 160) return;
        for (const c of cows) {
          if (!c.isValid) continue;
          const d = sub(T, c.location);
          d.y = 0;
          const k = Math.min(0.45, 0.04 * Math.hypot(d.x, d.z));
          c.applyImpulse(add(mul(norm(d), k), v3(0, 0.05, 0)));
        }
      };
    },
  },
  // v0.3.1 (T-25): o buraco negro em geometria, todos os anéis acesos. A câmera dá uma volta acima do disco e
  // outra abaixo: confere a orientação da malha (sgx:cal), o giro da textura e o espelho de baixo.
  11: {
    ticks: 480,
    stage: (env) => madd(env.P, [env.F, 100], [env.U, 30]),
    setup(env) {
      const O = madd(env.P, [env.F, 100], [env.U, 30]);
      const bins = DATA.lens.bins;
      let cur = pickBin(bins, 10);
      let sent = binValue(cur, 10);
      const e = spawnFx(env, BH_ID, O, { t0: 16.0, cal: env.cal ?? 0, bin: sent });
      const up = orbit(env, O, 95, 17, 12), down = orbit(env, O, 95, -17, 12);
      return (t) => {
        (t < 240 ? up : down)(t);
        const a = (2 * Math.PI * t) / 240;
        const camPos = madd(O, [env.F, -Math.cos(a) * 95], [env.R, Math.sin(a) * 95], [env.U, t < 240 ? 17 : -17]);
        const el = elevation(camPos, O);
        cur = pickBin(bins, el, cur);
        const v = binValue(cur, el);
        if (v !== sent && e.isValid) e.setProperty(`${NS}:bin`, (sent = v));
      };
    },
  },
};

export const SPIKE_COUNT = Object.keys(SPIKES).length;

export async function runSpike(n, { player, mc, system, world, cal = 0 }) {
  const s = SPIKES[n];
  if (!s) {
    player.sendMessage({ translate: "sgx.spike.unknown" });
    return false;
  }
  if (running) {
    player.sendMessage({ translate: "sgx.spike.busy" });
    return false;
  }
  const env = { player, mc, system, dim: player.dimension, cleanup: [], cal, ...frame(player) };
  player.sendMessage({ translate: `sgx.spike.${n}` });
  if (s.stage && world) {
    // v0.2.5: cena longe (escala B) → área simulando durante o teste
    running = { n, stop: () => {} };
    await openStage({ world, system, dimension: env.dim, center: s.stage(env), id: SPIKE_AREA, radius: 56, below: 24, above: 40 });
    env.cleanup.push(() => closeStage({ world, system, id: SPIKE_AREA, delayTicks: 0 }));
    running = null;
  }
  let tick;
  try {
    tick = s.setup(env);
  } catch (e) {
    player.sendMessage(`§c[S-${String(n).padStart(2, "0")}] ${e}`);
    for (const f of env.cleanup) f();
    return false;
  }
  let t = 0;
  const finish = (silent) => {
    system.clearRun(id);
    for (const f of env.cleanup.reverse()) {
      try {
        f();
      } catch {}
    }
    releaseCamera(player, system);
    running = null;
    if (!silent) player.sendMessage({ translate: "sgx.spike.end", with: [String(n).padStart(2, "0")] });
  };
  const id = system.runInterval(() => {
    try {
      tick(t);
    } catch (e) {
      player.sendMessage(`§c[S-${String(n).padStart(2, "0")}] t=${t}: ${e}`);
      finish(true);
      return;
    }
    if (++t >= s.ticks) finish(false);
  }, 1);
  running = { n, stop: () => finish(false) };
  return true;
}

export function stopSpike() {
  if (!running) return false;
  running.stop();
  return true;
}
