"""VS_study.py — Vital Signs — Study-level checks
VSPRJ001 : Missing vital sign collection date (VSDTC)
VSPRJ002 : Duplicate vital sign records same subject/visit/test
VSPRJ003 : Invalid position (VSPOS) value
"""
import pandas as pd
from pyCoreGage import collect_findings

ALLOWED_POS = {"STANDING", "SITTING", "SUPINE", "PRONE", "ORIGINAL"}


def check_VS_study(state, cfg):
    vs = state.domains.get("vs")
    if vs is None or vs.empty:
        print("  WARNING [VS_study]: domains['vs'] is empty - skipping.")
        return state
    r = state.active_rules

    #VSPRJ001 : Missing vital sign collection date (VSDTC)
    if r.get("VSPRJ001"):
        res = vs[vs["VSDTC"].isna() | (vs["VSDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Collection date (VSDTC) is missing for test: " +
            res["VSTEST"] + " (" + res["VSTESTCD"] + ") at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSPRJ001")

    #VSPRJ002 : Duplicate vital sign records same subject/visit/test
    if r.get("VSPRJ002"):
        counts = vs.groupby(["USUBJID","VISITNUM","VSTESTCD"]).size().reset_index(name="_n")
        dups   = counts[counts["_n"] > 1][["USUBJID","VISITNUM","VSTESTCD"]]
        if not dups.empty:
            res = vs.merge(dups, on=["USUBJID","VISITNUM","VSTESTCD"])
            res = res.drop_duplicates(subset=["USUBJID","VISITNUM","VSTESTCD"]).copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Duplicate vital sign records for " + res["VSTEST"] +
                " (" + res["VSTESTCD"] + ") at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSPRJ002")

    #VSPRJ003 : Invalid position (VSPOS) value
    if r.get("VSPRJ003"):
        if "VSPOS" not in vs.columns:
            print("  NOTE: VSPOS column not found - skipping VSPRJ003.")
        else:
            sub = vs[vs["VSPOS"].notna() & (vs["VSPOS"].astype(str).str.strip() != "")].copy()
            res = sub[~sub["VSPOS"].str.upper().str.strip().isin(ALLOWED_POS)].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Position value '" + res["VSPOS"] +
                "' is not in allowed list (" + "/".join(sorted(ALLOWED_POS)) + ")" +
                " for test: " + res["VSTEST"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="VSPRJ003")

    return state
