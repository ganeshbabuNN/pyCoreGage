"""DM.py — Demographics — Trial-level checks
DMCHK001 : Missing sex (SEX)
DMCHK002 : Age outside inclusion criteria (18–80 years)
DMCHK003 : Missing reference start date (RFSTDTC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_DM(state, cfg):
    dm = state.domains.get("dm")
    if dm is None or dm.empty:
        print("  WARNING [DM]: domains['dm'] is empty - skipping.")
        return state
    r = state.active_rules

    #DMCHK001 : Missing sex (SEX)
    if r.get("DMCHK001"):
        res = dm[dm["SEX"].isna() | (dm["SEX"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Sex (SEX) is missing in the demographics record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMCHK001")
    
    #DMCHK002 : Age outside inclusion criteria (18–80 years)
    if r.get("DMCHK002"):
        sub = dm[dm["AGE"].notna() & (dm["AGE"].astype(str).str.strip() != "")].copy()
        sub["age_num"] = pd.to_numeric(sub["AGE"], errors="coerce")
        res = sub[sub["age_num"].notna() & ((sub["age_num"] < 18) | (sub["age_num"] > 80))].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Subject age (AGE=" + res["AGE"].astype(str) + " " +
            res["AGEU"].fillna("") + ")" +
            " is outside the inclusion criteria range of 18 to 80 years"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMCHK002")
    
    #DMCHK003 : Missing reference start date (RFSTDTC)
    if r.get("DMCHK003"):
        res = dm[dm["RFSTDTC"].isna() | (dm["RFSTDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Reference start date (RFSTDTC) is missing for the subject"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMCHK003")

    return state
