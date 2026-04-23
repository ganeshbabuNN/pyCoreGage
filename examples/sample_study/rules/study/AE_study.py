"""
AE_study.py — Study-level Adverse Events checks (cross-domain)
Checks: AEPRJ001 (SAE missing action), AEPRJ002 (missing coded term)
"""

import pandas as pd
from pyCoreGage import collect_findings


def check_AE_study(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        return state

    active_rules = state.active_rules

    # ── AEPRJ001 : Serious AE missing action taken ────────────────────────────
    if active_rules.get("AEPRJ001"):
        if "AESERY" in ae.columns and "AEACN" in ae.columns:
            result = ae[
                (ae["AESERY"].astype(str).str.upper() == "Y") & ae["AEACN"].isna()
            ].copy()
            if not result.empty:
                result["subj_id"]     = result["USUBJID"]
                result["vis_id"]      = float("nan")
                result["description"] = (
                    "Serious AE '" + result["AETERM"].fillna("unknown") +
                    "' has no action taken (AEACN missing)"
                )
                state = collect_findings(
                    state,
                    result[["subj_id", "vis_id", "description"]],
                    id="AEPRJ001",
                )

    # ── AEPRJ002 : Missing dictionary coded term (AEDECOD) ────────────────────
    if active_rules.get("AEPRJ002"):
        if "AEDECOD" in ae.columns:
            result = ae[ae["AEDECOD"].isna()].copy()
            if not result.empty:
                result["subj_id"]     = result["USUBJID"]
                result["vis_id"]      = float("nan")
                result["description"] = (
                    "AEDECOD missing for verbatim term: " +
                    result["AETERM"].fillna("unknown")
                )
                state = collect_findings(
                    state,
                    result[["subj_id", "vis_id", "description"]],
                    id="AEPRJ002",
                )

    return state
