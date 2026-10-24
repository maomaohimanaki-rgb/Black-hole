// F0 — esqueleto. Só registra o item e o /scriptevent sgx:spike <n>. O motor entra na F1 (docs/ROADMAP.md).
import { world, system } from "@minecraft/server";

const ITEM = "singularity:core";
world.afterEvents.itemUse.subscribe((ev) => {
  if (ev.itemStack?.typeId !== ITEM) return;
  system.run(() => ev.source.sendMessage({ translate: "sgx.menu.title" }));
});
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "sgx:spike") return;
  const n = Number(String(ev.message ?? "").trim());
  ev.sourceEntity?.sendMessage(`§8[SGX] spike ${n}: ainda não implementado (F0)`);
});
