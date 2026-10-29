#!/usr/bin/env python3
"""Empacota BP/ + RP/ em dist/DoomsDay_<versão>[_teste-<n>].mcaddon.
- Build de teste (padrão): UUIDs NOVOS a cada build (P-49), para o jogo não acusar pacote duplicado.
- --release: UUIDs estáveis de spec/project.json.
Antes de zipar, valida (P-49): todo JSON abre, BP depende do RP, a entrada do script existe, os sons
referenciados existem. Uso: python3 tools/package.py [--release] [--no-build]"""
import json
import re
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "spec/project.json").read_text(encoding="utf-8"))
release = "--release" in sys.argv
if "--no-build" not in sys.argv:
    subprocess.run([sys.executable, str(ROOT / "tools/build_all.py")], check=True)

ver = P["version"]
vlist = [int(x) for x in ver.split(".")]
errs = []

# ------------------------------------------------------------------ validação
for pack in ("BP", "RP"):
    for f in (ROOT / pack).rglob("*.json"):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append(f"{f.relative_to(ROOT)}: JSON inválido ({e})")
bp = json.loads((ROOT / "BP/manifest.json").read_text(encoding="utf-8"))
rp = json.loads((ROOT / "RP/manifest.json").read_text(encoding="utf-8"))
if not any(d.get("uuid") == rp["header"]["uuid"] for d in bp["dependencies"]):
    errs.append("BP não depende do RP")
entry = next(m["entry"] for m in bp["modules"] if m["type"] == "script")
if not (ROOT / "BP" / entry).exists():
    errs.append(f"entrada do script não existe: {entry}")
sd = json.loads((ROOT / "RP/sounds/sound_definitions.json").read_text(encoding="utf-8"))["sound_definitions"]
for sid, d in sd.items():
    for s in d["sounds"]:
        if not (ROOT / "RP" / f"{s['name']}.ogg").exists():
            errs.append(f"som sem arquivo: {sid} → {s['name']}.ogg")
for js in (ROOT / "BP/scripts").rglob("*.js"):
    for m in re.finditer(r'from "(\.[^"]+)"', js.read_text(encoding="utf-8")):
        if not (js.parent / m.group(1)).resolve().exists():
            errs.append(f"import quebrado: {js.relative_to(ROOT)} → {m.group(1)}")
if errs:
    sys.exit("✗ pacote inválido:\n  " + "\n  ".join(errs))

# ------------------------------------------------------------------ UUIDs e versão
if release:
    ids = {k: P["uuids"][k] for k in P["uuids"]}
    name = f"DoomsDay_{ver}"
else:
    ids = {k: str(uuid.uuid4()) for k in P["uuids"]}
    dist = ROOT / "dist"
    n = 1 + max([int(m.group(1)) for f in dist.glob(f"DoomsDay_{ver}_teste-*.mcaddon")
                 if (m := re.search(r"_teste-(\d+)\.mcaddon$", f.name))] + [0])
    name = f"DoomsDay_{ver}_teste-{n}"


def manifest(m, kind):
    m = json.loads(json.dumps(m))
    m["header"]["version"] = vlist
    if kind == "BP":
        m["header"]["uuid"] = ids["bp_header"]
        for mod in m["modules"]:
            mod["version"] = vlist
            mod["uuid"] = ids["bp_data_module"] if mod["type"] == "data" else ids["bp_script_module"]
        for d in m["dependencies"]:
            if "uuid" in d:
                d["uuid"], d["version"] = ids["rp_header"], vlist
    else:
        m["header"]["uuid"] = ids["rp_header"]
        m["modules"][0]["uuid"], m["modules"][0]["version"] = ids["rp_resources_module"], vlist
    return json.dumps(m, indent=2, ensure_ascii=False)


out = ROOT / "dist" / f"{name}.mcaddon"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for pack, man in (("BP", bp), ("RP", rp)):
        for f in sorted((ROOT / pack).rglob("*")):
            if f.is_dir() or f.name.startswith("."):
                continue
            arc = f"DoomsDay_{pack}/{f.relative_to(ROOT / pack).as_posix()}"
            if f.relative_to(ROOT / pack).as_posix() == "manifest.json":
                z.writestr(arc, manifest(man, pack))
            else:
                z.write(f, arc)
mix = ROOT / "build/singularity_mix.mp3"
if mix.exists():
    import shutil
    shutil.copyfile(mix, ROOT / "dist" / f"DoomsDay_{ver}_mixdown.mp3")
print(f"✓ {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB, {'UUIDs estáveis' if release else 'UUIDs novos'})")
