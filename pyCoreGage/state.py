"""
pyCoreGage.state
================
Core data structures for a pyCoreGage run.

CoreGageConfig  -- all path settings for a project (replaces project_config.R list)
CoreGageState   -- mutable run-time state passed through every function
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class CoreGageConfig:
    """
    All path settings for a pyCoreGage project.

    Parameters
    ----------
    project_name : str
        Human-readable project / trial identifier shown in console output.
    rule_registry : str
        Absolute path to rule_registry.xlsx.
    trial_checks : str
        Folder containing trial-level check scripts (AE.py, LB.py …).
    study_checks : str
        Folder containing study-level check scripts (AE_study.py …).
    inputs : str
        Folder where domain CSV / SAS files are dropped.
    reports : str
        Folder where Excel reports are written.
    feedback : str
        Root folder containing DM/, MW/, SDTM/, ADAM/ sub-folders.
    """

    project_name: str = "pyCoreGage Project"
    rule_registry: str = ""
    trial_checks: str = ""
    study_checks: str = ""
    inputs: str = ""
    reports: str = ""
    feedback: str = ""

    def validate(self) -> None:
        """Raise ValueError for any missing required path."""
        required = ["rule_registry", "trial_checks", "study_checks",
                    "inputs", "reports", "feedback"]
        for attr in required:
            val = getattr(self, attr)
            if not val:
                raise ValueError(
                    f"CoreGageConfig.{attr} must be set before running."
                )

    @classmethod
    def from_dict(cls, d: dict) -> "CoreGageConfig":
        """Build a config from a plain dictionary (e.g. from project_config.py)."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def _empty_issues() -> pd.DataFrame:
    return pd.DataFrame({
        "id":          pd.Series(dtype="string"),
        "subj_id":     pd.Series(dtype="string"),
        "vis_id":      pd.Series(dtype="float64"),
        "description": pd.Series(dtype="string"),
        "review":      pd.Series(dtype="string"),
    })


def _empty_summary_log() -> pd.DataFrame:
    return pd.DataFrame({
        "headlink": pd.Series(dtype="string"),
        "nu":       pd.Series(dtype="Int64"),
        "rule_set": pd.Series(dtype="string"),
        "sobs":     pd.Series(dtype="string"),
    })


def _empty_review_log() -> pd.DataFrame:
    return pd.DataFrame({
        "id":           pd.Series(dtype="string"),
        "subj_id":      pd.Series(dtype="string"),
        "vis_id":       pd.Series(dtype="float64"),
        "desrp":        pd.Series(dtype="string"),
        "find_dt":      pd.Series(dtype="object"),   # datetime.date
        "status":       pd.Series(dtype="string"),
        "analyst_note": pd.Series(dtype="string"),
        "analyst_id":   pd.Series(dtype="string"),
        "review_note":  pd.Series(dtype="string"),
        "reviewer_id":  pd.Series(dtype="string"),
        "last_mod":     pd.Series(dtype="object"),   # datetime
        "report_type":  pd.Series(dtype="string"),
    })


@dataclass
class CoreGageState:
    """
    Mutable state object passed through the entire pyCoreGage run.

    Attributes
    ----------
    rule_registry : pd.DataFrame
        Combined Trial + Study rows from rule_registry.xlsx.
    active_rules : Dict[str, bool]
        Mapping of check ID -> True/False (replaces R named logical vector).
    session : dict
        Run metadata: sdate (ddMMMYYYY string) and stime (HH:MM string).
    issues : pd.DataFrame
        Master findings table.  Columns: id, subj_id, vis_id, description, review.
    summary_log : pd.DataFrame
        One row per check call: headlink, nu, rule_set, sobs.
    review_log : pd.DataFrame
        Full audit trail (populated by reporter).
    domains : Dict[str, pd.DataFrame]
        Loaded domain data keyed by lowercase filename stem (e.g. "ae", "lb").
    """

    rule_registry: pd.DataFrame = field(default_factory=pd.DataFrame)
    active_rules:  Dict[str, bool] = field(default_factory=dict)
    session:       dict = field(default_factory=dict)
    issues:        pd.DataFrame = field(default_factory=_empty_issues)
    summary_log:   pd.DataFrame = field(default_factory=_empty_summary_log)
    review_log:    pd.DataFrame = field(default_factory=_empty_review_log)
    domains:       Dict[str, pd.DataFrame] = field(default_factory=dict)
