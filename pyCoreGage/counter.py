"""
pyCoreGage.counter
==================
count_valid() — counts observations in a findings DataFrame,
optionally excluding rows that could unblind the study.
"""

from __future__ import annotations

from typing import List

import pandas as pd


def count_valid(df: pd.DataFrame, unblind_codes: List[str] = None) -> int:
    """
    Count valid rows in a findings DataFrame.

    Rows with a negative subject ID (``subj_id`` starting with ``"-"``)
    are excluded when *none* of the ``unblind_codes`` appear in the
    ``description`` column.  This prevents accidental unblinding.

    Parameters
    ----------
    df : pd.DataFrame
        Findings DataFrame with at least ``subj_id`` and ``description``.
    unblind_codes : list of str, optional
        Topic codes whose presence exempts a negative-ID row from exclusion.
        Pass an empty list or ``None`` to skip unblinding filtering.

    Returns
    -------
    int
        Number of valid rows.

    Examples
    --------
    >>> import pandas as pd
    >>> from pyCoreGage import count_valid
    >>> df = pd.DataFrame({
    ...     "subj_id":     ["001", "-002"],
    ...     "description": ["Issue A", "Issue B"],
    ... })
    >>> count_valid(df)
    2
    >>> count_valid(df, unblind_codes=["TOPIC_X"])
    1
    """
    if df is None or df.empty:
        return 0

    if unblind_codes and "subj_id" in df.columns and "description" in df.columns:
        subj_str = df["subj_id"].astype(str)
        is_negative = subj_str.str.startswith("-")

        def _has_code(desc: str) -> bool:
            desc = str(desc)
            return any(code in desc for code in unblind_codes)

        has_code = df["description"].apply(_has_code)
        # Exclude rows that are negative AND do NOT contain any unblind code
        df = df[~(is_negative & ~has_code)]

    return len(df)
