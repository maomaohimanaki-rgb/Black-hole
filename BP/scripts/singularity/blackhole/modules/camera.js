// Câmera do filme: CameraTrack dos 58 keyframes do storyboard + tremor.
// v0.1.0: o tremor é feito NA POSE (rotação + posição), não com camera.addShake: o addShake mexe
// na câmera do jogador e não se sabe se vale na câmera livre da cutscene.

import { CameraTrack, CameraDriver } from "../../engine/camera_engine.js";

// Nível de tremor 1–10 → amplitude em graus (rotação) e blocos (posição), decaindo em DECAY ticks.
const DECAY = 8;
export function shakeAt(events, t) {
  let amp = 0;
  for (const e of events) {
    if (e.t > t) break;
    const age = t - e.t;
    if (age < DECAY) amp = Math.max(amp, e.level * (1 - age / DECAY));
  }
  return amp;
}

export default {
  name: "camera",
  setup(ctx) {
    const track = new CameraTrack(ctx.layout.cameraKeys());
    const driver = new CameraDriver({ camera: ctx.player.camera, easeType: ctx.mc.EasingType.Linear });
    const shakes = ctx.data.blocks.flatMap((b) => b.shake).sort((a, b) => a.t - b.t);
    ctx.cameraTrack = track;

    ctx.hook("pose", (t) => {
      const pose = track.sample(Math.min(t, ctx.data.meta.filmTicks - 1));
      const a = shakeAt(shakes, t);
      if (a > 0) {
        pose.rot.pitch += a * 0.12 * Math.sin(t * 2.3);
        pose.rot.yaw += a * 0.12 * Math.sin(t * 3.1 + 1);
        pose.p = { x: pose.p.x + a * 0.015 * Math.sin(t * 2.9), y: pose.p.y + a * 0.015 * Math.sin(t * 3.7), z: pose.p.z };
      }
      ctx.pose = pose;
      driver.apply(pose);
    }, { win: [0, ctx.data.meta.filmTicks + ctx.data.meta.outroTicks] });

    ctx.onTeardown(() => {
      try {
        ctx.player.camera.clear();
      } catch {}
      ctx.cameraPackets = driver.packets;
    });
  },
};
