# defacers/base.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class Defacer:
    key: str
    label: str
    description: str
    is_available: Callable[[], bool]
    run: Callable[[Path, Path], None]
