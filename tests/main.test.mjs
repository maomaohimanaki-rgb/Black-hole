// O main.js de verdade, com o jogo falso: menu, scriptevents, os 10 spikes, o palco (ticking area) e a
// restauração após crash.
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
// v0.2.5: o filme e alguns spikes esperam a ticking area carregar (promessa): cada tick deixa as
// continuações assíncronas rodarem antes do próximo.
const flush = () => new Promise((r) => setImmediate(r));
async function advance(n) {
  for (let i = 0; i < n; i++) {
    game.run(1);
    await flush();
  }
}

for (let n = 1; n <= 10; n++) {
  test(`spike ${n}: monta, explica no chat, termina e limpa`, async () => {
    game.log.messages = [];
    const before = game.log.entities.length;
    ev("sgx:spike", String(n));
    assert.equal(msgs()[0], `sgx.spike.${n}`);
    await advance(400);
    const m = msgs();
    assert.ok(m.includes("sgx.spike.end"), m.join(" | "));
    assert.ok(!m.some((x) => x.startsWith("§c")), m.join(" | "));
    for (const e of game.log.entities.slice(before)) assert.equal(e.isValid, false, `${e.typeId} ficou no mundo`);
    assert.ok(game.log.camera.at(-1)?.clear, "câmera de volta ao normal");
    // v0.1.1: um clear no mesmo tick do último setCamera com ease perdia para o ease (câmera presa
    // no fim do S-01/S-02). Tem que haver um clear depois que o ease terminou.
    const lastSet = game.log.camera.filter((c) => !c.clear).at(-1)?.tick ?? -99;
    assert.ok(game.log.camera.some((c) => c.clear && c.tick >= lastSet + 3), "clear depois do último ease");
    assert.ok(game.log.commands.some((c) => c.c === "camera @s fov_clear"));
    assert.ok(!game.areas.has("sgx_spike"), "a área do teste some no fim");
  });
}

test("spike 1 (cena longe) abre a área antes de montar", async () => {
  game.log.areas.length = 0;
  ev("sgx:spike", "1");
  await advance(3);
  assert.equal(game.log.areas[0]?.op, "add");
  assert.equal(game.log.areas[0]?.id, "sgx_spike");
  ev("sgx:stop");
  await advance(15);
});

test("spike: número inválido avisa; dois ao mesmo tempo não", async () => {
  game.log.messages = [];
  ev("sgx:spike", "99");
  assert.deepEqual(msgs(), ["sgx.spike.unknown"]);
  ev("sgx:spike", "3");
  ev("sgx:spike", "4");
  assert.ok(msgs().includes("sgx.spike.busy"));
  await advance(3);
  ev("sgx:stop");
  await advance(15);
});

test("sgx:play blackhole: espera a área carregar, roda o animatic inteiro e restaura tudo", async () => {
  game.log.messages = [];
  game.log.areas.length = 0;
  ev("sgx:play", "blackhole");
  assert.ok(!game.tags.has("cinematic_busy"), "ainda carregando a área");
  await advance(3);
  assert.ok(game.tags.has("cinematic_busy"));
  const add = game.log.areas.find((a) => a.op === "add" && a.id === "sgx_film");
  assert.ok(add, "abriu a ticking area do filme");
  // a área cobre a cratera (raio 45) e o disco (raio 42) em volta da mira
  assert.ok(add.to.x - add.from.x >= 2 * 45 && add.to.z - add.from.z >= 2 * 45);
  await advance(800);
  assert.ok(msgs().includes("sgx.msg.film_done"), msgs().join(" | "));
  assert.ok(!msgs().some((x) => x.startsWith("§c")), msgs().join(" | "));
  assert.ok(!game.tags.has("cinematic_busy"));
  const lastSet = game.log.camera.filter((c) => !c.clear).at(-1).tick;
  assert.ok(game.log.camera.some((c) => c.clear && c.tick >= lastSet + 3), "câmera solta depois do filme");
  // P-40: a área fica 60 s depois do fim e some
  assert.ok(game.areas.has("sgx_film"));
  await advance(1210);
  assert.ok(!game.areas.has("sgx_film"), "a área some 60 s depois do filme");
});

test("item → menu sem mira válida: usa 90 blocos à frente e avisa (não recusa)", async () => {
  game.log.messages = [];
  const orig = game.player.getBlockFromViewDirection;
  game.player.getBlockFromViewDirection = () => ({ block: { location: { x: 0, y: 63, z: 5 } } }); // perto demais
  game.formAnswer = { canceled: false, selection: 0 };
  game.emit("itemUse", { itemStack: { typeId: "singularity:core" }, source: game.player });
  await advance(4);
  game.player.getBlockFromViewDirection = orig;
  assert.ok(msgs().includes("sgx.msg.auto_target"), msgs().join(" | "));
  assert.ok(game.tags.has("cinematic_busy"));
  ev("sgx:stop");
  await advance(15);
});

test("item → menu → BURACO NEGRO começa o filme; sgx:stop para no meio", async () => {
  game.formAnswer = { canceled: false, selection: 0 };
  game.emit("itemUse", { itemStack: { typeId: "singularity:core" }, source: game.player });
  await advance(12);
  assert.ok(game.tags.has("cinematic_busy"));
  ev("sgx:stop");
  assert.ok(!game.tags.has("cinematic_busy"));
  assert.equal(game.rules.doMobSpawning, true);
});

test("crash no meio do filme: o estado volta no próximo spawn (P-44) e a área sobrando some (P-40)", async () => {
  game.props["sgx:restore"] = JSON.stringify({ time: 1234, daylight: true, mobs: true });
  game.rules.doMobSpawning = false;
  game.tags.add("cinematic_busy");
  game.emit("playerSpawn", { initialSpawn: true, player: game.player });
  await advance(25);
  assert.equal(game.timeOfDay, 1234);
  assert.equal(game.rules.doMobSpawning, true);
  assert.ok(!game.tags.has("cinematic_busy"));
});
