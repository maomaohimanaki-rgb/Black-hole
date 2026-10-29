// O evento 1: buraco negro. Junta layout + dados gerados + módulos (a câmera primeiro: os outros
// podem usar ctx.pose).

import { DATA } from "./storyboard_data.js";
import { makeLayout } from "./layout.js";
import camera from "./modules/camera.js";
import screen from "./modules/screen.js";
import hud from "./modules/hud.js";
import audio from "./modules/audio.js";
import gizmos from "./modules/gizmos.js";
import impostor from "./modules/impostor.js";

export const BLACKHOLE = {
  id: "blackhole",
  data: DATA,
  modules: [camera, screen, audio, hud, impostor, gizmos],
  layout: (playerPos, G) => makeLayout(playerPos, G, DATA),
};
