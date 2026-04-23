"""
pyCoreGage.collector
====================
collect_findings() — validates a check's output DataFrame and appends
findings to the master issues table in state.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import pandas as pd

from .state import CoreGageState
from .counter import count_valid

logger = logging.getLogger("pyCoreGage")


def collect_findings(
    state: CoreGageState,
    df: Optional[pd.DataFrame],
    id: str,
    desc_col: str = "description",
    sobs: bool = True,
    unblind_codes: List[str] = None,
) -> CoreGageState:
    """
    Collect findings from a single check into the master issues table.

    Called at the end of every individual check block.  Validates the
    findings DataFrame, counts valid observations, and appends to
    ``state.issues`` and ``state.summary_log``.

    Parameters
    ----------
    state : CoreGageState
        Current run state (mutated in place and returned).
    df : pd.DataFrame or None
        Findings produced by the check.  Must contain columns:

        - ``subj_id`` (str) — subject identifier
        - ``vis_id``  (float or NaN) — visit number
        - ``description`` (str, max 200 chars) — human-readable finding

    id : str
        Check ID matching the ``ID`` column in rule_registry.xlsx.
    desc_col : str, optional
        Name of the description column in *df*.  Default ``"description"``.
    sobs : bool, optional
        Whether to flag output as subject-observation-limited.  Default True.
    unblind_codes : list of str, optional
        Topic codes used for unblinding protection.  Default None (no filtering).

    Returns
    -------
    CoreGageState
        Updated state object.

    Examples
    --------
    >>> import pandas as pd
    >>> from pyCoreGage import CoreGageState, collect_findings
    >>> state = CoreGageState()
    >>> findings = pd.DataFrame({
    ...     "subj_id":     ["SUBJ-001", "SUBJ-002"],
    ...     "vis_id":      [float("nan"), float("nan")],
    ...     "description": ["AESEV missing for RASH", "AESEV missing for HEADACHE"],
    ... })
    >>> state = collect_findings(state, findings, id="AECHK001")
    """
    if df is None or not isinstance(df, pd.DataFrame):
        logger.warning(
            "  WARNING [collector]: dataset for %s is None or not a DataFrame. Skipping.", id
        )
        return state

    if "subj_id" not in df.columns:
        logger.warning(
            "  WARNING [collector]: subj_id column missing for %s. Skipping.", id
        )
        return state

    if desc_col not in df.columns:
        logger.warning(
            "  WARNING [collector]: description column '%s' missing for %s. Skipping.",
            desc_col, id,
        )
        return state

    # Check for rows with empty/null descriptions
    empty_desc_mask = df[desc_col].isna() | (df[desc_col].astype(str).str.strip() == "")
    if empty_desc_mask.any():
        logger.warning(
            "  WARNING [collector]: %d rows have empty descriptions for %s. Skipping.",
            empty_desc_mask.sum(), id,
        )
        return state

    n = count_valid(df, unblind_codes or [])
    logger.info("  >> [collector] Appending %d finding(s) for: %s", n, id)

    new_issues = df.copy()

    # Rename desc_col -> "description" if needed
    if desc_col != "description":
        new_issues = new_issues.rename(columns={desc_col: "description"})

    # Keep only the three canonical columns
    keep = [c for c in ["subj_id", "vis_id", "description"] if c in new_issues.columns]
    new_issues = new_issues[keep].copy()

    # Ensure vis_id exists and is numeric
    if "vis_id" not in new_issues.columns:
        new_issues["vis_id"] = float("nan")
    else:
        new_issues["vis_id"] = pd.to_numeric(new_issues["vis_id"], errors="coerce")

    if not new_issues.empty:
        new_issues["id"]          = id
        new_issues["review"]      = "ANALYST"
        new_issues["subj_id"]     = new_issues["subj_id"].astype(str)
        new_issues["description"] = (
            new_issues["description"].astype(str).str[:200]
        )
    else:
        new_issues["id"]     = pd.Series(dtype="string")
        new_issues["review"] = pd.Series(dtype="string")

    # Reorder columns and deduplicate
    cols = ["id", "subj_id", "vis_id", "description", "review"]
    new_issues = new_issues[[c for c in cols if c in new_issues.columns]]
    new_issues = new_issues.drop_duplicates()

    # Append to master issues table
    state.issues = pd.concat(
        [state.issues, new_issues], ignore_index=True
    ).drop_duplicates()

    # Append to summary log
    log_row = pd.DataFrame([{
        "headlink": id,
        "nu":       int(n),
        "rule_set": id,
        "sobs":     "Y" if sobs else "N",
    }])
    state.summary_log = pd.concat(
        [state.summary_log, log_row], ignore_index=True
    )

    return state
