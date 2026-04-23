"""LB_study.py — Laboratory Results — Study-level checks
LBPRJ001 : Missing lab collection date (LBDTC)
LBPRJ002 : Inconsistent analysis method across sites for same test
LBPRJ003 : Specimen condition not in allowed list
"""
import pandas as pd
from pyCoreGage import collect_findings

ALLOWED_COND = {"ORIGINAL", "RECOLLECT"}


def check_LB_study(state, cfg):
    lb = state.domains.get("lb")
    if lb is None or lb.empty:
        print("  WARNING [LB_study]: domains['lb'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("LBPRJ001"):
        res = lb[lb["LBDTC"].isna() | (lb["LBDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Lab collection date (LBDTC) is missing for test " +
            res["LBTEST"] + " (" + res["LBTESTCD"] + ") at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBPRJ001")

    if r.get("LBPRJ002"):
        if "LBMETHOD" not in lb.columns:
            print("  NOTE: LBMETHOD column not found - skipping LBPRJ002.")
        else:
            sub = lb[lb["LBMETHOD"].notna() & (lb["LBMETHOD"].astype(str).str.strip() != "")].copy()
            method_check = (
                sub.groupby(["VISITNUM","LBTESTCD"])["LBMETHOD"]
                .nunique().reset_index(name="n_methods")
            )
            method_check = method_check[method_check["n_methods"] > 1]
            if not method_check.empty:
                method_labels = (
                    sub.groupby(["VISITNUM","LBTESTCD"])["LBMETHOD"]
                    .apply(lambda x: " / ".join(sorted(x.unique())))
                    .reset_index(name="methods")
                )
                multi = method_check.merge(method_labels, on=["VISITNUM","LBTESTCD"])
                res = lb.merge(multi[["VISITNUM","LBTESTCD","methods"]], on=["VISITNUM","LBTESTCD"])
                res = res.drop_duplicates(subset=["USUBJID","VISITNUM","LBTESTCD"]).copy()
                res["subj_id"] = res["USUBJID"]
                res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
                res["description"] = (
                    "Inconsistent analysis method for " + res["LBTEST"] +
                    " (" + res["LBTESTCD"] + ") at visit " + res["VISIT"] +
                    " - methods used: " + res["methods"]
                )
                state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBPRJ002")

    if r.get("LBPRJ003"):
        if "LBSPCCND" not in lb.columns:
            print("  NOTE: LBSPCCND column not found - skipping LBPRJ003.")
        else:
            sub = lb[lb["LBSPCCND"].notna() & (lb["LBSPCCND"].astype(str).str.strip() != "")].copy()
            res = sub[~sub["LBSPCCND"].str.upper().str.strip().isin(ALLOWED_COND)].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Specimen condition '" + res["LBSPCCND"] +
                "' not in allowed list (" + "/".join(sorted(ALLOWED_COND)) + ")" +
                " for test " + res["LBTEST"] + " (" + res["LBTESTCD"] + ") at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="LBPRJ003")

    return state
