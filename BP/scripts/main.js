// Dooms Day: entrada do addon. Item singularity:core → menu (BURACO NEGRO · MAGNETAR · OPÇÕES),
// scriptevents sgx:* e restauração depois de crash (P-44).
// v0.1.0: o "buraco negro" é o ANIMATIC da F1 (caixas cinzas). Destruição entra na F6.

import * as mc from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { startFilm, stopFilm, activeFilm } from "./singularity/engine/cutscene.js";
import * as safety from "./singularity/engine/safety.js";
import { openStage, closeStage, cleanupStages } from "./singularity/engine/stage.js";
import { BLACKHOLE } from "./singularity/blackhole/film.js";
import { precache } from "./singularity/blackhole/modules/audio.js";
import { runSpike, stopSpike, spikeRunning } from "./singularity/spikes/index.js";
import { cleanupBlackHoles } from "./singularity/blackhole/modules/bh.js";

const { world, system } = mc;
const ITEM = "singularity:core";
// v0.2.4: escala B (T-18): cratera de raio 45 → mira a 60–160 (spec/project.json → targeting)
const MIN_DIST = 60;
const MAX_DIST = 160;
const opts = { trace: true };

const tr = (key, ...w) => ({ translate: key, with: w.map(String) });

// v0.3.1 (T-25): calibração da malha do buraco negro (bit 0: vira 180°; bit 1: sentido da textura ao girar a
// câmera; v0.3.3: bits 2 e 3 invertem os eixos x e z do deslocamento da âncora). Fica no mundo: o usuário acerta
// uma vez com o S-13 e esquece.
const getCal = () => {
  const v = Number(world.getDynamicProperty?.("sgx_cal") ?? 0);
  return Number.isFinite(v) ? Math.max(0, Math.min(15, Math.floor(v))) : 0;
};

// Mira: bloco olhado a 60–160 blocos. Sem mira válida, cai para o chão 90 blocos à frente.
function findTarget(player, { lenient = false } = {}) {
  const hit = player.getBlockFromViewDirection({ maxDistance: MAX_DIST + 8, includeLiquidBlocks: true });
  const P = player.location;
  if (hit) {
    const b = hit.block.location;
    const G = { x: b.x + 0.5, y: b.y + 1, z: b.z + 0.5 };
    const dist = Math.hypot(G.x - P.x, G.z - P.z);
    if (dist >= MIN_DIST && dist <= MAX_DIST) return { G };
    if (!lenient) return { error: dist < MIN_DIST ? "too_close" : "too_far" };
  } else if (!lenient) return { error: "no_target" };
  const auto = true;
  const d = player.getViewDirection();
  const h = Math.hypot(d.x, d.z) || 1;
  const x = P.x + (d.x / h) * 90, z = P.z + (d.z / h) * 90;
  const top = player.dimension.getTopmostBlock({ x: Math.floor(x), z: Math.floor(z) });
  return { auto, G: { x: Math.floor(x) + 0.5, y: (top ? top.location.y : Math.floor(P.y)) + 1, z: Math.floor(z) + 0.5 } };
}

let loading = false;

async function play(player, { from = 0, lenient = true } = {}) {
  if (loading || activeFilm() || spikeRunning() || player.hasTag(safety.BUSY_TAG)) {
    player.sendMessage(tr("sgx.msg.busy"));
    return;
  }
  const tg = findTarget(player, { lenient });
  // v0.1.1: mira fora de 40–128 não recusa mais; usa o chão 60 blocos à frente e avisa.
  if (tg.auto) player.sendMessage(tr("sgx.msg.auto_target"));
  if (tg.error) {
    const key = { too_close: "sgx.msg.too_close", too_far: "sgx.msg.too_far", no_target: "sgx.msg.no_target" }[tg.error];
    player.sendMessage(tr(key, tg.error === "too_far" ? MAX_DIST : MIN_DIST));
    return;
  }
  // v0.2.5: a cena fica além da distância de simulação (escala B): o filme só começa com a área carregada
  // e simulando (P-40). Sem a área (limite de chunks, API ausente), segue e avisa.
  loading = true;
  player.onScreenDisplay.setActionBar({ translate: "sgx.msg.loading" });
  const st = await openStage({ world, system, dimension: player.dimension, center: tg.G });
  loading = false;
  if (!st.ok) player.sendMessage(tr("sgx.msg.stage_warn", st.reason));
  const r = startFilm({
    system, world, mc, player,
    layout: BLACKHOLE.layout(player.location, tg.G),
    data: BLACKHOLE.data,
    modules: BLACKHOLE.modules,
    options: {
      from,
      trace: opts.trace,
      cal: getCal(),
      onEnd: (rep) => {
        closeStage({ world, system }); // 60 s depois do fim (P-40)
        player.sendMessage(tr("sgx.msg.film_done", rep.ticks, rep.skipped, rep.msAvg.toFixed(1), rep.msPeak.toFixed(0)));
        for (const e of [...rep.cueErrors, ...rep.hookErrors].slice(0, 5)) player.sendMessage(`§c[SGX] ${e.tag ?? e.hook ?? e.job} @${e.tick ?? e.t}: ${e.error.split("\n")[0]}`);
      },
    },
  });
  if (r.error) {
    closeStage({ world, system, delayTicks: 0 });
    player.sendMessage(tr("sgx.msg.busy"));
  }
}

async function openMenu(player) {
  precache(player);
  const form = new ActionFormData()
    .title(tr("sgx.menu.title"))
    .body(tr("sgx.menu.body"))
    .button({ rawtext: [{ translate: "sgx.menu.play" }, { text: "\n" }, { translate: "sgx.menu.play.sub" }] })
    .button({ rawtext: [{ translate: "sgx.menu.magnetar" }, { text: "\n" }, { translate: "sgx.menu.magnetar.sub" }] })
    .button({ rawtext: [{ translate: "sgx.menu.options" }, { text: "\n" }, { translate: "sgx.menu.options.sub" }] });
  const res = await form.show(player);
  if (res.canceled) return;
  if (res.selection === 0) await play(player);
  else if (res.selection === 1) player.sendMessage(tr("sgx.menu.soon"));
  else if (res.selection === 2) {
    await new ActionFormData().title(tr("sgx.menu.options")).body(tr("sgx.menu.options.body")).button(tr("sgx.menu.cancel")).show(player);
  }
}

world.afterEvents.itemUse.subscribe((ev) => {
  if (ev.itemStack?.typeId !== ITEM) return;
  const player = ev.source;
  system.run(() => openMenu(player).catch((e) => console.warn(`[SGX] menu: ${e}`)));
});

// /scriptevent sgx:play blackhole · sgx:from <t> · sgx:stop · sgx:spike <n> · sgx:trace on|off · sgx:cal <0–15>
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  const player = ev.sourceEntity;
  if (!player || player.typeId !== "minecraft:player") return;
  const msg = String(ev.message ?? "").trim();
  switch (ev.id) {
    case "sgx:play":
      if (msg === "" || msg === "blackhole") play(player, { lenient: true }).catch((e) => console.warn(`[SGX] play: ${e}`));
      else if (msg === "magnetar") player.sendMessage(tr("sgx.menu.soon"));
      break;
    case "sgx:from":
      play(player, { from: Number(msg) || 0, lenient: true }).catch((e) => console.warn(`[SGX] play: ${e}`));
      break;
    case "sgx:stop":
      if (stopFilm("stop") || stopSpike()) player.sendMessage(tr("sgx.msg.stopped"));
      else if (safety.restore({ world, player, mc, system })) player.sendMessage(tr("sgx.msg.restored"));
      break;
    case "sgx:spike":
      if (activeFilm()) player.sendMessage(tr("sgx.spike.busy"));
      else runSpike(Number(msg), { player, mc, system, world, cal: getCal() }).catch((e) => console.warn(`[SGX] spike: ${e}`));
      break;
    case "sgx:cal": {
      const n = Math.floor(Number(msg));
      if (msg !== "" && Number.isFinite(n) && n >= 0 && n <= 15) world.setDynamicProperty("sgx_cal", n);
      player.sendMessage(tr("sgx.msg.cal", getCal()));
      break;
    }
    case "sgx:trace":
      opts.trace = msg !== "off";
      player.sendMessage(`§8[SGX] trace ${opts.trace ? "on" : "off"}`);
      break;
  }
});

// P-40: área de um filme interrompido por crash. O gerenciador é deste addon, então limpar tudo é seguro.
system.runTimeout(() => {
  cleanupStages(world);
  // v0.3.1: entidades do buraco negro de um filme interrompido (crash, /reload)
  try {
    cleanupBlackHoles(world.getDimension("overworld"));
  } catch (e) {
    console.warn(`[SGX] limpeza: ${e}`);
  }
}, 20);

// P-44: se o jogo fechou no meio do filme, o estado original volta no primeiro spawn.
world.afterEvents.playerSpawn.subscribe((ev) => {
  if (!ev.initialSpawn) return;
  system.runTimeout(() => {
    if (safety.restore({ world, player: ev.player, mc, system })) ev.player.sendMessage(tr("sgx.msg.restored"));
  }, 20);
});
