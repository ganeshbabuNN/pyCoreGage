"""
pyCoreGage.runner
=================
run_checks() — loops through all active rule sets, dynamically imports
each check script, and dispatches check_RULESET(state, cfg).
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import types
from pathlib import Path

from .state import CoreGageConfig, CoreGageState

logger = logging.getLogger("pyCoreGage")


def _load_check_module(check_file: str, rule_set: str) -> types.ModuleType:
    """
    Dynamically load a check script as a module.

    Equivalent to R's ``sys.source(check_file, envir = check_env)``.

    Parameters
    ----------
    check_file : str
        Absolute path to the Python check script.
    rule_set : str
        Rule-set name (used as the module name to avoid collisions).

    Returns
    -------
    types.ModuleType
    """
    # Build a unique module name so repeated imports don't collide
    mod_name = f"_pycoregage_check_{rule_set}"

    # Remove any previously loaded version from sys.modules
    sys.modules.pop(mod_name, None)

    spec = importlib.util.spec_from_file_location(mod_name, check_file)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_checks(cfg: CoreGageConfig, state: CoreGageState) -> CoreGageState:
    """
    Execute all active check scripts.

    Iterates over active rule sets in ``state.rule_registry``, loads each
    check script from the appropriate folder
    (``cfg.trial_checks`` for Trial sheet, ``cfg.study_checks`` for Study sheet),
    and calls ``check_RULESET(state, cfg)``.

    The check function **must** be named exactly ``check_{Rule_Set}``
    (e.g. ``check_AE``, ``check_LB_study``).

    Parameters
    ----------
    cfg : CoreGageConfig
        Project configuration providing check script folder paths.
    state : CoreGageState
        Run state returned by :func:`setup_coregage`.

    Returns
    -------
    CoreGageState
        Updated state with ``issues`` and ``summary_log`` populated.

    Examples
    --------
    >>> from pyCoreGage import setup_coregage, run_checks
    >>> state = setup_coregage(cfg)
    >>> state.domains = load_inputs(cfg)
    >>> state = run_checks(cfg, state)
    """
    logger.info(">> [runner] Starting check execution ...")

    reg = state.rule_registry
    sources = reg["sheet"].dropna().unique().tolist()

    for src in sources:
        check_dir = cfg.trial_checks if src == "Trial" else cfg.study_checks

        active_sets = (
            reg.loc[
                (reg["sheet"] == src) & reg["active"].str.startswith("Y"),
                "rule_set",
            ]
            .dropna()
            .unique()
        )
        active_sets = sorted(active_sets)

        if len(active_sets) == 0:
            logger.info(">> [runner] No active rule sets for sheet: %s", src)
            continue

        for rs in active_sets:
            check_file = os.path.join(check_dir, f"{rs}.py")
            logger.info(
                "%s Executing: %s %s",
                ">" * 20, rs, "<" * 20,
            )

            if not os.path.isfile(check_file):
                logger.warning(
                    "  WARNING: Check script not found: %s -- skipping.", check_file
                )
                continue

            try:
                mod     = _load_check_module(check_file, rs)
                fn_name = f"check_{rs}"

                if not hasattr(mod, fn_name):
                    raise AttributeError(
                        f"Function '{fn_name}' not found in {check_file}. "
                        f"Ensure the function is named check_{rs}(state, cfg)."
                    )

                check_fn = getattr(mod, fn_name)
                state    = check_fn(state, cfg)

            except Exception as exc:
                logger.error("  ERROR in rule set %s: %s", rs, exc)

            logger.info(
                "%s Finished:  %s %s",
                ">" * 20, rs, "<" * 20,
            )

    n_issues = len(state.issues)
    logger.info(">> [runner] All checks executed. Total findings: %d", n_issues)
    return state
