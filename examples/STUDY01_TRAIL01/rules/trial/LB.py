"""LB.py — Laboratory Results — Trial-level checks
LBCHK001 : Lab value outside normal reference range
LBCHK002 : Missing lab result value (LBORRES)
LBCHK003 : Duplicate records for same subject/visit/test
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_LB(state, cfg):
    lb = state.domains.get("lb")
    if lb is None or lb.empty:
        print("  WARNING [LB]: domains['lb'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("LBCHK001"):
        sub = lb[
            lb["LBORRES"].notna() & (lb["LBORRES"].astype(str).str.strip() != "") &
            lb["LBNRLO"].notna()  & (lb["LBNRLO"].astype(str).str.strip()  != "") &
            lb["LBNRHI"].notna()  & (lb["LBNRHI"].astype(str).str.strip()  != "")
        ].copy()
        sub["val"] = pd.to_numeric(sub["LBORRES"], errors="coerce")
        sub["lo"]  = pd.to_numeric(sub["LBNRLO"],  errors="coerce")
        sub["hi"]  = pd.to_numeric(sub["LBNRHI"],  errors="coerce")
        res = sub[sub["val"].notna() & sub["lo"].notna() & sub["hi"].notna() &
                  ((sub["val"] < sub["lo"]) | (sub["val"] > sub["hi"]))].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            res["LBTEST"] + " (" + res["LBTESTCD"] + ") = " +
            res["val"].astype(str) + " " + res["LBORRESU"].fillna("") +
            " outside normal range [" + res["lo"].astype(str) +
            " - " + res["hi"].astype(str) + "] at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBCHK001")

    if r.get("LBCHK002"):
        res = lb[lb["LBORRES"].isna() | (lb["LBORRES"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Lab result (LBORRES) is missing for test " +
            res["LBTEST"] + " (" + res["LBTESTCD"] + ") at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBCHK002")

    if r.get("LBCHK003"):
        counts = lb.groupby(["USUBJID","VISITNUM","LBTESTCD"]).size().reset_index(name="_n")
        dups   = counts[counts["_n"] > 1][["USUBJID","VISITNUM","LBTESTCD"]]
        if not dups.empty:
            res = lb.merge(dups, on=["USUBJID","VISITNUM","LBTESTCD"])
            res = res.drop_duplicates(subset=["USUBJID","VISITNUM","LBTESTCD"]).copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Duplicate records for test " + res["LBTEST"] +
                " (" + res["LBTESTCD"] + ") at visit " + res["VISIT"] +
                " - more than one result recorded"
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBCHK003")

    return state
