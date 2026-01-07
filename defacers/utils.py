# defacers/utils.py
from __future__ import annotations
from pathlib import Path
import shutil


def strip_nii_suffix(name: str) -> str:
    if name.endswith(".nii.gz"):
        return name[: -len(".nii.gz")]
    if name.endswith(".nii"):
        return name[: -len(".nii")]
    return Path(name).stem


def which(cmd: str) -> bool:
    return shutil.which(cmd) is not None
