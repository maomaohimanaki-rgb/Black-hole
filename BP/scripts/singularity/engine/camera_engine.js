// Câmera "on ones" (ARCHITECTURE §4.3): 1 pose por tick, enviada com ease linear de 0,05 s (P-10).
// Keyframe já resolvido em mundo: {t, p, l | r:{pitch,yaw}, fov, ease, cut, stutter, handheld}.
// p e l podem ser vetores ou funções (t) => vetor (alvos que andam: pedaço-herói, B em órbita).
// O ease diz como se CHEGA no keyframe; fov herda do anterior.

import { ease, lerp } from "./easing.js";
import { add, mul, sub, lerpV, len, dirToRot, rotToDir } from "./vec.js";

export const FOV_MIN = 30;
export const FOV_MAX = 110;

const val = (x, t) => (typeof x === "function" ? x(t) : x);

export class CameraTrack {
  constructor(keys) {
    if (!keys.length) throw new Error("câmera sem keyframes");
    this.keys = [...keys].sort((a, b) => a.t - b.t);
    let fov = 70;
    for (const k of this.keys) {
      if (k.fov == null) k.fov = fov;
      fov = k.fov;
    }
  }

  // Segmento [k0, k1] que contém t.
  _segment(t) {
    const K = this.keys;
    if (t <= K[0].t) return [K[0], K[0]];
    for (let i = 1; i < K.length; i++) if (t <= K[i].t) return [K[i - 1], K[i]];
    const last = K[K.length - 1];
    return [last, last];
  }

  // Stutter: a pose só atualiza nos ticks t0 + h1, t0 + h1 + h2, … (o último h se repete).
  static stutterTick(t, t0, holds) {
    let q = t0, i = 0;
    for (;;) {
      const h = Math.max(1, holds[Math.min(i, holds.length - 1)]);
      if (q + h > t) return q;
      q += h;
      i++;
    }
  }

  _look(k, p, t) {
    if (k.l != null) return val(k.l, t);
    if (k.r) return add(p, mul(rotToDir(k.r), 16));
    throw new Error(`keyframe ${k.t} sem l nem r`);
  }

  // Pose no tick t: {p, rot:{pitch,yaw}, fov, cut, k1}.
  sample(t) {
    let [k0, k1] = this._segment(t);
    let ts = t;
    if (k1.stutter && k0 !== k1) ts = CameraTrack.stutterTick(t, k0.t, k1.stutter);
    const span = k1.t - k0.t;
    const u = span <= 0 ? 1 : ease(k1.ease ?? "linear", (ts - k0.t) / span);
    const p0 = val(k0.p, ts), p1 = val(k1.p, ts);
    const p = lerpV(p0, p1, u);
    const l = lerpV(this._look(k0, p0, ts), this._look(k1, p1, ts), u);
    let d = sub(l, p);
    if (len(d) < 1e-6) d = sub(this._look(k1, p1, ts), p0);
    const rot = dirToRot(d);
    const fov = lerp(k0.fov, k1.fov, u);
    if (k1.handheld && u > 0 && u < 1) {
      // Câmera na mão: ruído determinístico (soma de senos), em graus.
      const a = k1.handheld * 4;
      rot.pitch += a * (Math.sin(t * 0.71) * 0.6 + Math.sin(t * 1.93) * 0.4);
      rot.yaw += a * (Math.sin(t * 0.53 + 1) * 0.6 + Math.sin(t * 1.37) * 0.4);
    }
    // Corte: chegada seca no tick do keyframe com cut, ou cada passo do stutter.
    const cut = (k1.cut && t === k1.t) || (k1.stutter && ts === t && t !== k0.t) || false;
    return { p, rot, fov, cut, key: k1, ts };
  }
}

// Envia poses para o jogo com o mínimo de pacotes: câmera por tick, FOV só quando muda.
export class CameraDriver {
  constructor({ camera, easeType, easeTime = 0.05 }) {
    this.camera = camera; // Player.camera
    this.easeType = easeType; // EasingType.Linear (injetado: o motor não importa o jogo)
    this.easeTime = easeTime;
    this.last = null;
    this.lastFov = null;
    this.packets = 0;
  }

  apply(pose) {
    const same =
      this.last &&
      !pose.cut &&
      Math.abs(this.last.p.x - pose.p.x) < 1e-4 &&
      Math.abs(this.last.p.y - pose.p.y) < 1e-4 &&
      Math.abs(this.last.p.z - pose.p.z) < 1e-4 &&
      Math.abs(this.last.rot.pitch - pose.rot.pitch) < 1e-3 &&
      Math.abs(this.last.rot.yaw - pose.rot.yaw) < 1e-3;
    if (!same) {
      const opts = { location: pose.p, rotation: { x: pose.rot.pitch, y: pose.rot.yaw } };
      if (!pose.cut && this.last) opts.easeOptions = { easeTime: this.easeTime, easeType: this.easeType };
      this.camera.setCamera("minecraft:free", opts);
      this.packets++;
    }
    // v0.1.1: o jogo só aceita FOV de 30 a 110 (o B16–B18 pede 120 e o setFov lançava erro no 535+).
    const fov = Math.round(Math.min(FOV_MAX, Math.max(FOV_MIN, pose.fov)) * 4) / 4;
    if (fov !== this.lastFov) {
      const o = { fov };
      if (!pose.cut && this.lastFov != null) o.easeOptions = { easeTime: this.easeTime, easeType: this.easeType };
      this.camera.setFov(o);
      this.lastFov = fov;
      this.packets++;
    }
    this.last = pose;
  }
}
