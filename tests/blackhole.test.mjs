import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { DATA } from "../BP/scripts/singularity/blackhole/storyboard_data.js";
import { makeLayout } from "../BP/scripts/singularity/blackhole/layout.js";
import { halfOrbitTicks, separation, fGw } from "../BP/scripts/singularity/blackhole/binary_math.js";
import { CameraTrack } from "../BP/scripts/singularity/engine/camera_engine.js";
import { lbCode, buildFlashTrack } from "../BP/scripts/singularity/blackhole/modules/screen.js";
import { hudState } from "../BP/scripts/singularity/blackhole/modules/hud.js";
import { sampleCurve } from "../BP/scripts/singularity/engine/easing.js";
import { len, sub } from "../BP/scripts/singularity/engine/vec.js";

const spec = (f) => JSON.parse(readFileSync(new URL(`../spec/${f}`, import.meta.url), "utf8"));
const SB = spec("storyboard.json");
const LY = spec("layout.json");
const layout = makeLayout({ x: 0, y: 64, z: 0 }, { x: 0, y: 64, z: 60 }, DATA);

test("spec ↔ código: storyboard_data.js bate com spec/storyboard.json", () => {
  assert.equal(DATA.blocks.length, SB.blocks.length);
  assert.equal(DATA.meta.filmTicks, SB.meta.film_ticks);
  for (let i = 0; i < SB.blocks.length; i++) {
    assert.deepEqual(DATA.blocks[i].ticks, SB.blocks[i].ticks);
    assert.deepEqual(DATA.blocks[i].camera.map((k) => k.t), SB.blocks[i].camera.map((k) => k.t));
  }
});

test("órbita ↔ áudio: as 19 meias-órbitas da fórmula = spec/layout.json", () => {
  assert.deepEqual(halfOrbitTicks(), LY.binary.half_orbit_ticks);
  assert.ok(Math.abs(separation(60) - 8) < 1e-9);
  assert.ok(Math.abs(separation(239) - 2.18) < 0.01);
  assert.ok(Math.abs(fGw(60) - 35) < 1e-9);
});

test("layout: O = G + 14, frame ortonormal, R à direita de F", () => {
  assert.equal(layout.O.y - layout.G.y, 14);
  assert.deepEqual(layout.F, { x: 0, y: 0, z: 1 });
  assert.deepEqual(layout.R, { x: -1, y: 0, z: 0 }); // olhando para +Z, a direita é −X
  // A e B do lado oposto de O, com as massas certas
  const b = layout.binary(150);
  const dA = len(sub(b.A, layout.O)), dB = len(sub(b.B, layout.O));
  assert.ok(Math.abs(dA / dB - 29 / 36) < 1e-9);
});

test("câmera: todos os keyframes resolvem e a câmera não salta sem corte", () => {
  const tr = new CameraTrack(layout.cameraKeys());
  const cuts = new Set(layout.cameraKeys().filter((k) => k.cut).map((k) => k.t));
  let prev = tr.sample(0);
  for (let t = 1; t < DATA.meta.filmTicks; t++) {
    const s = tr.sample(t);
    for (const v of [s.p.x, s.p.y, s.p.z, s.rot.pitch, s.rot.yaw, s.fov]) assert.ok(Number.isFinite(v), `t=${t}`);
    const jump = len(sub(s.p, prev.p));
    // Sem corte, um tick anda no máximo ~8 blocos (a viagem mais rápida é a do B08/B15).
    if (!cuts.has(t) && !s.cut) assert.ok(jump < 8, `salto de ${jump.toFixed(1)} blocos no tick ${t}`);
    prev = s;
  }
});

test("câmera: mira a ≥ 40 blocos → o corpo do jogador fica fora da cratera (raio 30)", () => {
  const G = layout.G;
  const P = { x: 0, y: 64, z: 0 };
  assert.ok(Math.hypot(G.x - P.x, G.z - P.z) >= 40);
});

test("pedaço-herói: contínuo e chega perto da sombra no 539", () => {
  let prev = layout.heroChunk(460);
  for (let t = 461; t <= 539; t++) {
    const p = layout.heroChunk(t);
    assert.ok(len(sub(p, prev)) < 2, `t=${t}`);
    prev = p;
  }
  assert.ok(len(sub(layout.heroChunk(539), layout.O)) < 3);
});

test("letterbox: 16:9 no começo, fechado 600–619 (preto), aberto de novo no fim", () => {
  const code = (t) => lbCode(sampleCurve(DATA.letterbox, "vis", t));
  assert.equal(code(0), 1);
  for (let t = 600; t <= 619; t++) assert.equal(code(t), 99, `t=${t}`);
  assert.equal(code(719), 1);
  assert.equal(code(300), 26); // 2,39 → altura visível 0,418 da largura
});

test("continuidade: HUD nunca depois do 580 (só o título), nenhum som em 600–619", () => {
  const ev = DATA.blocks.flatMap((b) => b.hud).sort((a, b) => a.t - b.t);
  for (let t = 580; t < 720; t++) {
    const s = hudState(ev, t);
    for (const ch of Object.keys(s)) assert.ok(ch === "TT" || ch === "TT2", `${ch} no ${t}`);
  }
  for (const s of DATA.sounds) assert.ok(!(s.tick >= 600 && s.tick <= 619), s.id);
});

test("flashes: impacto negativo no 240 (2 ticks) e cores do catálogo", () => {
  const { fl, imp } = buildFlashTrack(DATA.blocks);
  assert.deepEqual(imp, [[240, 241]]);
  for (const f of fl) assert.ok(f.code >= 1 && f.code <= 79, String(f.code));
});
