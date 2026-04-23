"""
LB_study.py — Study-level Laboratory checks (cross-domain / consistency)
Checks: LBPRJ001 (missing lab date)
"""

import pandas as pd
from pyCoreGage import collect_findings


def check_LB_study(state, cfg):
    lb = state.domains.get("lb")
    if lb is None or lb.empty:
        return state

    active_rules = state.active_rules

    # ── LBPRJ001 : Missing lab collection date (LBDTC) ───────────────────────
    if active_rules.get("LBPRJ001"):
        if "LBDTC" in lb.columns:
            result = lb[lb["LBDTC"].isna()].copy()
            if not result.empty:
                result["subj_id"]     = result["USUBJID"]
                result["vis_id"]      = pd.to_numeric(result["VISITNUM"], errors="coerce")
                result["description"] = (
                    "Study-level: LBDTC missing for " +
                    result["LBTEST"].fillna("unknown") +
                    " at visit " + result["VISIT"].fillna("unknown")
                )
                state = collect_findings(
                    state,
                    result[["subj_id", "vis_id", "description"]],
                    id="LBPRJ001",
                )

    return state
