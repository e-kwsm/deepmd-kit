# SPDX-License-Identifier: LGPL-3.0-or-later
"""Module providing compatibility between `0.x.x` and `1.x.x` input versions."""

import json
import warnings
from collections.abc import (
    Sequence,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
    Optional,
    Union,
)

import numpy as np

from deepmd.common import (
    j_deprecated,
)


def convert_input_v0_v1(
    jdata: dict[str, Any], warning: bool = True, dump: Optional[Union[str, Path]] = None
) -> dict[str, Any]:
    """Convert input from v0 format to v1.

    Parameters
    ----------
    jdata : dict[str, Any]
        loaded json/yaml file
    warning : bool, optional
        whether to show deprecation warning, by default True
    dump : Optional[Union[str, Path]], optional
        whether to dump converted file, by default None

    Returns
    -------
    dict[str, Any]
        converted output
    """
    output = {}
    output["model"] = _model(jdata, jdata["use_smooth"])
    output["learning_rate"] = _learning_rate(jdata)
    output["loss"] = _loss(jdata)
    output["training"] = _training(jdata)
    if warning:
        _warning_input_v0_v1(dump)
    if dump is not None:
        with open(dump, "w") as fp:
            json.dump(output, fp, indent=4)
    return output


def _warning_input_v0_v1(fname: Optional[Union[str, Path]]) -> None:
    msg = (
        "It seems that you are using a deepmd-kit input of version 0.x.x, "
        "which is deprecated. we have converted the input to >2.0.0 compatible"
    )
    if fname is not None:
        msg += f", and output it to file {fname}"
    warnings.warn(msg)


def _model(jdata: dict[str, Any], smooth: bool) -> dict[str, dict[str, Any]]:
    """Convert data to v1 input for non-smooth model.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data
    smooth : bool
        whether to use smooth or non-smooth descriptor version

    Returns
    -------
    dict[str, dict[str, Any]]
        dictionary with model input parameters and sub-dictionaries for descriptor and
        fitting net
    """
    model = {}
    model["descriptor"] = (
        _smth_descriptor(jdata) if smooth else _nonsmth_descriptor(jdata)
    )
    model["fitting_net"] = _fitting_net(jdata)
    return model


def _nonsmth_descriptor(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for non-smooth descriptor.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with descriptor parameters
    """
    descriptor = {}
    descriptor["type"] = "loc_frame"
    _jcopy(jdata, descriptor, ("sel_a", "sel_r", "rcut", "axis_rule"))
    return descriptor


def _smth_descriptor(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for smooth descriptor.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with descriptor parameters
    """
    descriptor = {}
    seed = jdata.get("seed", None)
    if seed is not None:
        descriptor["seed"] = seed
    descriptor["type"] = "se_a"
    descriptor["sel"] = jdata["sel_a"]
    _jcopy(jdata, descriptor, ("rcut",))
    descriptor["rcut_smth"] = jdata.get("rcut_smth", descriptor["rcut"])
    descriptor["neuron"] = jdata["filter_neuron"]
    descriptor["axis_neuron"] = j_deprecated(jdata, "axis_neuron", ["n_axis_neuron"])
    descriptor["resnet_dt"] = False
    if "resnet_dt" in jdata:
        descriptor["resnet_dt"] = jdata["filter_resnet_dt"]

    return descriptor


def _fitting_net(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for fitting net.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with fitting net parameters
    """
    fitting_net = {}

    seed = jdata.get("seed", None)
    if seed is not None:
        fitting_net["seed"] = seed
    fitting_net["neuron"] = j_deprecated(jdata, "fitting_neuron", ["n_neuron"])
    fitting_net["resnet_dt"] = True
    if "resnet_dt" in jdata:
        fitting_net["resnet_dt"] = jdata["resnet_dt"]
    if "fitting_resnet_dt" in jdata:
        fitting_net["resnet_dt"] = jdata["fitting_resnet_dt"]
    return fitting_net


def _learning_rate(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for learning rate section.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with learning rate parameters
    """
    learning_rate = {}
    learning_rate["type"] = "exp"
    _jcopy(jdata, learning_rate, ("decay_steps", "decay_rate", "start_lr"))
    return learning_rate


def _loss(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for loss function.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with loss function parameters
    """
    loss: dict[str, Any] = {}
    _jcopy(
        jdata,
        loss,
        (
            "start_pref_e",
            "limit_pref_e",
            "start_pref_f",
            "limit_pref_f",
            "start_pref_v",
            "limit_pref_v",
        ),
    )
    if "start_pref_ae" in jdata:
        loss["start_pref_ae"] = jdata["start_pref_ae"]
    if "limit_pref_ae" in jdata:
        loss["limit_pref_ae"] = jdata["limit_pref_ae"]
    return loss


def _training(jdata: dict[str, Any]) -> dict[str, Any]:
    """Convert data to v1 input for training.

    Parameters
    ----------
    jdata : dict[str, Any]
        parsed input json/yaml data

    Returns
    -------
    dict[str, Any]
        dict with training parameters
    """
    training = {}
    seed = jdata.get("seed", None)
    if seed is not None:
        training["seed"] = seed

    _jcopy(jdata, training, ("systems", "set_prefix", "stop_batch", "batch_size"))
    training["disp_file"] = "lcurve.out"
    if "disp_file" in jdata:
        training["disp_file"] = jdata["disp_file"]
    training["disp_freq"] = jdata["disp_freq"]
    training["numb_test"] = jdata["numb_test"]
    training["save_freq"] = jdata["save_freq"]
    training["save_ckpt"] = jdata["save_ckpt"]
    training["disp_training"] = jdata["disp_training"]
    training["time_training"] = jdata["time_training"]
    if "profiling" in jdata:
        training["profiling"] = jdata["profiling"]
        if training["profiling"]:
            training["profiling_file"] = jdata["profiling_file"]
    return training


def _jcopy(src: dict[str, Any], dst: dict[str, Any], keys: Sequence[str]) -> None:
    """Copy specified keys from one dict to another.

    Parameters
    ----------
    src : dict[str, Any]
        source dictionary
    dst : dict[str, Any]
        destination dictionary, will be modified in place
    keys : Sequence[str]
        list of keys to copy
    """
    for k in keys:
        if k in src:
            dst[k] = src[k]


def remove_decay_rate(jdata: dict[str, Any]) -> None:
    """Convert decay_rate to stop_lr.

    Parameters
    ----------
    jdata : dict[str, Any]
        input data
    """
    lr = jdata["learning_rate"]
    if "decay_rate" in lr:
        decay_rate = lr["decay_rate"]
        start_lr = lr["start_lr"]
        stop_step = jdata["training"]["stop_batch"]
        decay_steps = lr["decay_steps"]
        stop_lr = np.exp(np.log(decay_rate) * (stop_step / decay_steps)) * start_lr
        lr["stop_lr"] = stop_lr
        lr.pop("decay_rate")


def convert_input_v1_v2(
    jdata: dict[str, Any], warning: bool = True, dump: Optional[Union[str, Path]] = None
) -> dict[str, Any]:
    tr_cfg = jdata["training"]
    tr_data_keys = {
        "systems",
        "set_prefix",
        "batch_size",
        "sys_prob",
        "auto_prob",
        # alias included
        "sys_weights",
        "auto_prob_style",
    }

    tr_data_cfg = {k: v for k, v in tr_cfg.items() if k in tr_data_keys}
    new_tr_cfg = {k: v for k, v in tr_cfg.items() if k not in tr_data_keys}
    new_tr_cfg["training_data"] = tr_data_cfg
    if "training_data" in tr_cfg:
        raise RuntimeError(
            "Both v1 (training/systems) and v2 (training/training_data) parameters are given."
        )

    jdata["training"] = new_tr_cfg

    # remove deprecated arguments
    remove_decay_rate(jdata)

    if warning:
        _warning_input_v1_v2(dump)
    if dump is not None:
        with open(dump, "w") as fp:
            json.dump(jdata, fp, indent=4)

    return jdata


def _warning_input_v1_v2(fname: Optional[Union[str, Path]]) -> None:
    msg = (
        "It seems that you are using a deepmd-kit input of version 1.x.x, "
        "which is deprecated. we have converted the input to >2.0.0 compatible"
    )
    if fname is not None:
        msg += f", and output it to file {fname}"
    warnings.warn(msg)


def deprecate_numb_test(
    jdata: dict[str, Any], warning: bool = True, dump: Optional[Union[str, Path]] = None
) -> dict[str, Any]:
    """Deprecate `numb_test` since v2.1. It has taken no effect since v2.0.

    See `#1243 <https://github.com/deepmodeling/deepmd-kit/discussions/1243>`_.

    Parameters
    ----------
    jdata : dict[str, Any]
        loaded json/yaml file
    warning : bool, optional
        whether to show deprecation warning, by default True
    dump : Optional[Union[str, Path]], optional
        whether to dump converted file, by default None

    Returns
    -------
    dict[str, Any]
        converted output
    """
    try:
        jdata.get("training", {}).pop("numb_test")
    except KeyError:
        pass
    else:
        if warning:
            warnings.warn(
                "The argument training->numb_test has been deprecated since v2.0.0. "
                "Use training->validation_data->batch_size instead."
            )

    if dump is not None:
        with open(dump, "w") as fp:
            json.dump(jdata, fp, indent=4)
    return jdata


def update_deepmd_input(
    jdata: dict[str, Any], warning: bool = True, dump: Optional[Union[str, Path]] = None
) -> dict[str, Any]:
    def is_deepmd_v0_input(jdata):
        return "model" not in jdata.keys()

    def is_deepmd_v1_input(jdata):
        return "systems" in jdata["training"].keys()

    if is_deepmd_v0_input(jdata):
        jdata = convert_input_v0_v1(jdata, warning, None)
        jdata = convert_input_v1_v2(jdata, False, None)
        jdata = deprecate_numb_test(jdata, False, dump)
    elif is_deepmd_v1_input(jdata):
        jdata = convert_input_v1_v2(jdata, warning, None)
        jdata = deprecate_numb_test(jdata, False, dump)
    else:
        jdata = deprecate_numb_test(jdata, warning, dump)

    return jdata
