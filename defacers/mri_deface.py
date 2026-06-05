from __future__ import annotations
import os
import subprocess
from pathlib import Path

_BIN_DIR = Path(__file__).parent.parent / "bin"
_BINARY = _BIN_DIR / "mri_deface"
_TALAIRACH_GCA = _BIN_DIR / "talairach_mixed_with_skull.gca"
_FACE_GCA = _BIN_DIR / "face.gca"


def is_available() -> bool:
    return (
        _BINARY.exists()
        and _TALAIRACH_GCA.exists()
        and _FACE_GCA.exists()
    )


def run(input_path: Path, output_path: Path) -> None:
    cmd = [
        str(_BINARY),
        str(input_path),
        str(_TALAIRACH_GCA),
        str(_FACE_GCA),
        str(output_path),
    ]
    env = {**os.environ, "DYLD_LIBRARY_PATH": str(_BIN_DIR)}
    result = subprocess.run(cmd, capture_output=True, env=env)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        if "could not find wm peak" in stderr:
            raise RuntimeError(
                "mri_deface could not process this image: white matter peak not found. "
                "mri_deface requires a T1-weighted whole-brain MRI. "
                "Non-brain regions, non-T1 contrasts, and partial field-of-view scans are not supported."
            )
        raise RuntimeError(f"mri_deface failed (exit {result.returncode}): {stderr}")
