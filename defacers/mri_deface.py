# defacers/mri_deface.py
from __future__ import annotations
from pathlib import Path
import subprocess
from .utils import which


def is_available() -> bool:
    return which("mri_deface")


def run(input_path: Path, output_path: Path) -> None:
    cmd = ["mri_deface", str(input_path), str(output_path)]
    subprocess.run(cmd, check=True, capture_output=True)
