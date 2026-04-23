"""CM.py — Concomitant Medications — Trial-level checks
CMCHK001 : CM end date before start date
CMCHK002 : Missing medication name (CMTRT)
CMCHK003 : Missing indication (CMINDC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_CM(state, cfg):
    cm = state.domains.get("cm")
    if cm is None or cm.empty:
        print("  WARNING [CM]: domains['cm'] is empty - skipping.")
        return state
    r = state.active_rules

    #CMCHK001 : CM end date before start date
    if r.get("CMCHK001"):
        sub = cm.dropna(subset=["CMSTDTC","CMENDTC"]).copy()
        sub = sub[sub["CMSTDTC"].str.strip() != ""][sub["CMENDTC"].str.strip() != ""]
        sub["st"] = pd.to_datetime(sub["CMSTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["CMENDTC"], errors="coerce")
        res = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "CM end date (" + res["en"].dt.strftime("%d%b%Y") +
            ") is before start date (" + res["st"].dt.strftime("%d%b%Y") +
            ") for medication: " + res["CMTRT"].fillna("[CMTRT missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMCHK001")
    
    #CMCHK002 : Missing medication name (CMTRT)
    if r.get("CMCHK002"):
        res = cm[cm["CMTRT"].isna() | (cm["CMTRT"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Medication name (CMTRT) is missing in the concomitant medication record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMCHK002")

    #CMCHK003 : Missing indication (CMINDC)
    if r.get("CMCHK003"):
        res = cm[cm["CMINDC"].isna() | (cm["CMINDC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Indication (CMINDC) is missing for medication: " +
            res["CMTRT"].fillna("[CMTRT missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="CMCHK003")

    return state
