"""PC_study.py — Pharmacokinetics Concentrations — Study-level checks
PCPRJ001 : Missing specimen type (PCSPEC)
PCPRJ002 : Missing concentration units (PCSTRESU)
PCPRJ003 : Duplicate records for same subject, visit, and test
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_PC_study(state, cfg):
    pc = state.domains.get("pc")
    if pc is None or pc.empty:
        print("  WARNING [PC_study]: domains['pc'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("PCPRJ001"):
        if "PCSPEC" not in pc.columns:
            print("  NOTE: PCSPEC column not found - skipping PCPRJ001.")
        else:
            res = pc[pc["PCSPEC"].isna() | (pc["PCSPEC"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Specimen type (PCSPEC) is missing for test: " +
                res["PCTESTCD"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCPRJ001")

    if r.get("PCPRJ002"):
        if "PCSTRESU" not in pc.columns:
            print("  NOTE: PCSTRESU column not found - skipping PCPRJ002.")
        else:
            sub = pc[pc["PCORRES"].notna() & (pc["PCORRES"].astype(str).str.strip() != "")].copy()
            res = sub[sub["PCSTRESU"].isna() | (sub["PCSTRESU"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Concentration units (PCSTRESU) are missing although result (PCORRES=" +
                res["PCORRES"].astype(str) + ") is present for test: " + res["PCTESTCD"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCPRJ002")

    if r.get("PCPRJ003"):
        counts = pc.groupby(["USUBJID","VISITNUM","PCTESTCD"]).size().reset_index(name="_n")
        dups   = counts[counts["_n"] > 1][["USUBJID","VISITNUM","PCTESTCD"]]
        if not dups.empty:
            res = pc.merge(dups, on=["USUBJID","VISITNUM","PCTESTCD"])
            res = res.drop_duplicates(subset=["USUBJID","VISITNUM","PCTESTCD"]).copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Duplicate records found for test: " + res["PCTESTCD"] +
                " at visit " + res["VISIT"] + " - more than one result recorded"
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCPRJ003")

    return state
