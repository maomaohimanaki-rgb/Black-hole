// v0.3.1 (F3, T-25): o buraco negro em geometria. Trava:
//  - o Molang gerado (escala/ringdown e a órbita de A/B) bate com o layout.js e o binary_math.js (chirp em sincronia);
//  - o script cria as entidades com tudo escrito no spawn (P-28), troca o bin só quando muda e limpa no fim;
//  - toda pose de câmera cai perto de um bin; o pacote fecha (ossos, texturas, materiais, propriedades P-29).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync, statSync } from "node:fs";
import { makeGame } from "./harness.mjs";
import { startFilm, stopFilm } from "../BP/scripts/singularity/engine/cutscene.js";
import { BLACKHOLE } from "../BP/scripts/singularity/blackhole/film.js";
import { ID, ID_SMALL, elevation, pickBin, binValue, mcYaw } from "../BP/scripts/singularity/blackhole/modules/bh.js";

const ROOT = new URL("../", import.meta.url);
const json = (p) => JSON.parse(readFileSync(new URL(p, ROOT), "utf8"));
const G = { x: 0.5, y: 64, z: 60.5 };
const LENS = BLACKHOLE.data.lens;

// Molang → JS (só o que o gerador usa): trig em graus, math.mod, q.property, variáveis v.*
function molang(lines, { props, lifeTime, frameAlpha = 0 }) {
  const v = {};
  const q = {
    property: (k) => props[k] ?? 0,
    life_time: lifeTime,
    frame_alpha: frameAlpha,
    rotation_to_camera: () => 0,
    body_y_rotation: 0,
  };
  const math = {
    sin: (d) => Math.sin((d * Math.PI) / 180), cos: (d) => Math.cos((d * Math.PI) / 180),
    pow: Math.pow, exp: Math.exp, abs: Math.abs, max: Math.max, min: Math.min, floor: Math.floor,
    mod: (a, b) => a - b * Math.floor(a / b), clamp: (x, a, b) => Math.min(b, Math.max(a, x)),
  };
  const src = lines.join("\n").replace(/\bq\.(life_time|frame_alpha|body_y_rotation)\b/g, "q.$1");
  new Function("v", "q", "math", src)(v, q, math);
  return v;
}

const client = (id) => json(`RP/entity/${id}.entity.json`)["minecraft:client_entity"].description;

function run({ from = 0 } = {}) {
  const game = makeGame();
  const layout = BLACKHOLE.layout(game.player.location, G);
  const r = startFilm({ system: game.system, world: game.world, mc: game.mc, player: game.player, now: game.now,
    layout, data: BLACKHOLE.data, modules: BLACKHOLE.modules, options: { from, cal: 2 } });
  assert.ok(!r.error, r.error);
  return { game, layout };
}

test("bh: elevação com sinal, bin mais perto com histerese, valor ±(j+1)", () => {
  const c = { x: 0, y: 0, z: 0 };
  assert.equal(Math.round(elevation({ x: 10, y: 10, z: 0 }, c)), 45);
  assert.equal(Math.round(elevation({ x: 0, y: -10, z: 10 }, c)), -45);
  const bins = LENS.bins;
  const j = pickBin(bins, 7.5);
  assert.equal(bins[j], 7.5);
  assert.equal(bins[pickBin(bins, -14.2)], 14);
  assert.equal(pickBin(bins, 8.4, j), j, "histerese segura o bin perto da borda");
  assert.equal(binValue(0, -3), -1);
  assert.equal(binValue(4, 3), 5);
  assert.equal(Math.round(mcYaw({ x: 0, z: 1 })) + 0, 0);
  assert.equal(Math.round(mcYaw({ x: -1, z: 0 })), 90);
});

const layoutOnly = () => BLACKHOLE.layout(makeGame().player.location, G);

test("bh: Molang da escala = layout.scaleAt (curva + ringdown), liso entre ticks", () => {
  const layout = layoutOnly();
  const pre = client("sgx_bh").scripts.pre_animation;
  const rs = json("spec/layout.json").black_hole.r_s_final;
  for (let t = 236; t <= 702; t += 1.25) {
    const v = molang(pre, { props: { "singularity:t0": 0 }, lifeTime: Math.floor(t) / 20, frameAlpha: t - Math.floor(t) });
    const want = layout.scaleAt(t) * rs;
    assert.ok(Math.abs(v.sc - want) < 1e-6 + 1e-6 * want, `t=${t}: ${v.sc} ≠ ${want}`);
  }
  // visível 240–699, disco apagado a partir do 620
  const at = (t) => molang(pre, { props: { "singularity:t0": 0 }, lifeTime: t / 20 });
  assert.ok(!at(239).on && at(240).on && at(699).on && !at(700).on);
  assert.ok(!at(619).disk_off && at(620).disk_off);
});

test("bh: Molang da órbita de A e B = layout.binary (mesma fase do chirp)", () => {
  const layout = layoutOnly();
  const pre = client("sgx_bh_small").scripts.pre_animation;
  const fyaw = mcYaw(layout.F);
  for (let t = 20; t < 240; t += 7) {
    const b = layout.binary(t);
    for (const [side, P] of [[1, b.A], [2, b.B]]) {
      const v = molang(pre, { props: { "singularity:t0": 0, "singularity:side": side, "singularity:fyaw": fyaw }, lifeTime: t / 20 });
      assert.ok(Math.abs(v.wx - (P.x - layout.O.x)) < 1e-4 && Math.abs(v.wz - (P.z - layout.O.z)) < 1e-4,
        `t=${t} lado ${side}: (${v.wx.toFixed(3)}, ${v.wz.toFixed(3)}) ≠ (${(P.x - layout.O.x).toFixed(3)}, ${(P.z - layout.O.z).toFixed(3)})`);
    }
  }
});

test("bh: o filme cria as 3 entidades em O com tudo no spawn, troca o bin só quando muda e limpa", () => {
  const { game, layout } = run();
  game.run(30);
  const ents = game.log.entities.filter((e) => e.typeId === ID || e.typeId === ID_SMALL);
  assert.equal(ents.length, 3);
  for (const e of ents) {
    assert.deepEqual(e.location, layout.O);
    for (const k of ["t0", "cal", "bin"]) assert.ok(`singularity:${k}` in e.props, `${e.typeId} sem ${k}`);
    assert.equal(e.props["singularity:cal"], 2);
    assert.notEqual(e.props["singularity:bin"], 0);
  }
  const small = ents.filter((e) => e.typeId === ID_SMALL);
  assert.deepEqual(small.map((e) => e.props["singularity:side"]).sort(), [1, 2]);
  // conta as trocas de bin do buraco final durante o filme
  const main = ents.find((e) => e.typeId === ID);
  let sets = 0;
  const orig = main.setProperty.bind(main);
  main.setProperty = (k, v) => ((sets += 1), orig(k, v));
  game.run(260);
  assert.ok(small.every((e) => !e.isValid), "A e B somem depois da fusão");
  assert.ok(main.isValid);
  game.run(520);
  assert.ok(!main.isValid, "o buraco final some no fim");
  assert.ok(sets < 120, `${sets} trocas de bin (só quando muda)`);
});

test("bh: sgx:from no meio cria só o buraco final; stop remove tudo", () => {
  const { game } = run({ from: 300 });
  game.run(3);
  const ents = game.log.entities.filter((e) => e.typeId === ID || e.typeId === ID_SMALL);
  assert.deepEqual(ents.map((e) => e.typeId), [ID]);
  assert.equal(ents[0].props["singularity:t0"], 15);
  stopFilm("stop");
  assert.ok(!ents[0].isValid);
});

test("bh: toda pose de câmera de 240 a 699 fica a ≤ 3,5° de um bin", () => {
  const { game, layout } = run();
  game.run(760);
  for (const c of game.log.camera) {
    if (c.clear || !c.location || c.tick < 240 || c.tick > 699) continue;
    const e = Math.abs(elevation(c.location, layout.O));
    const d = Math.min(...LENS.bins.map((b) => Math.abs(b - e)));
    assert.ok(d <= 3.5, `tick ${c.tick}: elevação ${e.toFixed(1)}° a ${d.toFixed(1)}° do bin mais perto`);
  }
});

test("bh: pacote fecha (geometrias, ossos do part_visibility, texturas, materiais, propriedades)", () => {
  let bytes = 0;
  for (const id of ["sgx_bh", "sgx_bh_small"]) {
    const d = client(id);
    for (const t of Object.values(d.textures)) assert.ok(existsSync(new URL(`RP/${t}.png`, ROOT)), t);
    assert.deepEqual(Object.values(d.materials).sort(), ["charged_creeper", "charged_creeper", "entity_alphatest"]);
    const geos = {};
    for (const [key, ident] of Object.entries(d.geometry)) {
      const kind = id === "sgx_bh" ? "bh" : "bhs";
      const file = new URL(`RP/models/entity/sgx_${kind}_${key}.geo.json`, ROOT);
      bytes += statSync(file).size;
      const g = JSON.parse(readFileSync(file, "utf8"))["minecraft:geometry"][0];
      assert.equal(g.description.identifier, ident);
      geos[`Geometry.${key}`] = new Set(g.bones.map((b) => b.name));
      for (const b of g.bones) if (b.poly_mesh) assert.ok(b.poly_mesh.polys.length > 0 && b.poly_mesh.normalized_uvs, b.name);
    }
    const rcs = json(`RP/render_controllers/${id}.render_controllers.json`).render_controllers;
    assert.deepEqual(d.render_controllers, Object.keys(rcs));
    assert.match(d.render_controllers[0], /_core$/, "a sombra (core) primeiro");
    for (const [name, rc] of Object.entries(rcs)) {
      const bones = geos[rc.geometry];
      assert.ok(bones, `${name}: ${rc.geometry}`);
      for (const pv of rc.part_visibility) for (const b of Object.keys(pv)) assert.ok(bones.has(b), `${name}: osso ${b}`);
      if (/flow\d$/.test(name)) assert.ok(rc.uv_anim && /v\.t\b/.test(rc.uv_anim.offset[0]), `${name}: uv_anim`);
    }
    // P-29: faixas float com literal float; P-28: client_sync
    const bpText = readFileSync(new URL(`BP/entities/${id}.json`, ROOT), "utf8");
    const props = JSON.parse(bpText)["minecraft:entity"].description.properties;
    for (const [k, p] of Object.entries(props)) {
      assert.equal(p.client_sync, true, k);
      if (p.type === "float") assert.match(bpText, new RegExp(`"${k}":\\{"type":"float","range":\\[-?\\d+\\.\\d+,-?\\d+\\.\\d+\\]`), k);
    }
  }
  assert.ok(bytes < 7e6, `geometria ${(bytes / 1e6).toFixed(1)} MB`);
  // cada bin tem sombra e anel; cada anel do disco tem malha em todo bin
  const core = json("RP/models/entity/sgx_bh_core.geo.json")["minecraft:geometry"][0].bones.map((b) => b.name);
  for (let j = 0; j < LENS.bins.length; j++) for (const p of ["s", "p"]) assert.ok(core.includes(`${p}${j}`), `${p}${j}`);
  for (let k = 0; k < 5; k++) {
    const f = json(`RP/models/entity/sgx_bh_flow${k}.geo.json`)["minecraft:geometry"][0].bones.map((b) => b.name);
    for (let j = 0; j < LENS.bins.length; j++) assert.ok(f.includes(`f${j}_${k}`), `f${j}_${k}`);
  }
});
