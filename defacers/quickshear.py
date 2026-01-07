# defacers/quickshear.py
from __future__ import annotations
from pathlib import Path
import subprocess
from .utils import which, strip_nii_suffix


def is_available() -> bool:
    return which("bet") and which("quickshear")


def run(input_path: Path, output_path: Path) -> None:
    base = strip_nii_suffix(input_path.name)
    brain_base = input_path.with_name(base + "_brain")

    bet_cmd = [
        "bet", str(input_path), str(brain_base),
        "-R", "-f", "0.5", "-g", "0", "-m"
    ]
    subprocess.run(bet_cmd, check=True, capture_output=True)

    brain_img_path = brain_base.with_suffix(".nii.gz")
    if not brain_img_path.exists():
        raise RuntimeError(f"BET brain output not found: {brain_img_path}")

    qs_cmd = ["quickshear", str(input_path), str(brain_img_path), str(output_path)]
    subprocess.run(qs_cmd, check=True, capture_output=True)
