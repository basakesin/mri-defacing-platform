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
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"deepdefacer failed (exit {result.returncode}): {stderr}")
