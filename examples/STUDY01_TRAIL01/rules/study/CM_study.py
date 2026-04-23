"""CM_study.py — Concomitant Medications — Study-level checks
CMPRJ001 : Missing route of administration (CMROUTE)
CMPRJ002 : Missing dictionary coded term (CMDECOD)
CMPRJ003 : Ongoing medication missing end flag (CMENRTPT)
"""
from pyCoreGage import collect_findings


def check_CM_study(state, cfg):
    cm = state.domains.get("cm")
    if cm is None or cm.empty:
        print("  WARNING [CM_study]: domains['cm'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("CMPRJ001"):
        res = cm[cm["CMROUTE"].isna() | (cm["CMROUTE"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Route of administration (CMROUTE) is missing for medication: " +
            res["CMTRT"].fillna("[CMTRT missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMPRJ001")

    if r.get("CMPRJ002"):
        sub = cm[cm["CMTRT"].notna() & (cm["CMTRT"].astype(str).str.strip() != "")].copy()
        res = sub[sub["CMDECOD"].isna() | (sub["CMDECOD"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Dictionary coded term (CMDECOD) is missing for medication: " + res["CMTRT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMPRJ002")

    if r.get("CMPRJ003"):
        if "CMENRTPT" not in cm.columns:
            print("  NOTE: CMENRTPT column not found - skipping CMPRJ003.")
        else:
            res = cm[
                (cm["CMENDTC"].isna() | (cm["CMENDTC"].astype(str).str.strip() == "")) &
                (cm["CMENRTPT"].isna() | (cm["CMENRTPT"].astype(str).str.strip() == ""))
            ].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Ongoing medication has no end date and CMENRTPT is also missing for: " +
                res["CMTRT"].fillna("[CMTRT missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMPRJ003")

    return state
