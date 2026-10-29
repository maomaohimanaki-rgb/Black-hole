// v0.3.0 (F3): o impostor do buraco negro. Trava: toda pose da câmera cai num quadro assado, o quadro certo em
// cada trecho do filme (A/B, sem disco, com disco), e o atlas/partícula batem com spec/bake.json.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { makeGame } from "./harness.mjs";
import { startFilm } from "../BP/scripts/singularity/engine/cutscene.js";
import { BLACKHOLE } from "../BP/scripts/singularity/blackhole/film.js";
import { inclination, pickCell } from "../BP/scripts/singularity/blackhole/modules/impostor.js";

const ROOT = new URL("../", import.meta.url);
const G = { x: 0.5, y: 64, z: 60.5 };
const CELLS = BLACKHOLE.data.impostor.cells;
const BAKE = JSON.parse(readFileSync(new URL("spec/bake.json", ROOT), "utf8")).impostor;

function run() {
  const game = makeGame();
  const layout = BLACKHOLE.layout(game.player.location, G);
  const r = startFilm({ system: game.system, world: game.world, mc: game.mc, player: game.player, now: game.now,
    layout, data: BLACKHOLE.data, modules: BLACKHOLE.modules, options: {} });
  assert.ok(!r.error, r.error);
  game.run(800);
  const bh = game.log.particles.filter((p) => p.id === "singularity:sgx_p_bh")
    .map((p) => ({ ...p, cell: p.vars["variable.incl"].x, s: p.vars["variable.s"].x, tint: p.vars["variable.c0"].x }));
  return { game, layout, bh };
}

test("impostor: inclinação com sinal (acima +, abaixo −, de lado 90)", () => {
  const c = { x: 0, y: 0, z: 0 };
  assert.equal(Math.round(inclination({ x: 10, y: 0, z: 0 }, c)), 90);
  assert.equal(Math.round(inclination({ x: 10, y: 10, z: 0 }, c)), 45);
  assert.equal(Math.round(inclination({ x: 10, y: -10, z: 0 }, c)), -45);
  assert.equal(Math.round(inclination({ x: 0, y: 10, z: 0.001 }, c)), 0);
});

test("impostor: pickCell só devolve quadro de disco, o mais perto, com histerese", () => {
  const i75 = pickCell(CELLS, 75);
  assert.equal(CELLS[i75].incl, 75);
  assert.equal(CELLS[pickCell(CELLS, -80)].incl, -82.5);
  for (let a = -90; a <= 90; a += 0.5) assert.equal(CELLS[pickCell(CELLS, a)].kind, "disk");
  // 78,9° fica mais perto do 82,5 por 0,3°: sem trocar (histerese de 1,5°)
  assert.equal(pickCell(CELLS, 78.9, i75), i75);
  assert.equal(CELLS[pickCell(CELLS, 81, i75)].incl, 82.5);
});

test("impostor: toda pose da câmera com disco (280–619) cai a ≤ 5,25° de um quadro assado", () => {
  const { game, layout } = run();
  for (const c of game.log.camera) {
    if (c.clear || !c.location || c.tick < 280 || c.tick > 619) continue;
    const inc = inclination(c.location, layout.O);
    const d = Math.min(...CELLS.filter((x) => x.kind === "disk").map((x) => Math.abs(x.incl - inc)));
    assert.ok(d <= 3.75 + 1.5, `tick ${c.tick}: inclinação ${inc.toFixed(1)}° a ${d.toFixed(1)}° do quadro mais perto`);
  }
});

test("impostor: quadro certo em cada trecho, tamanho pela sombra e entrada por tinta", () => {
  const { game, bh } = run();
  const kind = (p) => CELLS[p.cell].kind;
  assert.ok(bh.length > 200, `${bh.length} impostores`);
  for (const p of bh) {
    assert.ok(Number.isInteger(p.cell) && p.cell >= 0 && p.cell < CELLS.length, `quadro ${p.cell}`);
    if (p.tick < 240) assert.fail(`impostor grande no ${p.tick}`);
    else if (p.tick < 280 || p.tick > 619) assert.equal(kind(p), "bare", `tick ${p.tick}`);
    else assert.ok(kind(p) === "disk" || (kind(p) === "bare" && p.tick < 320), `tick ${p.tick}: ${kind(p)}`);
  }
  assert.ok(!bh.some((p) => p.tick > 699), "nada depois do 699");
  // A e B: atlas pequeno, de 20 a 239, e o quadro segue a câmera (o par é visto de baixo e de cima)
  const ab = game.log.particles.filter((p) => p.id === "singularity:sgx_p_bh_small");
  assert.ok(ab.length > 150 && ab.every((p) => p.tick >= 20 && p.tick <= 239), `${ab.length} A/B`);
  const sm = BLACKHOLE.data.impostor.small.cells;
  const incl = new Set(ab.map((p) => sm[p.vars["variable.incl"].x].incl));
  assert.ok([...incl].some((x) => x < 0) && [...incl].some((x) => x > 0), [...incl].join(" "));
  const disk = bh.filter((p) => kind(p) === "disk");
  assert.ok(disk[0].tint < 0.2, `entra escuro (${disk[0].tint})`);
  assert.equal(disk.at(-1).tint, 1);
  // 360: buraco em escala cheia; meia-largura = sombra × hw do quadro
  const at = disk.find((p) => p.tick >= 360 && p.tick <= 362);
  const { shadowF } = BLACKHOLE.data.scene;
  assert.ok(Math.abs(at.s - shadowF * CELLS[at.cell].hw) < shadowF * CELLS[at.cell].hw * 0.25, `meia-largura ${at.s}`);
  // as bolinhas pretas do animatic (A, B e o buraco final) saíram
  const black = game.log.particles.filter((p) => p.id === "singularity:sgx_gizmo" && p.vars["variable.c0"].x === 0 && p.vars["variable.c0"].y === 0);
  assert.equal(black.length, 0, `${black.length} gizmos pretos`);
});

test("impostor: atlas e partícula batem com spec/bake.json", () => {
  assert.equal(CELLS.length, BAKE.cells.length);
  assert.ok(CELLS.length <= BAKE.grid * BAKE.grid);
  assert.equal(BAKE.cell_px * BAKE.grid, 2048, "atlas 2048 (P-52)");
  const png = new URL("RP/textures/sgx/impostor/bh_atlas.png", ROOT);
  assert.ok(existsSync(png), "rode tools/build_all.py (o bake vem depois do gen_assets)");
  const b = readFileSync(png);
  assert.equal(b.readUInt32BE(16), 2048);
  assert.equal(b.readUInt32BE(20), 2048);
  const part = JSON.parse(readFileSync(new URL("RP/particles/sgx_p_bh.json", ROOT), "utf8")).particle_effect;
  assert.equal(part.description.basic_render_parameters.texture, "textures/sgx/impostor/bh_atlas");
  const bb = part.components["minecraft:particle_appearance_billboard"];
  assert.equal(bb.facing_camera_mode, "lookat_xyz");
  assert.deepEqual(bb.uv.uv_size, [BAKE.cell_px, BAKE.cell_px]);
  assert.deepEqual([...new Set(CELLS.map((c) => c.kind))].sort(), ["bare", "disk"]);
  const sp = readFileSync(new URL("RP/textures/sgx/impostor/bh_small.png", ROOT));
  assert.equal(sp.readUInt32BE(16), BAKE.small.cell_px * BAKE.small.grid);
  assert.equal(BLACKHOLE.data.impostor.small.cells.length, BAKE.small.cells.length);
});
