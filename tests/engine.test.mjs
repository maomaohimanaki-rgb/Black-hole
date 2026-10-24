import { test } from "node:test";
import assert from "node:assert/strict";
import { TickScheduler, MasterClock, MAX_LEAD } from "../BP/scripts/singularity/engine/clock.js";
import { Arbiter } from "../BP/scripts/singularity/engine/arbiter.js";
import { EASES, ease, lerpAngle, sampleCurve } from "../BP/scripts/singularity/engine/easing.js";
import { CameraTrack } from "../BP/scripts/singularity/engine/camera_engine.js";
import { UiBus, encodeBus } from "../BP/scripts/singularity/engine/ui_bus.js";
import { dirToRot, rotToDir } from "../BP/scripts/singularity/engine/vec.js";

test("scheduler: ordem (tick, order, inserção), selado e erro não derruba", () => {
  const s = new TickScheduler();
  const out = [];
  s.at(5, () => out.push("b"), { order: 1 });
  s.at(5, () => out.push("a"), { order: 0 });
  s.at(4.6, () => out.push("r")); // arredonda para 5, order 0, depois de "a"
  s.at(2, () => {
    throw new Error("x");
  }, { tag: "bomba" });
  s.at(1, () => out.push("1"));
  s.advanceTo(5);
  assert.deepEqual(out, ["1", "a", "r", "b"]);
  assert.equal(s.errors.length, 1);
  assert.equal(s.errors[0].tag, "bomba");
  assert.throws(() => s.at(9, () => {}));
});

function clockWith(endTick = 1000) {
  let ms = 0;
  const s = new TickScheduler();
  const fired = [];
  const c = new MasterClock({ now: () => ms, scheduler: s, endTick, onTick: (t) => fired.push(t) });
  return { c, s, fired, adv: (x) => (ms += x) };
}

test("clock: tick 0 dispara no start", () => {
  const { c, s } = clockWith();
  let hit = false;
  s.at(0, () => (hit = true));
  c.start();
  assert.ok(hit);
  assert.equal(c.t, 0);
});

test("clock: servidor lento → alcança o relógio de parede, até MAX_LEAD na frente", () => {
  const { c, adv } = clockWith(10_000);
  c.start();
  for (let i = 0; i < 100; i++) {
    adv(100); // 10 TPS
    c.tick();
  }
  assert.equal(c.t, Math.min(200, 100 + MAX_LEAD));
  assert.ok(c.lag.skippedFrames > 0);
});

test("clock: nunca atrás do servidor e nunca volta", () => {
  const { c, adv, fired } = clockWith();
  c.start();
  for (let i = 0; i < 50; i++) {
    adv(i % 3 ? 10 : 120);
    c.tick();
  }
  for (let i = 1; i < fired.length; i++) assert.ok(fired[i] > fired[i - 1]);
  assert.ok(c.t >= 50);
});

test("clock: pausa > 2,5 s reancora (não pula)", () => {
  const { c, adv } = clockWith();
  c.start();
  for (let i = 0; i < 10; i++) {
    adv(50);
    c.tick();
  }
  const before = c.t;
  adv(60_000);
  c.tick();
  assert.equal(c.t, before + 1);
  assert.equal(c.lag.reanchors, 1);
});

test("clock: stop idempotente, onStop uma vez, para no endTick", () => {
  let n = 0;
  let ms = 0;
  const c = new MasterClock({ now: () => ms, scheduler: new TickScheduler(), endTick: 5, onStop: () => n++ });
  c.start();
  for (let i = 0; i < 10; i++) {
    ms += 50;
    c.tick();
  }
  c.stop();
  c.stop();
  assert.equal(n, 1);
  assert.equal(c.t, 5);
  assert.equal(c.stopReason, "end");
});

test("clock: from <t> descarta os cues anteriores sem executar", () => {
  let ms = 0;
  const s = new TickScheduler();
  const out = [];
  s.at(10, () => out.push(10));
  s.at(50, () => out.push(50));
  const c = new MasterClock({ now: () => ms, scheduler: s, startTick: 40 });
  c.start();
  for (let i = 0; i < 20; i++) {
    ms += 50;
    c.tick();
  }
  assert.deepEqual(out, [50]);
});

test("arbiter: janela, hook sem janela é erro, não-inanição", () => {
  let ms = 0;
  const a = new Arbiter({ now: () => ms, budgetMs: 10 });
  assert.throws(() => a.add(() => {}, {}));
  const ran = [];
  a.add((t) => {
    ran.push(["crit", t]);
    ms += 12; // estoura o orçamento
  }, { win: [0, 100], prio: "critical", name: "crit" });
  a.add((t) => ran.push(["norm", t]), { win: [0, 100], prio: "normal", name: "norm" });
  a.add((t) => ran.push(["late", t]), { win: [50, 60], prio: "normal", name: "late" });
  a.run(1);
  assert.deepEqual(ran, [["crit", 1]]); // normal ficou de fora…
  a.run(2);
  assert.deepEqual(ran.slice(1), [["crit", 2], ["norm", 2]]); // …e roda obrigatoriamente no seguinte
  assert.equal(a.stats.forced, 1);
});

test("arbiter: tarefa de fundo anda nas sobras e finish() completa na hora", () => {
  let ms = 0;
  const a = new Arbiter({ now: () => ms, budgetMs: 10 });
  function* job() {
    let s = 0;
    for (let i = 0; i < 100; i++) {
      s += i;
      ms += 1;
      yield;
    }
    return s;
  }
  a.addJob("soma", job());
  a.run(0);
  assert.equal(a.jobs[0].done, false);
  assert.equal(a.finish("soma"), 4950);
});

test("easing: todos começam em 0 e terminam em 1", () => {
  for (const [name, f] of Object.entries(EASES)) {
    assert.ok(Math.abs(f(1) - 1) < 1e-9, name);
    if (name !== "step") assert.ok(Math.abs(f(0)) < 1e-9, name);
  }
  assert.equal(ease("step", 0.99), 0);
  assert.throws(() => ease("nada", 0.5));
  assert.equal(lerpAngle(350, 10, 0.5), 360);
  assert.equal(sampleCurve([{ t: 0, v: 0 }, { t: 10, v: 10 }], "v", 5), 5);
});

test("vec: dirToRot ↔ rotToDir (yaw 0 = +Z, pitch + = para baixo)", () => {
  assert.deepEqual(Object.values(dirToRot({ x: 0, y: 0, z: 1 })).map((v) => Math.round(v) + 0), [0, 0]);
  assert.equal(Math.round(dirToRot({ x: -1, y: 0, z: 0 }).yaw), 90);
  assert.equal(Math.round(dirToRot({ x: 0, y: -1, z: 0.0001 }).pitch), 90);
  const d = rotToDir({ pitch: 30, yaw: 120 });
  const r = dirToRot(d);
  assert.ok(Math.abs(r.pitch - 30) < 1e-6 && Math.abs(r.yaw - 120) < 1e-6);
});

test("câmera: cut chega seco, step segura, stutter segura a pose", () => {
  const P = (x) => ({ x, y: 0, z: 0 });
  const L = { x: 0, y: 0, z: 100 };
  const tr = new CameraTrack([
    { t: 0, p: P(0), l: L, fov: 60, ease: "linear" },
    { t: 10, p: P(10), l: L, ease: "linear" },
    { t: 20, p: P(20), l: L, ease: "step", cut: true },
    { t: 40, p: P(40), l: L, ease: "linear", stutter: [2, 4] },
  ]);
  assert.equal(tr.sample(5).p.x, 5);
  assert.equal(tr.sample(15).p.x, 10); // step: segura
  const c = tr.sample(20);
  assert.equal(c.p.x, 20);
  assert.equal(c.cut, true);
  assert.equal(tr.sample(10).fov, 60); // fov herda
  // stutter [2, 4]: atualiza em 22, 26, 30, …
  assert.equal(tr.sample(21).p.x, 20);
  assert.equal(tr.sample(23).p.x, 22);
  assert.equal(tr.sample(25).p.x, 22);
  assert.equal(tr.sample(26).p.x, 26);
});

test("ui bus: canais ordenados com 2 dígitos, só envia quando muda (+ reenvio a cada 100)", () => {
  const sent = [];
  const ui = new UiBus({ send: (t) => sent.push(t) });
  ui.set("LB", 5);
  ui.set("FL", 12);
  assert.equal(encodeBus(ui.ch), "SGXB;FL=12;LB=05;");
  for (let t = 0; t < 150; t++) ui.flush(t);
  assert.equal(sent.length, 2); // t=0 e reenvio no 100
  ui.set("FL", 0);
  ui.flush(150);
  assert.equal(sent.at(-1), "SGXB;LB=05;");
  assert.throws(() => ui.set("lb", 1));
});
