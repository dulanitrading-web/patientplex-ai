"""Check schema registration in a fresh interpreter, without a database connection."""
import subprocess
import sys
from pathlib import Path


def test_standalone_schema_registration():
    backend = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, "-c",
         "from create_tables import Base; "
         "assert {'clinic_staff', 'patients', 'appointments'} <= set(Base.metadata.tables); "
         "list(Base.metadata.sorted_tables)"],
        cwd=backend, check=True,
    )
