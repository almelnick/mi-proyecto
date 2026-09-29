import sys
from pathlib import Path

# Permite importar `generador` al correr pytest desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).parent.parent))
