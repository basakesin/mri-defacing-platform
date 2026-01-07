from .base import Defacer

from . import pydeface as pydeface_mod
from . import quickshear as quickshear_mod
from . import deepdefacer as deepdefacer_mod
from . import mri_deface as mri_deface_mod

DEFACERS = {
    "pydeface": Defacer(
        key="pydeface",
        label="PyDeface",
        description="PyDeface - Industry standard FSL-based method",
        is_available=pydeface_mod.is_available,
        run=pydeface_mod.run,
    ),
    "quickshear": Defacer(
        key="quickshear",
        label="Quickshear",
        description="Quickshear - Fast and high-quality defacing",
        is_available=quickshear_mod.is_available,
        run=quickshear_mod.run,
    ),
    "deepdefacer": Defacer(
        key="deepdefacer",
        label="DeepDefacer",
        description="DeepDefacer - AI-powered face detection",
        is_available=deepdefacer_mod.is_available,
        run=deepdefacer_mod.run,
    ),
    "mri_deface": Defacer(
        key="mri_deface",
        label="MRI Deface",
        description="MRI Deface - FreeSurfer-based approach",
        is_available=mri_deface_mod.is_available,
        run=mri_deface_mod.run,
    ),
}
