// Segurança do filme (ARCHITECTURE §4.8): grava o estado original ANTES de mexer em qualquer coisa
// e restaura no fim, no abort e no próximo spawn depois de um crash (P-44).
//  - noite fixa na hora que deixa a Lua longe dos planos (P-42) e sem monstros (P-41);
//  - HUD do jogador escondido (título e actionbar ficam: são o nosso barramento);
//  - tag cinematic_busy (sinal entre addons, P-51) e jogador parado.

export const BUSY_TAG = "cinematic_busy";
const KEY = "sgx:restore";

// P-42: às 18000 a Lua fica no zênite. 14500 = Lua a leste, 21500 = a oeste: escolhe o lado
// oposto ao olhar (F) do jogador.
export const nightFor = (F) => (F.x > 0 ? 21500 : 14500);

export function hideList(mc) {
  const H = mc.HudElement;
  return [H.PaperDoll, H.Armor, H.ToolTips, H.TouchControls, H.Crosshair, H.Hotbar, H.Health, H.ProgressBar, H.Hunger, H.AirBubbles, H.HorseHealth, H.StatusEffects, H.ItemText].filter((x) => x != null);
}

export function engage({ world, player, mc, F, night = true }) {
  const state = {
    time: world.getTimeOfDay(),
    daylight: world.gameRules.doDayLightCycle,
    mobs: world.gameRules.doMobSpawning,
  };
  player.setDynamicProperty(KEY, JSON.stringify(state));
  player.addTag(BUSY_TAG);
  world.gameRules.doMobSpawning = false;
  if (night) {
    world.gameRules.doDayLightCycle = false;
    world.setTimeOfDay(nightFor(F));
  }
  try {
    player.onScreenDisplay.setHudVisibility(mc.HudVisibility.Hide, hideList(mc));
  } catch {}
  setInput(player, mc, false);
  return state;
}

function setInput(player, mc, on) {
  const C = mc.InputPermissionCategory;
  for (const c of [C?.Movement, C?.Camera, C?.Jump, C?.Sneak]) {
    if (c == null) continue;
    try {
      player.inputPermissions.setPermissionCategory(c, on);
    } catch {}
  }
}

// Idempotente: sem estado gravado, não faz nada.
export function restore({ world, player, mc }) {
  const raw = player.getDynamicProperty(KEY);
  if (typeof raw !== "string") {
    player.removeTag(BUSY_TAG);
    return false;
  }
  try {
    const s = JSON.parse(raw);
    world.gameRules.doDayLightCycle = !!s.daylight;
    world.gameRules.doMobSpawning = !!s.mobs;
    world.setTimeOfDay(s.time);
  } catch {}
  try {
    player.onScreenDisplay.setHudVisibility(mc.HudVisibility.Reset);
  } catch {}
  try {
    player.camera.clear();
    player.runCommand("camera @s fov_clear"); // o clear não garante o FOV de volta
  } catch {}
  setInput(player, mc, true);
  player.removeTag(BUSY_TAG);
  player.setDynamicProperty(KEY, undefined);
  return true;
}
