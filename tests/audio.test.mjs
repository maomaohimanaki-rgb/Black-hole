// O áudio de verdade (F2): o que foi sintetizado, analisado e gerado bate com o spec.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { SOUND_CUES, ONSETS, ENVELOPE } from "../BP/scripts/singularity/blackhole/timeline_data.js";
import { halfOrbitTicks } from "../BP/scripts/singularity/blackhole/binary_math.js";

const AU = JSON.parse(readFileSync(new URL("../spec/audio_cues.json", import.meta.url), "utf8"));

test("timeline: os sons e os ticks são os do spec", () => {
  assert.deepEqual(SOUND_CUES.map((c) => [c.sound, c.tick, c.end]), AU.sounds.map((s) => [s.id, s.tick, s.end_tick]));
  for (const c of SOUND_CUES) {
    assert.ok(existsSync(new URL(`../RP/sounds/singularity/${c.sound}.ogg`, import.meta.url)), c.sound);
    assert.ok(existsSync(new URL(`../RP/sounds/singularity/${c.sound}_m.ogg`, import.meta.url)), `${c.sound}_m`);
  }
});

test("ida e volta: todo onset pedido foi detectado no áudio a ±0,5 tick", () => {
  for (const s of AU.sounds) {
    if (!s.heard_in_cutscene) continue;
    for (const o of s.onsets_intended) {
      const hit = ONSETS.some((d) => d.sound === s.id && Math.abs(d.tick - o.tick) <= 0.5);
      assert.ok(hit, `${s.id} @${o.tick}`);
    }
  }
});

test("os acentos do chirp caem nas meias-órbitas da órbita visual", () => {
  const chirp = ONSETS.filter((o) => o.sound === "sgx_chirp");
  for (const t of halfOrbitTicks()) assert.ok(chirp.some((o) => Math.abs(o.tick - t) <= 0.5), `meia-órbita ${t}`);
});

test("silêncio absoluto 600–619: nenhum som de cutscene e envelope zerado", () => {
  for (let t = 600; t <= 619; t++) assert.equal(ENVELOPE[t], 0, `t=${t}`);
  for (const c of SOUND_CUES) if (c.mode !== "outside") assert.ok(c.end <= 600 || c.tick >= 620, c.sound);
});

test("quase-silêncio 268–279 (fim do ringdown)", () => {
  for (let t = 268; t <= 279; t++) assert.ok(ENVELOPE[t] < 0.05 * 0.9 + 1e-9, `t=${t}: ${ENVELOPE[t]}`);
});
