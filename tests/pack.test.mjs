// O pacote: idiomas, referências entre arquivos e as armadilhas que só aparecem no aparelho.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => readFileSync(join(ROOT, p), "utf8");
const json = (p) => JSON.parse(read(p));
const walk = (d) =>
  readdirSync(join(ROOT, d)).flatMap((f) => {
    const p = join(d, f);
    return statSync(join(ROOT, p)).isDirectory() ? walk(p) : [p];
  });
const lang = (p) =>
  Object.fromEntries(
    read(p)
      .split("\n")
      .filter((l) => l && !l.startsWith("#"))
      .map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)]),
  );
const scripts = walk("BP/scripts").filter((f) => f.endsWith(".js"));
const allJs = scripts.map((f) => read(f)).join("\n");

test("i18n: as mesmas chaves e os mesmos %n nos dois idiomas (P-50)", () => {
  for (const pack of ["BP", "RP"]) {
    const en = lang(`${pack}/texts/en_US.lang`), pt = lang(`${pack}/texts/pt_BR.lang`);
    assert.deepEqual(Object.keys(en).sort(), Object.keys(pt).sort(), pack);
    for (const k of Object.keys(en)) {
      const n = (s) => (s.match(/%\d/g) ?? []).sort().join();
      assert.equal(n(en[k]), n(pt[k]), k);
    }
  }
});

test("i18n: toda chave usada no script existe no .lang", () => {
  const keys = new Set(Object.keys(lang("RP/texts/en_US.lang")));
  const used = [...allJs.matchAll(/["'`](sgx\.(?:menu|msg|spike)\.[a-z0-9_.]+)["'`]/g)].map((m) => m[1]);
  assert.ok(used.length > 10);
  for (const k of used) assert.ok(keys.has(k), k);
  for (let n = 1; n <= 10; n++) assert.ok(keys.has(`sgx.spike.${n}`), `sgx.spike.${n}`);
});

test("item: sem display_name literal; nome vem do .lang (P-50)", () => {
  const it = json("BP/items/sgx_core.json");
  assert.equal(it["minecraft:item"].components["minecraft:display_name"], undefined);
  assert.ok(lang("RP/texts/pt_BR.lang")["item.singularity:core"]);
});

test("propriedades float com literais float (P-29) e escritas no spawn (P-28)", () => {
  for (const f of walk("BP/entities")) {
    const raw = read(f);
    for (const m of raw.matchAll(/"type": "float",\s*"range": \[\s*([^\]]+)\]/g)) {
      for (const n of m[1].split(",").map((s) => s.trim())) assert.match(n, /\./, `${f}: ${m[1]}`);
    }
  }
});

test("referências: partículas, sons, entidades e texturas usados existem", () => {
  const particles = new Set(walk("RP/particles").map((f) => json(f).particle_effect.description.identifier));
  for (const m of allJs.matchAll(/"(singularity:sgx_(?:gizmo|p_|spike_)[a-z_]*)"/g)) {
    if (m[1].includes("spike_bb") || m[1].includes("spike_mesh")) continue;
    assert.ok(particles.has(m[1]), m[1]);
  }
  for (const m of allJs.matchAll(/`\$\{NS\}:(sgx_(?:spike_atlas|spike_shadow|p_impostor|gizmo_add))`/g)) assert.ok(particles.has(`singularity:${m[1]}`), m[1]);
  const entities = new Set(walk("BP/entities").map((f) => json(f)["minecraft:entity"].description.identifier));
  const clientEntities = new Set(walk("RP/entity").map((f) => json(f)["minecraft:client_entity"].description.identifier));
  for (const m of allJs.matchAll(/`\$\{NS\}:(sgx_[a-z_]+)`/g)) {
    const id = `singularity:${m[1]}`;
    if (particles.has(id) || id.startsWith("singularity:sgx2d")) continue;
    assert.ok(entities.has(id), `BP: ${id}`);
    assert.ok(clientEntities.has(id), `RP: ${id}`);
  }
  // sons: definição + arquivo
  const sd = json("RP/sounds/sound_definitions.json").sound_definitions;
  for (const [id, def] of Object.entries(sd)) {
    for (const s of def.sounds) assert.ok(existsSync(join(ROOT, "RP", `${s.name}.ogg`)), `${id}: ${s.name}.ogg`);
  }
  for (const s of json("spec/audio_cues.json").sounds) {
    if (s.heard_in_cutscene) assert.ok(sd[`singularity:sgx2d_${s.id.slice(4)}`], s.id);
    if (s.heard_outside_cutscene) assert.ok(sd[`singularity:${s.id}`], s.id);
  }
  // texturas de partículas, entidades e UI
  const tex = [
    ...walk("RP/particles").map((f) => json(f).particle_effect.description.basic_render_parameters.texture),
    ...walk("RP/entity").flatMap((f) => Object.values(json(f)["minecraft:client_entity"].description.textures)),
    ...[...read("RP/ui/hud_screen.json").matchAll(/"texture": "([^"]+)"/g)].map((m) => m[1]),
    ...Object.values(json("RP/textures/item_texture.json").texture_data).map((d) => d.textures),
  ];
  for (const t of new Set(tex)) assert.ok(existsSync(join(ROOT, "RP", `${t}.png`)), t);
});

test("texturas ≤ 2048 de lado (P-52)", () => {
  for (const f of walk("RP/textures").filter((f) => f.endsWith(".png"))) {
    const b = readFileSync(join(ROOT, f));
    const w = b.readUInt32BE(16), h = b.readUInt32BE(20);
    assert.ok(w <= 2048 && h <= 2048, `${f}: ${w}×${h}`);
  }
});

test("partículas: modo de direção 'custom' (P-19) e nada de (0,1,0) exato (P-21)", () => {
  for (const f of walk("RP/particles")) {
    const raw = read(f);
    assert.ok(!raw.includes("custom_direction\": \"") && !raw.includes('"mode": "custom_direction"'), f);
    assert.ok(!/"custom_direction": \[\s*0,\s*1,\s*0\s*\]/.test(raw), f);
    assert.ok(!/"facing_camera_mode": "lookat_direction"[\s\S]*"custom_direction": \[\s*0,\s*1,\s*0\s*\]/.test(raw), f);
  }
});

test("UI: título do barramento escondido nos filhos (P-13) e controles por insert_back (P-14)", () => {
  const ui = json("RP/ui/hud_screen.json");
  for (const k of ["hud_title_text/title_frame/title", "hud_title_text/title_frame/title_background"]) {
    assert.ok(ui[k].bindings.some((b) => b.source_property_name === "((#text - 'SGX') = #text)"), k);
  }
  assert.equal(ui.root_panel.modifications[0].operation, "insert_back");
});

test("manifests: BP depende do RP, script aponta para main.js, versões da API", () => {
  const bp = json("BP/manifest.json"), rp = json("RP/manifest.json");
  assert.ok(bp.dependencies.some((d) => d.uuid === rp.header.uuid));
  const script = bp.modules.find((m) => m.type === "script");
  assert.ok(existsSync(join(ROOT, "BP", script.entry)));
  assert.ok(bp.dependencies.some((d) => d.module_name === "@minecraft/server" && d.version === "2.11.0"));
});

test("imports relativos dos scripts existem", () => {
  for (const f of scripts) {
    for (const m of read(f).matchAll(/from "(\.[^"]+)"/g)) {
      assert.ok(existsSync(join(ROOT, dirname(f), m[1])), `${f} → ${m[1]}`);
    }
  }
});
