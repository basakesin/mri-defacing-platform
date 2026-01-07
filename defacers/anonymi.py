# defacers/anonymi.py
from __future__ import annotations
from pathlib import Path
import subprocess
from .utils import which


def is_available() -> bool:
    # Hem python package hem de CLI senaryosunu kapsamak için:
    if which("anonymi"):
        return True
    try:
        import anonymi  # noqa: F401
        return True
    except Exception:
        return False


def run(input_path: Path, output_path: Path) -> None:
    try:
        from anonymi import anonymize
        anonymize(str(input_path), str(output_path))
    except ImportError:
        cmd = ["anonymi", str(input_path), str(output_path)]
        subprocess.run(cmd, check=True, capture_output=True)
