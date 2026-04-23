"""VS.py — Vital Signs — Trial-level checks
VSCHK001 : Systolic BP not greater than diastolic BP
VSCHK002 : Missing vital sign result (VSORRES)
VSCHK003 : Vital sign value outside normal reference range
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_VS(state, cfg):
    vs = state.domains.get("vs")
    if vs is None or vs.empty:
        print("  WARNING [VS]: domains['vs'] is empty - skipping.")
        return state
    r = state.active_rules

    #VSCHK001 : Systolic BP not greater than diastolic BP
    if r.get("VSCHK001"):
        sysbp = vs[
            (vs["VSTESTCD"] == "SYSBP") &
            vs["VSORRES"].notna() & (vs["VSORRES"].astype(str).str.strip() != "")
        ][["USUBJID","VISITNUM","VISIT","VSDTC","VSORRES"]].rename(columns={"VSORRES":"sysbp"})

        diabp = vs[
            (vs["VSTESTCD"] == "DIABP") &
            vs["VSORRES"].notna() & (vs["VSORRES"].astype(str).str.strip() != "")
        ][["USUBJID","VISITNUM","VISIT","VSDTC","VSORRES"]].rename(columns={"VSORRES":"diabp"})

        merged = sysbp.merge(diabp, on=["USUBJID","VISITNUM","VISIT","VSDTC"])
        merged["s"] = pd.to_numeric(merged["sysbp"], errors="coerce")
        merged["d"] = pd.to_numeric(merged["diabp"],  errors="coerce")
        res = merged[merged["s"].notna() & merged["d"].notna() & (merged["s"] <= merged["d"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Systolic BP (" + res["sysbp"].astype(str) +
            " mmHg) is not greater than diastolic BP (" +
            res["diabp"].astype(str) + " mmHg) at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSCHK001")

    #VSCHK002 : Missing vital sign result (VSORRES)
    if r.get("VSCHK002"):
        res = vs[vs["VSORRES"].isna() | (vs["VSORRES"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Vital sign result (VSORRES) is missing for test: " +
            res["VSTEST"] + " (" + res["VSTESTCD"] + ") at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSCHK002")

    #VSCHK003 : Vital sign value outside normal reference range
    if r.get("VSCHK003"):
        sub = vs[
            vs["VSORRES"].notna()  & (vs["VSORRES"].astype(str).str.strip()  != "") &
            vs["VSSTNRLO"].notna() & (vs["VSSTNRLO"].astype(str).str.strip() != "") &
            vs["VSSTNRHI"].notna() & (vs["VSSTNRHI"].astype(str).str.strip() != "")
        ].copy()
        sub["val"] = pd.to_numeric(sub["VSORRES"],  errors="coerce")
        sub["lo"]  = pd.to_numeric(sub["VSSTNRLO"], errors="coerce")
        sub["hi"]  = pd.to_numeric(sub["VSSTNRHI"], errors="coerce")
        res = sub[sub["val"].notna() & sub["lo"].notna() & sub["hi"].notna() &
                  ((sub["val"] < sub["lo"]) | (sub["val"] > sub["hi"]))].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            res["VSTEST"] + " (" + res["VSTESTCD"] + ") = " +
            res["val"].astype(str) + " " + res["VSORRESU"].fillna("") +
            " outside normal range [" + res["lo"].astype(str) +
            " - " + res["hi"].astype(str) + "] at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSCHK003")

    return state
