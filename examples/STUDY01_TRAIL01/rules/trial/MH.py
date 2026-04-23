"""MH.py — Medical History — Trial-level checks
MHCHK001 : Missing medical history term (MHTERM)
MHCHK002 : Medical history end date before start date
MHCHK003 : Missing onset date (MHSTDTC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_MH(state, cfg):
    mh = state.domains.get("mh")
    if mh is None or mh.empty:
        print("  WARNING [MH]: domains['mh'] is empty - skipping.")
        return state
    r = state.active_rules

    #MHCHK001 : Missing medical history term (MHTERM)
    if r.get("MHCHK001"):
        res = mh[mh["MHTERM"].isna() | (mh["MHTERM"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Medical history term (MHTERM) is missing in the medical history record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHCHK001")

    #MHCHK002 : Medical history end date before start date
    if r.get("MHCHK002"):
        sub = mh.dropna(subset=["MHSTDTC","MHENDTC"]).copy()
        sub = sub[(sub["MHSTDTC"].str.strip() != "") & (sub["MHENDTC"].str.strip() != "")]
        sub["st"] = pd.to_datetime(sub["MHSTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["MHENDTC"], errors="coerce")
        res = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Medical history end date (" + res["en"].dt.strftime("%d%b%Y") +
            ") is before onset date (" + res["st"].dt.strftime("%d%b%Y") +
            ") for condition: " + res["MHTERM"].fillna("[MHTERM missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHCHK002")

    #MHCHK003 : Missing onset date (MHSTDTC)
    if r.get("MHCHK003"):
        res = mh[mh["MHSTDTC"].isna() | (mh["MHSTDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Onset date (MHSTDTC) is missing for condition: " +
            res["MHTERM"].fillna("[MHTERM missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHCHK003")

    return state
