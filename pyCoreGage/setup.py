"""
pyCoreGage.setup
================
Initialises a pyCoreGage run session.

Reads rule_registry.xlsx, builds the active-rule switch dictionary,
and returns a fresh CoreGageState ready for use.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional

import pandas as pd

from .state import (
    CoreGageConfig, CoreGageState,
    _empty_issues, _empty_summary_log, _empty_review_log,
)

logger = logging.getLogger("pyCoreGage")

_REQUIRED_COLS = [
    "category", "subcategory", "id", "active",
    "dm_report", "mw_report", "sdtm_report", "adam_report",
    "rule_set", "description", "notes",
]

_COL_MAP = {
    "Category":    "category",
    "Subcategory": "subcategory",
    "ID":          "id",
    "Active":      "active",
    "DM_Report":   "dm_report",
    "MW_Report":   "mw_report",
    "SDTM_Report": "sdtm_report",
    "ADAM_Report": "adam_report",
    "Rule_Set":    "rule_set",
    "Description": "description",
    "Notes":       "notes",
}


def _read_sheet(path: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Read one sheet from rule_registry.xlsx and normalise it.

    Returns None if the sheet does not exist or has no valid rows.
    """
    try:
        xl = pd.ExcelFile(path)
        if sheet_name not in xl.sheet_names:
            logger.info("  NOTE: sheet '%s' not found — skipping.", sheet_name)
            return None

        df = xl.parse(sheet_name, dtype=str)
    except Exception as exc:
        logger.warning("  Could not read sheet '%s': %s", sheet_name, exc)
        return None

    logger.info("  Sheet '%s' columns : %s", sheet_name, ", ".join(df.columns))
    logger.info("  Sheet '%s' rows    : %d", sheet_name, len(df))

    # Rename known columns
    df = df.rename(columns=_COL_MAP)

    # Add any missing required columns
    for col in _REQUIRED_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    # Keep only required columns (drops unknown extras)
    df = df[_REQUIRED_COLS].copy()

    # Debug: first 10 IDs
    logger.info("  First 10 IDs:")
    for i, row in df.head(10).iterrows():
        logger.info("    [%d] '%s'  active='%s'", i, row["id"], row["active"])

    # Strip whitespace and normalise
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})

    # Filter out blank IDs and the placeholder row
    mask = (
        df["id"].notna()
        & (df["id"].fillna("") != "")
        & (df["id"].str.upper() != "YOURID")
    )
    df = df[mask].copy()

    if df.empty:
        logger.info("  NOTE: sheet '%s' has no valid rows.", sheet_name)
        return None

    df["sheet"] = sheet_name

    # Normalise key columns
    df["id"]          = df["id"].str.upper()
    df["active"]      = df["active"].str.upper().fillna("")
    df["dm_report"]   = df["dm_report"].str.upper().fillna("")
    df["mw_report"]   = df["mw_report"].str.upper().fillna("")
    df["sdtm_report"] = df["sdtm_report"].str.upper().fillna("")
    df["adam_report"] = df["adam_report"].str.upper().fillna("")

    logger.info("  Valid rows from '%s': %d", sheet_name, len(df))
    return df


def setup_coregage(cfg: CoreGageConfig) -> CoreGageState:
    """
    Initialise a pyCoreGage run session.

    Reads rule_registry.xlsx, builds the active-rule switch dictionary,
    and returns a fresh :class:`CoreGageState`.

    Parameters
    ----------
    cfg : CoreGageConfig
        Project configuration.  ``cfg.rule_registry`` must point to a
        readable ``rule_registry.xlsx`` file.

    Returns
    -------
    CoreGageState

    Raises
    ------
    FileNotFoundError
        If ``rule_registry.xlsx`` does not exist.
    ValueError
        If no valid check definitions are found.

    Examples
    --------
    >>> from pyCoreGage import CoreGageConfig, setup_coregage
    >>> cfg = CoreGageConfig(
    ...     project_name="TRIAL_ABC",
    ...     rule_registry="/path/to/rule_registry.xlsx",
    ...     trial_checks="/path/to/rules/trial",
    ...     study_checks="/path/to/rules/study",
    ...     inputs="/path/to/inputs",
    ...     reports="/path/to/outputs/reports",
    ...     feedback="/path/to/outputs/feedback",
    ... )
    >>> state = setup_coregage(cfg)
    """
    logger.info(">> [setup] Starting CoreGage initialisation ...")

    import os
    if not os.path.isfile(cfg.rule_registry):
        raise FileNotFoundError(
            f"rule_registry.xlsx not found at: {cfg.rule_registry}"
        )

    trial_df = _read_sheet(cfg.rule_registry, "Trial")
    study_df = _read_sheet(cfg.rule_registry, "Study")

    sheets = [df for df in [trial_df, study_df] if df is not None]
    if not sheets:
        raise ValueError(
            "No valid check definitions found in rule_registry.xlsx. "
            "Ensure sheets are named 'Trial' and/or 'Study'."
        )

    rule_registry = pd.concat(sheets, ignore_index=True)
    rule_registry = rule_registry.sort_values(
        ["rule_set", "id"], na_position="last"
    ).reset_index(drop=True)

    logger.info(
        ">> [setup] Imported %d rules from: %s",
        len(rule_registry),
        " + ".join(rule_registry["sheet"].unique()),
    )

    n_on  = rule_registry["active"].str.startswith("Y").sum()
    n_off = len(rule_registry) - n_on
    logger.info("  Active: %d ON  /  %d OFF", n_on, n_off)

    # Build active-rules switch dict  (replaces R named logical vector)
    active_rules: dict[str, bool] = {
        row["id"]: row["active"].startswith("Y")
        for _, row in rule_registry.iterrows()
    }

    session = {
        "sdate": date.today().strftime("%d%b%Y"),
        "stime": datetime.now().strftime("%H:%M"),
    }

    state = CoreGageState(
        rule_registry = rule_registry,
        active_rules  = active_rules,
        session       = session,
        issues        = _empty_issues(),
        summary_log   = _empty_summary_log(),
        review_log    = _empty_review_log(),
        domains       = {},
    )

    logger.info(">> [setup] Initialisation complete.")
    return state
