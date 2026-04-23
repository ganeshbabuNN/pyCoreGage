"""
LB.py — Trial-level Laboratory checks
Checks: LBCHK001 (out-of-range), LBCHK002 (missing date)
"""

import pandas as pd
from pyCoreGage import collect_findings


def check_LB(state, cfg):
    lb = state.domains.get("lb")
    if lb is None or lb.empty:
        return state

    active_rules = state.active_rules

    # ── LBCHK001 : Lab value outside normal reference range ──────────────────
    if active_rules.get("LBCHK001"):
        sub = lb.copy()
        sub["val"] = pd.to_numeric(sub["LBORRES"], errors="coerce")
        sub["lo"]  = pd.to_numeric(sub["LBNRLO"],  errors="coerce")
        sub["hi"]  = pd.to_numeric(sub["LBNRHI"],  errors="coerce")
        result = sub[
            sub["val"].notna() & sub["lo"].notna() & sub["hi"].notna() &
            ((sub["val"] < sub["lo"]) | (sub["val"] > sub["hi"]))
        ].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = pd.to_numeric(result["VISITNUM"], errors="coerce")
            result["description"] = (
                result["LBTEST"] + " = " + result["val"].astype(str) +
                " " + result["LBORRESU"].fillna("") +
                " outside [" + result["lo"].astype(str) +
                " – " + result["hi"].astype(str) + "]" +
                " at visit " + result["VISIT"].fillna("")
            )
            state = collect_findings(
                state,
                result[["subj_id", "vis_id", "description"]],
                id="LBCHK001",
            )

    # ── LBCHK002 : Missing lab collection date (LBDTC) ───────────────────────
    if active_rules.get("LBCHK002"):
        result = lb[lb["LBDTC"].isna()].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = pd.to_numeric(result["VISITNUM"], errors="coerce")
            result["description"] = "LBDTC missing for: " + result["LBTEST"].fillna("unknown")
            state = collect_findings(
                state,
                result[["subj_id", "vis_id", "description"]],
                id="LBCHK002",
            )

    return state
