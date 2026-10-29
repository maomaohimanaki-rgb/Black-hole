// Harness do Node: um "jogo" falso que conta chamadas nativas (P-01) e simula ticks, servidor
// atrasado e pausas. O motor não importa @minecraft/server, então roda aqui sem nada do jogo.

export class MolangVariableMap {
  constructor() {
    this.vars = {};
  }
  setVector3(k, v) {
    this.vars[k] = v;
  }
  setFloat(k, v) {
    this.vars[k] = v;
  }
}

export const mc = {
  MolangVariableMap,
  EasingType: { Linear: "Linear" },
  HudVisibility: { Hide: 0, Reset: 1 },
  HudElement: { PaperDoll: 0, Armor: 1, ToolTips: 2, TouchControls: 3, Crosshair: 4, Hotbar: 5, Health: 6, ProgressBar: 7, Hunger: 8, AirBubbles: 9, HorseHealth: 10, StatusEffects: 11, ItemText: 12 },
  InputPermissionCategory: { Camera: 1, Movement: 2, LateralMovement: 4, Sneak: 5, Jump: 6 },
};

export function makeGame({ msPerTick = 50 } = {}) {
  const log = { particles: [], camera: [], fov: [], titles: [], actionbar: [], sounds: [], commands: [], perTick: [] };
  let clockMs = 1_000_000;
  let tick = 0;
  const intervals = new Map();
  let nextId = 1;
  const props = {};
  const tags = new Set();
  const rules = { doDayLightCycle: true, doMobSpawning: true };
  let timeOfDay = 6000;

  log.entities = [];
  const dimension = {
    id: "minecraft:overworld",
    heightRange: { min: -64, max: 320 },
    spawnParticle(id, pos, m) {
      log.particles.push({ tick, id, pos, vars: m?.vars });
    },
    getTopmostBlock: ({ x, z }) => ({ location: { x, y: 63, z } }),
    getEntities: ({ type } = {}) => log.entities.filter((e) => e.isValid && (!type || e.typeId === type)),
    spawnEntity(typeId, location) {
      const e = {
        typeId, location: { ...location }, isValid: true, props: {}, impulses: 0,
        setProperty(k, v) {
          this.props[k] = v;
        },
        remove() {
          this.isValid = false;
        },
        applyImpulse() {
          this.impulses++;
        },
      };
      log.entities.push(e);
      return e;
    },
  };
  const player = {
    id: "p1",
    typeId: "minecraft:player",
    location: { x: 0, y: 64, z: 0 },
    dimension,
    camera: {
      setCamera(preset, o) {
        log.camera.push({ tick, preset, ...o });
      },
      setFov(o) {
        // Como o jogo: FOV fora de 30–110 lança erro (visto no aparelho na v0.1.0, ticks 535+).
        if (o?.fov != null && (o.fov < 30 || o.fov > 110)) throw new Error(`fov ${o.fov} fora de 30–110`);
        log.fov.push({ tick, ...o });
      },
      clear() {
        log.camera.push({ tick, clear: true });
      },
    },
    onScreenDisplay: {
      setTitle(text, o) {
        log.titles.push({ tick, text, o });
      },
      clearTitle() {},
      setActionBar(x) {
        log.actionbar.push({ tick, x });
      },
      setHudVisibility(v, els) {
        log.hud = { v, els };
      },
    },
    inputPermissions: { setPermissionCategory(c, on) {} },
    playSound(id, o) {
      log.sounds.push({ tick, id, o });
    },
    runCommand(c) {
      log.commands.push({ tick, c });
    },
    sendMessage(m) {
      (log.messages ??= []).push({ tick, m });
    },
    getViewDirection: () => ({ x: 0, y: -0.2, z: 0.98 }),
    getBlockFromViewDirection: () => ({ block: { location: { x: 0, y: 63, z: 60 } } }),
    hasTag: (t) => tags.has(t),
    addTag: (t) => tags.add(t),
    removeTag: (t) => tags.delete(t),
    getDynamicProperty: (k) => props[k],
    setDynamicProperty: (k, v) => {
      if (v === undefined) delete props[k];
      else props[k] = v;
    },
  };
  const subs = (name) => ({ subscribe: (fn) => ((handlers[name] ??= []).push(fn), fn) });
  const handlers = {};
  // Ticking areas (P-40): a promessa resolve no próximo tick, como o jogo carregando os chunks.
  const areas = new Map();
  log.areas = [];
  const tickingAreaManager = {
    maxChunkCount: 100,
    get chunkCount() {
      return areas.size * 64;
    },
    hasCapacity: () => true,
    hasTickingArea: (id) => areas.has(id),
    getTickingArea: (id) => areas.get(id),
    getAllTickingAreas: () => [...areas.values()],
    createTickingArea(id, o) {
      if (areas.has(id)) return Promise.reject(new Error("IdentifierAlreadyExists"));
      areas.set(id, { identifier: id, ...o });
      log.areas.push({ tick, op: "add", id, from: o.from, to: o.to });
      return new Promise((res) => timeouts.push({ at: tick + 1, fn: res }));
    },
    removeTickingArea(id) {
      areas.delete(id);
      log.areas.push({ tick, op: "remove", id });
    },
    removeAllTickingAreas() {
      areas.clear();
      log.areas.push({ tick, op: "removeAll" });
    },
  };
  const world = {
    tickingAreaManager,
    afterEvents: { itemUse: subs("itemUse"), playerSpawn: subs("playerSpawn") },
    gameRules: rules,
    getTimeOfDay: () => timeOfDay,
    setTimeOfDay: (t) => (timeOfDay = t),
    getPlayers: () => [player],
    getDimension: () => dimension,
    getDynamicProperty: (k) => worldProps[k],
    setDynamicProperty: (k, v) => {
      if (v === undefined) delete worldProps[k];
      else worldProps[k] = v;
    },
  };
  const worldProps = {};
  const timeouts = [];
  const system = {
    afterEvents: { scriptEventReceive: subs("scriptEventReceive") },
    run(fn) {
      timeouts.push({ at: tick + 1, fn });
    },
    runTimeout(fn, n = 1) {
      timeouts.push({ at: tick + n, fn });
    },
    runInterval(fn, every = 1) {
      const id = nextId++;
      intervals.set(id, fn);
      return id;
    },
    clearRun(id) {
      intervals.delete(id);
    },
  };

  // Avança n ticks do servidor; msPerTick > 50 simula servidor lento.
  function run(n, { ms = msPerTick } = {}) {
    for (let i = 0; i < n && (intervals.size || timeouts.length); i++) {
      tick++;
      clockMs += ms;
      for (const fn of [...intervals.values()]) fn();
      for (const x of timeouts.filter((x) => x.at <= tick)) {
        timeouts.splice(timeouts.indexOf(x), 1);
        x.fn();
      }
    }
  }
  const emit = (name, ev) => (handlers[name] ?? []).forEach((fn) => fn(ev));

  return {
    mc, world, system, player, dimension, log, run, emit,
    now: () => clockMs,
    advanceMs: (ms) => (clockMs += ms),
    get tick() {
      return tick;
    },
    get timeOfDay() {
      return timeOfDay;
    },
    rules, tags, props, areas,
    intervals,
  };
}
