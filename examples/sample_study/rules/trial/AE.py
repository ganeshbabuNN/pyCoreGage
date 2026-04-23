"""
AE.py — Trial-level Adverse Events checks
Checks: AECHK001 (date), AECHK002 (severity), AECHK003 (outcome)
"""

import pandas as pd
from pyCoreGage import collect_findings


def check_AE(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        return state

    active_rules = state.active_rules

    # ── AECHK001 : AE end date before start date ─────────────────────────────
    if active_rules.get("AECHK001"):
        mask = ae["AESTDTC"].notna() & ae["AEENDTC"].notna()
        sub  = ae[mask].copy()
        sub["st"] = pd.to_datetime(sub["AESTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["AEENDTC"], errors="coerce")
        result = sub[(sub["en"].notna()) & (sub["st"].notna()) & (sub["en"] < sub["st"])].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = float("nan")
            result["description"] = (
                "End (" + result["en"].dt.strftime("%d%b%Y") +
                ") before start (" + result["st"].dt.strftime("%d%b%Y") +
                ") for: " + result["AETERM"]
            )
            state = collect_findings(
                state,
                result[["subj_id", "vis_id", "description"]],
                id="AECHK001",
            )

    # ── AECHK002 : Missing AE severity (AESEV) ───────────────────────────────
    if active_rules.get("AECHK002"):
        result = ae[ae["AESEV"].isna()].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = float("nan")
            result["description"] = "AESEV missing for: " + result["AETERM"].fillna("unknown")
            state = collect_findings(
                state,
                result[["subj_id", "vis_id", "description"]],
                id="AECHK002",
            )

    # ── AECHK003 : Missing AE outcome (AEOUT) ────────────────────────────────
    if active_rules.get("AECHK003"):
        result = ae[ae["AEOUT"].isna()].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = float("nan")
            result["description"] = "AEOUT missing for: " + result["AETERM"].fillna("unknown")
            state = collect_findings(
                state,
                result[["subj_id", "vis_id", "description"]],
                id="AECHK003",
            )

    return state
