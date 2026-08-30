# Run all Python analyses.

from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
scripts = [
    "Table_1.py",
    "Table_2.py",
    "Table_3.py",
    "Table_4.py",
    "Figure_1.py",
    "Figure_2.py",
    "Supplementary_Table_S1.py",
    "Supplementary_Table_S2.py",
    "Supplementary_Table_S3.py",
    "Supplementary_Table_S4.py",
    "Supplementary_Table_S5.py",
    "Supplementary_Table_S6.py",
    "Supplementary_Figure_S1.py",
    "Supplementary_Figure_S2.py",
    "Supplementary_Figure_S3.py",
]

data_arg = sys.argv[1] if len(sys.argv) > 1 else None

for script in scripts:
    cmd = [sys.executable, str(here / script)]
    if data_arg:
        cmd.append(data_arg)
    print(f"\n=== {script} ===")
    subprocess.run(cmd, check=True)
