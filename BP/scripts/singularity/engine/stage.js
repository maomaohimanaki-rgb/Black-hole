// Palco (ARCHITECTURE §4.8, P-40): uma ticking area em volta da cena SÓ durante o filme.
// v0.2.5: com a escala B (T-18) o centro do filme fica além da distância de simulação do jogador, e
// entidades/partículas de lá não aconteciam (visto pelo usuário no aparelho). O filme espera a área carregar
// (a promessa do createTickingArea resolve quando os chunks estão carregados E simulando) e a área some
// 60 s depois do fim. O gerenciador é do addon: "remover tudo" na carga do mundo limpa sobra de crash sem
// tocar em área de outro addon.

export const FILM_AREA = "sgx_film";
export const CLOSE_DELAY_TICKS = 1200; // 60 s (P-40)

const generations = new Map(); // id → quantas vezes foi aberta (um fechamento atrasado não derruba uma reabertura)

function box(dimension, c, radius, below, above) {
  const lo = dimension.heightRange?.min ?? -64;
  const hi = (dimension.heightRange?.max ?? 320) - 1;
  return {
    dimension,
    from: { x: Math.floor(c.x - radius), y: Math.max(lo, Math.floor(c.y - below)), z: Math.floor(c.z - radius) },
    to: { x: Math.floor(c.x + radius), y: Math.min(hi, Math.floor(c.y + above)), z: Math.floor(c.z + radius) },
  };
}

// Abre (ou reabre) a área e espera ela carregar, com prazo. Nunca lança: devolve {ok, reason}.
export async function openStage({ world, system, dimension, center, id = FILM_AREA, radius = 64, below = 48, above = 112, timeoutTicks = 200 }) {
  const m = world.tickingAreaManager;
  if (!m) return { ok: false, reason: "no_api" };
  generations.set(id, (generations.get(id) ?? 0) + 1);
  try {
    if (m.hasTickingArea(id)) m.removeTickingArea(id);
    const opts = box(dimension, center, radius, below, above);
    if (!m.hasCapacity(opts)) return { ok: false, reason: "capacity" };
    let timer;
    const timeout = new Promise((res) => {
      timer = system.runTimeout(() => res("timeout"), timeoutTicks);
    });
    const r = await Promise.race([m.createTickingArea(id, opts).then(() => "ok"), timeout]);
    if (r === "ok") system.clearRun?.(timer);
    return { ok: r === "ok", reason: r };
  } catch (e) {
    return { ok: false, reason: String(e?.reason ?? e) };
  }
}

// Fecha depois de delayTicks (0 = já). Se a área foi reaberta nesse meio-tempo, não fecha.
export function closeStage({ world, system, id = FILM_AREA, delayTicks = CLOSE_DELAY_TICKS }) {
  const gen = generations.get(id);
  const close = () => {
    if (generations.get(id) !== gen) return;
    try {
      const m = world.tickingAreaManager;
      if (m?.hasTickingArea(id)) m.removeTickingArea(id);
    } catch {}
  };
  if (delayTicks > 0) system.runTimeout(close, delayTicks);
  else close();
}

// Na carga do mundo: qualquer área deste addon que existir é sobra de um crash (P-40).
export function cleanupStages(world) {
  try {
    const m = world.tickingAreaManager;
    if (m && m.getAllTickingAreas().length) {
      m.removeAllTickingAreas();
      return true;
    }
  } catch {}
  return false;
}
