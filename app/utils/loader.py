import os
from pathlib import Path

def load_fixture(filename: str) -> str:
    """
    Loads a fixture file using a robust absolute path search.
    """
    # Buscamos la carpeta del proyecto actual
    current_path = Path(__file__).resolve()
    
    # Buscamos la raíz subiendo hasta encontrar 'tests'
    project_root = current_path
    for parent in current_path.parents:
        if (parent / "tests").exists():
            project_root = parent
            break
            
    path = project_root / "tests" / "fixtures" / filename
    
    if not path.exists():
        # Esto te dirá exactamente dónde está intentando buscar
        raise FileNotFoundError(f"Fixture not found at: {path.absolute()}")
        
    with open(path, "r", encoding="utf-8") as f:
        return f.read()