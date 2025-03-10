# SPDX-License-Identifier: LGPL-3.0-or-later
from deepmd.utils.entry_point import (
    load_entry_point,
)

from .common import (
    DEFAULT_PRECISION,
    PRECISION_DICT,
    NativeOP,
)
from .model import (
    DPModelCommon,
)
from .output_def import (
    FittingOutputDef,
    ModelOutputDef,
    OutputVariableDef,
    fitting_check_output,
    get_deriv_name,
    get_hessian_name,
    get_reduce_name,
    model_check_output,
)

__all__ = [
    "DPModelCommon",
    "PRECISION_DICT",
    "DEFAULT_PRECISION",
    "NativeOP",
    "ModelOutputDef",
    "FittingOutputDef",
    "OutputVariableDef",
    "model_check_output",
    "fitting_check_output",
    "get_reduce_name",
    "get_deriv_name",
    "get_hessian_name",
]


load_entry_point("deepmd.dpmodel")
