"""AE_study.py — Adverse Events — Study-level checks
AEPRJ001 : Serious AE (AESER=Y) with missing action taken (AEACN)
AEPRJ002 : Dictionary coded term (AEDECOD) missing
AEPRJ003 : AE study day (AESTDY) missing
"""
from pyCoreGage import collect_findings


def check_AE_study(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        print("  WARNING [AE_study]: domains['ae'] is empty - skipping.")
        return state
    r = state.active_rules

    #AEPRJ001 : Serious AE (AESER=Y) with missing action taken (AEACN)
    if r.get("AEPRJ001"):
        res = ae[
            ae["AESER"].notna() & (ae["AESER"].astype(str).str.upper().str.strip() == "Y") &
            (ae["AEACN"].isna() | (ae["AEACN"].astype(str).str.strip() == ""))
        ].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Serious AE (AESER=Y) has no action taken (AEACN) for term: " +
            res["AETERM"] + " starting " + res["AESTDTC"].astype(str) +
            " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AEPRJ001")

    #AEPRJ002 : Dictionary coded term (AEDECOD) missing
    if r.get("AEPRJ002"):
        res = ae[ae["AEDECOD"].isna() | (ae["AEDECOD"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Dictionary coded term (AEDECOD) is missing for verbatim: " +
            res["AETERM"] + " starting " + res["AESTDTC"].astype(str) +
            " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AEPRJ002")

    #AEPRJ003 : AE study day (AESTDY) missing
    if r.get("AEPRJ003"):
        res = ae[ae["AESTDY"].isna() | (ae["AESTDY"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "AE study day (AESTDY) is missing for term: " +
            res["AETERM"] + " starting " + res["AESTDTC"].astype(str) +
            " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AEPRJ003")

    return state
