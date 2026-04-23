"""SV_study.py — Subject Visits — Study-level checks
SVPRJ001 : Missing visit description (SVUPDES)
SVPRJ002 : Duplicate visit records for same subject and visit number
SVPRJ003 : Visit date outside expected study window (after 2026-01-01)
"""
import pandas as pd
from datetime import date
from pyCoreGage import collect_findings

STUDY_END_DATE = date(2026, 1, 1)


def check_SV_study(state, cfg):
    sv = state.domains.get("sv")
    if sv is None or sv.empty:
        print("  WARNING [SV_study]: domains['sv'] is empty - skipping.")
        return state
    r = state.active_rules

    #SVPRJ001 : Missing visit description (SVUPDES)
    if r.get("SVPRJ001"):
        if "SVUPDES" not in sv.columns:
            print("  NOTE: SVUPDES column not found - skipping SVPRJ001.")
        else:
            res = sv[sv["SVUPDES"].isna() | (sv["SVUPDES"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Visit description (SVUPDES) is missing for visit: " +
                res["VISIT"] + " (VISITNUM=" + res["VISITNUM"].astype(str) + ")"
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVPRJ001")

    #SVPRJ002 : Duplicate visit records for same subject and visit number
    if r.get("SVPRJ002"):
        counts = sv.groupby(["USUBJID","VISITNUM"]).size().reset_index(name="_n")
        dups   = counts[counts["_n"] > 1][["USUBJID","VISITNUM"]]
        if not dups.empty:
            res = sv.merge(dups, on=["USUBJID","VISITNUM"])
            res = res.drop_duplicates(subset=["USUBJID","VISITNUM"]).copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Duplicate visit records found for visit: " + res["VISIT"] +
                " (VISITNUM=" + res["VISITNUM"].astype(str) +
                ") - more than one record exists for this subject and visit"
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVPRJ002")

    #SVPRJ003 : Visit date outside expected study window (after 2026-01-01)
    if r.get("SVPRJ003"):
        sub = sv[sv["SVSTDTC"].notna() & (sv["SVSTDTC"].astype(str).str.strip() != "")].copy()
        sub["sv_dt"] = pd.to_datetime(sub["SVSTDTC"], errors="coerce").dt.date
        res = sub[sub["sv_dt"].notna() & (sub["sv_dt"] > STUDY_END_DATE)].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Visit date (SVSTDTC=" +
            res["sv_dt"].apply(lambda d: d.strftime("%d%b%Y") if d else "") +
            ") is after the expected study end date (" +
            STUDY_END_DATE.strftime("%d%b%Y") + ") for visit: " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVPRJ003")

    return state
