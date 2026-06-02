from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_INPUT_DIR = PROJECT_ROOT / "data" / "input"
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

MAIN_WAREHOUSE_LOCATIONS = {"Depozitare", "Receptie"}
