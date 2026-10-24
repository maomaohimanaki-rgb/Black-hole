#!/usr/bin/env python3
"""Áudio PROVISÓRIO da F1 (ROADMAP): um bipe por onset pedido em spec/audio_cues.json, para o tempo ser
ouvido desde o primeiro dia. Altura do bipe = intensidade (rms_norm); um zumbido baixo marca a duração do som.
Também gera o teste S-05 (estéreo L→R) e atualiza RP/sounds/sound_definitions.json.
Os sons de verdade saem de tools/synth/ completo na F2. Precisa de numpy e ffmpeg (libvorbis)."""
import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AU = json.loads((ROOT / "spec/audio_cues.json").read_text(encoding="utf-8"))
P = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
NS = P["namespace"]
SR = 44100
OUT = ROOT / "RP/sounds/singularity"
SD = ROOT / "RP/sounds/sound_definitions.json"


def to_ogg(stereo, path):
    """stereo: array (n, 2) ou (n,) em [-1, 1] → .ogg vorbis q6 (mono se 1 canal)."""
    data = np.clip(stereo, -1, 1)
    ch = 1 if data.ndim == 1 else data.shape[1]
    pcm = (data * 32767).astype("<i2").tobytes()
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "x.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm)
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "6",
                        "-fflags", "+bitexact", "-flags:a", "+bitexact", str(path)], check=True)


def beep(n, freq, amp, dur=0.06):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.004) * np.exp(-t / (dur / 3))
    # 2º e 3º harmônicos: o alto-falante do celular não toca grave (P-48)
    return amp * env * (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(4 * np.pi * freq * t) + 0.2 * np.sin(6 * np.pi * freq * t))


def render(s):
    n = int(SR * (s["end_tick"] - s["tick"]) / 20) + SR // 10
    out = np.zeros(n)
    t = np.arange(n) / SR
    out += 0.05 * np.sin(2 * np.pi * 110 * t) * np.minimum(1, t / 0.05) * np.minimum(1, (n / SR - t) / 0.05)
    for o in s["onsets_intended"]:
        i = int(SR * (o["tick"] - s["tick"]) / 20)
        b = beep(n, 330 + 1400 * o["rms_norm"], 0.25 + 0.6 * o["rms_norm"])
        j = min(n, i + len(b))
        out[i:j] += b[: j - i]
    return out / max(1.0, np.max(np.abs(out)) / 0.89)  # pico ≤ −1 dBFS


sd = json.loads(SD.read_text(encoding="utf-8"))
for s in AU["sounds"]:
    mono = render(s)
    to_ogg(np.stack([mono, mono], axis=1), OUT / f"{s['id']}.ogg")
    to_ogg(mono, OUT / f"{s['id']}_m.ogg")

# S-05: tom com pulsos, pan L → R em 4 s, duas vezes (pan de potência constante)
dur = 8.5
t = np.arange(int(SR * dur)) / SR
sig = 0.5 * np.sin(2 * np.pi * 440 * t) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 4 * t)))
pan = np.clip((t % 4.25) / 4.0, 0, 1)
L, R = sig * np.cos(pan * np.pi / 2), sig * np.sin(pan * np.pi / 2)
to_ogg(np.stack([L, R], axis=1), OUT / "sgx_spike_pan.ogg")
sd["sound_definitions"][f"{NS}:sgx2d_spike_pan"] = {"category": "ui", "sounds": [
    {"name": "sounds/singularity/sgx_spike_pan", "is3D": False, "stream": False, "load_on_low_memory": True, "volume": 1.0}]}
SD.write_text(json.dumps(sd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"✓ áudio provisório: {len(AU['sounds'])} sons (estéreo + _m mono) + sgx_spike_pan")
