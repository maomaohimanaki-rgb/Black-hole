#!/usr/bin/env python3
"""Roda todos os geradores na ordem certa (idempotente). Depois: node --test tests/*.test.mjs e tools/package.py."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["tools/check_spec.py", "tools/gen_templates.py", "tools/build_storyboard_data.py", "tools/gen_assets.py",
         "tools/synth/render.py", "tools/build_timeline.py", "tools/gen_ui.py"]
for s in STEPS:
    r = subprocess.run([sys.executable, str(ROOT / s)], cwd=ROOT)
    if r.returncode:
        sys.exit(f"✗ {s} falhou")
