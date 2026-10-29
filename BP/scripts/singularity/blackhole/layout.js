// Geometria de cena do buraco negro (spec/layout.json → frame). G = chão mirado, O = G + oHeight·U.
// v0.2.4: escala B (T-18): os tamanhos vêm de DATA.scene (spec/layout.json), nada fixo aqui.
// F = frente (jogador → G, horizontal), R = F × U (direita), U = cima.
// Também resolve os keyframes de câmera do storyboard_data.js para coordenadas do mundo.

import { v3, add, sub, mul, norm, cross, madd, len } from "../engine/vec.js";
import { sampleCurve } from "../engine/easing.js";
import { offsets } from "./binary_math.js";

export function makeLayout(playerPos, targetG, data) {
  const { oHeight: O_HEIGHT, shadowF: SHADOW_FINAL, k: K } = data.scene;
  const U = v3(0, 1, 0);
  let fwd = sub(targetG, playerPos);
  fwd.y = 0;
  const F = norm(len(fwd) < 1e-3 ? v3(0, 0, 1) : fwd);
  const R = cross(F, U);
  const G = { ...targetG };
  const O = madd(G, [U, O_HEIGHT]);
  const toWorld = (base, f = 0, r = 0, u = 0) => madd(base, [F, f], [R, r], [U, u]);

  // Escala do buraco negro final (scale_curve + ringdown).
  const scaleAt = (t) => {
    if (t < 240) return 0;
    let s = sampleCurve(data.scaleCurve, "s", t);
    if (t >= 241 && t <= 279) {
      const x = t - 241;
      s *= 1 + 0.15 * Math.exp(-x / 10) * Math.sin((2 * Math.PI * x) / 12);
    }
    return s;
  };

  const binary = (t) => {
    const o = offsets(t);
    return {
      A: toWorld(O, o.A.f, o.A.r, 0),
      B: toWorld(O, o.B.f, o.B.r, 0),
      d: o.d,
      phi: o.phi,
    };
  };

  // Pedaço-herói (B15–B16): espiral de G + 12R + 0,5U até cruzar o plano do disco no 500,
  // depois mergulho radial até a sombra no 539.
  const heroChunk = (t) => {
    const a0 = Math.PI / 2; // começa no +R
    if (t <= 500) {
      const u = Math.min(1, Math.max(0, (t - 460) / 40));
      const r = K * (12 - 5 * u * u);
      const ang = a0 + 1.6 * Math.PI * u * u;
      const y = 0.5 + (O_HEIGHT - 0.5) * (u * u * (3 - 2 * u));
      return toWorld(G, -Math.cos(ang) * r, Math.sin(ang) * r, y);
    }
    const u = Math.min(1, (t - 500) / 39);
    const ang = a0 + 1.6 * Math.PI + 0.5 * Math.PI * u;
    const r = 7 * K - (7 * K - SHADOW_FINAL * 1.35) * u * u;
    return toWorld(O, -Math.cos(ang) * r, Math.sin(ang) * r, 0);
  };

  // Direção do mergulho final: de O para o pedaço-herói no 539.
  const diveDir = norm(sub(heroChunk(539), O));

  const named = {
    G: () => G,
    O: () => O,
    A: (t) => binary(t).A,
    B: (t) => binary(t).B,
    hero_chunk: (t) => heroChunk(t),
  };

  // {rel, f, r, u} · {around, r, az, el} · {follow, back, up} · {along, dist_to_shadow}
  function resolvePos(p) {
    if (p.rel) {
      const base = named[p.rel];
      if (!base) throw new Error(`rel desconhecido: ${p.rel}`);
      return (t) => toWorld(base(t), p.f ?? 0, p.r ?? 0, p.u ?? 0);
    }
    if (p.around) {
      const base = named[p.around];
      const az = (p.az * Math.PI) / 180, el = (p.el * Math.PI) / 180;
      // az 0 = do lado do jogador (O − r·F), cresce para +R; el = elevação.
      const h = madd(v3(), [F, -Math.cos(az)], [R, Math.sin(az)]);
      return (t) => madd(base(t), [h, p.r * Math.cos(el)], [U, p.r * Math.sin(el)]);
    }
    if (p.follow) {
      const base = named[p.follow];
      return (t) => {
        const H = base(t);
        let away = sub(H, O);
        away.y = 0;
        away = norm(away);
        return madd(H, [away, p.back ?? 0], [U, p.up ?? 0]);
      };
    }
    if (p.along) {
      return (t) => madd(O, [diveDir, SHADOW_FINAL * Math.max(scaleAt(t), 0.05) + p.dist_to_shadow]);
    }
    throw new Error(`pos de câmera desconhecida: ${JSON.stringify(p)}`);
  }

  function resolveLook(l) {
    if (typeof l === "string") {
      const base = named[l];
      if (!base) throw new Error(`look desconhecido: ${l}`);
      return { l: base };
    }
    if (l.rel) return { l: resolvePos(l) };
    if (l.pitch != null) return { lookRel: l };
    throw new Error(`look desconhecido: ${JSON.stringify(l)}`);
  }

  // Keyframes do storyboard → keyframes da CameraTrack.
  function cameraKeys() {
    const keys = [];
    for (const b of data.blocks) {
      for (const k of b.camera) {
        const p = resolvePos(k.pos);
        const lk = resolveLook(k.look);
        const key = { t: k.t, p, fov: k.fov, ease: k.ease, cut: !!k.cut, block: b.id };
        if (k.stutter) key.stutter = k.stutter;
        if (k.handheld) key.handheld = k.handheld;
        if (lk.l) key.l = lk.l;
        else {
          // yaw_rel 0 = olhando horizontalmente para O. pitch negativo = para cima.
          key.l = (t) => {
            const P = p(t);
            let h = sub(O, P);
            h.y = 0;
            h = norm(h);
            const yr = (lk.lookRel.yaw_rel * Math.PI) / 180, pr = (lk.lookRel.pitch * Math.PI) / 180;
            const side = cross(h, U);
            const dirH = madd(v3(), [h, Math.cos(yr)], [side, Math.sin(yr)]);
            return madd(P, [dirH, 16 * Math.cos(pr)], [U, -16 * Math.sin(pr)]);
          };
        }
        keys.push(key);
      }
    }
    return keys;
  }

  return { G, O, F, R, U, K, toWorld, scaleAt, binary, heroChunk, named, resolvePos, cameraKeys };
}
