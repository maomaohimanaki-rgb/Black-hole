// O main.js de verdade, com o jogo falso: menu, scriptevents, os 10 spikes e a restauração após crash.
import { test } from "node:test";
import assert from "node:assert/strict";
import { register } from "node:module";
import { makeGame } from "./harness.mjs";

register("./mc_stub_loader.mjs", import.meta.url);
const game = makeGame();
globalThis.__sgxGame = game;
await import("../BP/scripts/main.js");

const ev = (id, message = "") => game.emit("scriptEventReceive", { id, message, sourceEntity: game.player });
const msgs = () => (game.log.messages ?? []).map((m) => (typeof m.m === "string" ? m.m : m.m.translate));

for (let n = 1; n <= 10; n++) {
  test(`spike ${n}: monta, explica no chat, termina e limpa`, () => {
    game.log.messages = [];
    const before = game.log.entities.length;
    ev("sgx:spike", String(n));
    assert.equal(msgs()[0], `sgx.spike.${n}`);
    game.run(400);
    const m = msgs();
    assert.ok(m.includes("sgx.spike.end"), m.join(" | "));
    assert.ok(!m.some((x) => x.startsWith("§c")), m.join(" | "));
    for (const e of game.log.entities.slice(before)) assert.equal(e.isValid, false, `${e.typeId} ficou no mundo`);
    assert.ok(game.log.camera.at(-1)?.clear, "câmera de volta ao normal");
  });
}

test("spike: número inválido avisa; dois ao mesmo tempo não", () => {
  game.log.messages = [];
  ev("sgx:spike", "99");
  assert.deepEqual(msgs(), ["sgx.spike.unknown"]);
  ev("sgx:spike", "3");
  ev("sgx:spike", "4");
  assert.ok(msgs().includes("sgx.spike.busy"));
  ev("sgx:stop");
  game.run(5);
});

test("sgx:play blackhole roda o animatic inteiro e restaura tudo", () => {
  game.log.messages = [];
  ev("sgx:play", "blackhole");
  assert.ok(game.tags.has("cinematic_busy"));
  game.run(800);
  assert.ok(msgs().includes("sgx.msg.film_done"), msgs().join(" | "));
  assert.ok(!msgs().some((x) => x.startsWith("§c")), msgs().join(" | "));
  assert.ok(!game.tags.has("cinematic_busy"));
});

test("item → menu → BURACO NEGRO começa o filme; sgx:stop para no meio", async () => {
  game.formAnswer = { canceled: false, selection: 0 };
  game.emit("itemUse", { itemStack: { typeId: "singularity:core" }, source: game.player });
  game.run(2);
  await new Promise((r) => setTimeout(r, 0));
  game.run(10);
  assert.ok(game.tags.has("cinematic_busy"));
  ev("sgx:stop");
  assert.ok(!game.tags.has("cinematic_busy"));
  assert.equal(game.rules.doMobSpawning, true);
});

test("crash no meio do filme: o estado volta no próximo spawn (P-44)", () => {
  game.props["sgx:restore"] = JSON.stringify({ time: 1234, daylight: true, mobs: true });
  game.rules.doMobSpawning = false;
  game.tags.add("cinematic_busy");
  game.emit("playerSpawn", { initialSpawn: true, player: game.player });
  game.run(25);
  assert.equal(game.timeOfDay, 1234);
  assert.equal(game.rules.doMobSpawning, true);
  assert.ok(!game.tags.has("cinematic_busy"));
});
