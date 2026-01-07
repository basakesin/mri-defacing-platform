# defacers/deepdefacer.py
from __future__ import annotations
from pathlib import Path
import subprocess
from .utils import which


def is_available() -> bool:
    return which("deepdefacer")


def run(input_path: Path, output_path: Path) -> None:
    cmd = [
        "deepdefacer",
        "--input_file", str(input_path),
        "--defaced_output_path", str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
