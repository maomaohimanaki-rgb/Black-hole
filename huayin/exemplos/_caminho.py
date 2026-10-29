# Permite rodar os exemplos sem instalar o pacote (python3 exemplos/01_primeira_nota.py)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
SAIDA = Path(__file__).resolve().parent / "saida"
SAIDA.mkdir(exist_ok=True)
