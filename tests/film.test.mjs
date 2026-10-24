// O animatic inteiro no harness: roda do 0 ao 740 e confere orçamento, silêncio, segurança e limpeza.
import { test } from "node:test";
import assert from "node:assert/strict";
import { makeGame } from "./harness.mjs";
import { startFilm, activeFilm } from "../BP/scripts/singularity/engine/cutscene.js";
import { BLACKHOLE } from "../BP/scripts/singularity/blackhole/film.js";
import { BUS_CLEAR } from "../BP/scripts/singularity/engine/ui_bus.js";

const G = { x: 0.5, y: 64, z: 60.5 };

function play(game, options = {}) {
  let report = null;
  const r = startFilm({
    system: game.system, world: game.world, mc: game.mc, player: game.player, now: game.now,
    layout: BLACKHOLE.layout(game.player.location, G),
    data: BLACKHOLE.data, modules: BLACKHOLE.modules,
    options: { ...options, onEnd: (rep) => (report = rep) },
  });
  assert.ok(!r.error, r.error);
  return () => report;
}

test("filme inteiro: 740 ticks sem erro, dentro do orçamento de partículas", () => {
  const game = makeGame();
  const rep = play(game);
  game.run(800);
  const r = rep();
  assert.ok(r, "o filme terminou");
  assert.equal(r.reason, "end");
  assert.deepEqual(r.cueErrors, []);
  assert.deepEqual(r.hookErrors, []);
  // spec/budgets.json: média ≤ 60 e pico ≤ 120 partículas por tick
  const per = new Map();
  for (const p of game.log.particles) per.set(p.tick, (per.get(p.tick) ?? 0) + 1);
  const peak = Math.max(...per.values());
  const avg = game.log.particles.length / 740;
  assert.ok(peak <= 120, `pico ${peak}`);
  assert.ok(avg <= 60, `média ${avg.toFixed(1)}`);
  assert.equal(activeFilm(), null);
});

test("filme inteiro: silêncio e preto em 600–619", () => {
  const game = makeGame();
  play(game);
  game.run(800);
  const t0 = 1; // o tick 0 do filme cai no tick 0 do harness (start) → tick do harness = t do filme
  for (const s of game.log.sounds) assert.ok(!(s.tick >= 600 + t0 - 1 && s.tick <= 619 + t0 - 1), `${s.id} no ${s.tick}`);
  const titles = game.log.titles.filter((x) => x.tick >= 600 && x.tick <= 619);
  for (const x of titles) assert.match(x.text, /LB=99;/);
});

test("filme inteiro: título só quando muda; câmera 1 pacote por tick no máximo", () => {
  const game = makeGame();
  play(game);
  game.run(800);
  const texts = game.log.titles.map((x) => x.text);
  for (let i = 1; i < texts.length; i++) {
    const gap = game.log.titles[i].tick - game.log.titles[i - 1].tick;
    if (texts[i] === texts[i - 1]) assert.ok(gap >= 100 || texts[i] === BUS_CLEAR, `reenvio cedo no ${game.log.titles[i].tick}`);
  }
  const perTick = new Map();
  for (const c of game.log.camera) perTick.set(c.tick, (perTick.get(c.tick) ?? 0) + 1);
  for (const [t, n] of perTick) assert.ok(n <= 2, `${n} pacotes de câmera no tick ${t}`); // 1 + o clear do fim
  assert.ok(game.log.titles.length < 740 / 2, `${game.log.titles.length} títulos`);
});

test("segurança: noite fixa e sem mobs no filme, tudo restaurado no fim", () => {
  const game = makeGame();
  play(game);
  game.run(5);
  assert.equal(game.rules.doMobSpawning, false);
  assert.equal(game.rules.doDayLightCycle, false);
  assert.ok([14500, 21500].includes(game.timeOfDay));
  assert.ok(game.tags.has("cinematic_busy"));
  game.run(800);
  assert.equal(game.rules.doMobSpawning, true);
  assert.equal(game.rules.doDayLightCycle, true);
  assert.equal(game.timeOfDay, 6000);
  assert.ok(!game.tags.has("cinematic_busy"));
  assert.equal(game.props["sgx:restore"], undefined);
  assert.ok(game.log.camera.at(-1).clear);
  assert.equal(game.log.titles.at(-1).text, BUS_CLEAR);
});

test("servidor lento (12 TPS): o relógio segue o tempo real e termina", () => {
  const game = makeGame({ msPerTick: 83 });
  const rep = play(game);
  game.run(800);
  const r = rep();
  assert.ok(r);
  assert.ok(r.ticks < 740, `${r.ticks} ticks executados`);
  assert.ok(r.skipped > 0);
});

test("from 500: começa no meio, sem tocar os sons de antes", () => {
  const game = makeGame();
  play(game, { from: 500 });
  game.run(300);
  assert.ok(game.log.sounds.every((s) => !["singularity:sgx2d_chirp", "singularity:sgx2d_void_in"].includes(s.id)));
  assert.ok(game.log.sounds.some((s) => s.id === "singularity:sgx2d_horizon"));
});

test("não começa dois filmes ao mesmo tempo", () => {
  const game = makeGame();
  play(game);
  const r = startFilm({
    system: game.system, world: game.world, mc: game.mc, player: game.player, now: game.now,
    layout: BLACKHOLE.layout(game.player.location, G), data: BLACKHOLE.data, modules: BLACKHOLE.modules,
  });
  assert.equal(r.error, "busy");
  game.run(800);
});
