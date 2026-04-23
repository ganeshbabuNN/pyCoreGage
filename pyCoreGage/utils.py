"""
pyCoreGage.utils
================
load_inputs() — reads every CSV and (optionally) SAS7BDAT file from the
inputs/ folder into a dict of DataFrames.

cleanup_text() — internal helper to strip control characters from strings.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Dict

import pandas as pd

logger = logging.getLogger("pyCoreGage")


def load_inputs(cfg) -> Dict[str, pd.DataFrame]:
    """
    Load domain input data files from ``cfg.inputs``.

    Reads every ``.csv`` and (optionally) ``.sas7bdat`` file from the
    inputs folder into a named dictionary.  The key is the lowercase
    filename without extension (e.g. ``AE.csv`` → ``domains["ae"]``).

    Drop a new domain file into ``inputs/`` and it is picked up
    automatically on the next run — no code change required.

    Parameters
    ----------
    cfg : CoreGageConfig
        Project configuration.  ``cfg.inputs`` must point to a readable folder.

    Returns
    -------
    dict of str -> pd.DataFrame
        One entry per file found.

    Examples
    --------
    >>> from pyCoreGage import CoreGageConfig, load_inputs
    >>> import tempfile, os, pandas as pd
    >>> tmp = tempfile.mkdtemp()
    >>> pd.DataFrame({"USUBJID": ["S1"], "AETERM": ["Rash"]}).to_csv(
    ...     os.path.join(tmp, "AE.csv"), index=False)
    >>> cfg = CoreGageConfig(inputs=tmp)
    >>> domains = load_inputs(cfg)
    >>> list(domains.keys())
    ['ae']
    """
    data_dir = cfg.inputs
    if not os.path.isdir(data_dir):
        logger.warning("inputs/ folder not found at: %s", data_dir)
        return {}

    domains: Dict[str, pd.DataFrame] = {}

    # ── CSV files ────────────────────────────────────────────────────────────
    csv_files = sorted(
        Path(data_dir).glob("*.csv"),
        key=lambda p: p.name.lower(),
    )
    # Also pick up upper-case .CSV
    csv_files_upper = sorted(
        Path(data_dir).glob("*.CSV"),
        key=lambda p: p.name.lower(),
    )
    # Merge and deduplicate by resolved path
    all_csv = {str(p.resolve()): p for p in csv_files + csv_files_upper}

    for fpath in sorted(all_csv.values(), key=lambda p: p.name.lower()):
        stem = fpath.stem.lower()
        try:
            df = pd.read_csv(
                fpath,
                dtype=str,
                keep_default_na=False,
                na_values=["", "NA"],
            )
            domains[stem] = df
            logger.info(
                "   %s -> domains['%s']  (%d rows)", fpath.name, stem, len(df)
            )
        except Exception as exc:
            logger.warning("   Could not read %s: %s", fpath.name, exc)

    # ── SAS7BDAT files ───────────────────────────────────────────────────────
    sas_files = sorted(Path(data_dir).glob("*.sas7bdat"))
    if sas_files:
        try:
            import pyreadstat  # optional dependency
            for fpath in sas_files:
                stem = fpath.stem.lower()
                try:
                    df, _ = pyreadstat.read_sas7bdat(str(fpath))
                    domains[stem] = df
                    logger.info(
                        "   %s -> domains['%s']  (%d rows)",
                        fpath.name, stem, len(df),
                    )
                except Exception as exc:
                    logger.warning("   Could not read %s: %s", fpath.name, exc)
        except ImportError:
            logger.warning(
                ".sas7bdat files found but 'pyreadstat' is not installed. "
                "Run: pip install pyreadstat"
            )

    if not domains:
        logger.warning(
            "No data files found in: %s. "
            "Drop .csv or .sas7bdat files into inputs/ and re-run.",
            data_dir,
        )

    return domains


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

_CTRL_STRIP = re.compile(r"[\x01-\x09\x0b\x0e-\x1f]")
_CTRL_SPACE = re.compile(r"[\x0a\x0c\x0d]")
_MULTI_SPACE = re.compile(r"\s+")


def cleanup_text(x: str) -> str:
    """
    Remove control characters and collapse whitespace in a string.

    Parameters
    ----------
    x : str
        Input text.

    Returns
    -------
    str
        Cleaned text with control characters removed, newlines replaced
        by spaces, and multiple spaces collapsed to one.

    Examples
    --------
    >>> from pyCoreGage.utils import cleanup_text
    >>> cleanup_text("Hello\\nWorld   ")
    'Hello World'
    """
    if not isinstance(x, str):
        x = "" if (x is None or (isinstance(x, float) and x != x)) else str(x)
    x = _CTRL_STRIP.sub("", x)
    x = _CTRL_SPACE.sub(" ", x)
    x = _MULTI_SPACE.sub(" ", x)
    return x.strip()
