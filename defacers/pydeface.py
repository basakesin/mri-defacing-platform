from __future__ import annotations
from pathlib import Path
import subprocess
from .utils import which


def is_available() -> bool:
    return which("pydeface")


def run(input_path: Path, output_path: Path) -> None:
    cmd = ["pydeface", str(input_path), "--outfile", str(output_path), "--force"]
    subprocess.run(cmd, check=True, capture_output=True)
