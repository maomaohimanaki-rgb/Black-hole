// Loader do Node: "@minecraft/server" e "@minecraft/server-ui" viram o jogo falso de globalThis.__sgxGame
// (tests/harness.mjs). Assim o main.js de verdade roda nos testes, com os scriptevents e os 10 spikes.
const STUBS = {
  "@minecraft/server": `const g = globalThis.__sgxGame;
export const world = g.world, system = g.system;
export const { MolangVariableMap, EasingType, HudVisibility, HudElement, InputPermissionCategory } = g.mc;`,
  "@minecraft/server-ui": `export class ActionFormData {
  title() { return this; } body() { return this; } button() { return this; }
  async show() { return globalThis.__sgxGame.formAnswer ?? { canceled: true }; }
}`,
};

export async function resolve(specifier, context, next) {
  if (specifier in STUBS) return { url: `sgx-stub:${specifier}`, shortCircuit: true };
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url.startsWith("sgx-stub:")) return { format: "module", source: STUBS[url.slice(9)], shortCircuit: true };
  return next(url, context);
}
