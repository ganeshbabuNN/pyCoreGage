"""EX_study.py — Exposure — Study-level checks
EXPRJ001 : Invalid dose form — not in allowed list (TABLET/CAPSULE)
EXPRJ002 : Administered dose exceeds protocol maximum (40 mg)
EXPRJ003 : Missing administration status (EXSTAT)
"""
import pandas as pd
from pyCoreGage import collect_findings

ALLOWED_FORMS = {"TABLET", "CAPSULE"}
MAX_DOSE_MG   = 40


def check_EX_study(state, cfg):
    ex = state.domains.get("ex")
    if ex is None or ex.empty:
        print("  WARNING [EX_study]: domains['ex'] is empty - skipping.")
        return state
    r = state.active_rules

    #EXPRJ001 : Invalid dose form — not in allowed list (TABLET/CAPSULE)
    if r.get("EXPRJ001"):
        if "EXDOSFRM" not in ex.columns:
            print("  NOTE: EXDOSFRM column not found - skipping EXPRJ001.")
        else:
            sub = ex[ex["EXDOSFRM"].notna() & (ex["EXDOSFRM"].astype(str).str.strip() != "")].copy()
            res = sub[~sub["EXDOSFRM"].str.upper().str.strip().isin(ALLOWED_FORMS)].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Dose form '" + res["EXDOSFRM"] +
                "' not in allowed list (" + "/".join(sorted(ALLOWED_FORMS)) +
                ") for treatment: " + res["EXTRT"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXPRJ001")

    #EXPRJ002 : Administered dose exceeds protocol maximum (40 mg)
    if r.get("EXPRJ002"):
        sub = ex[ex["EXDOSE"].notna() & (ex["EXDOSE"].astype(str).str.strip() != "")].copy()
        sub["dose_num"] = pd.to_numeric(sub["EXDOSE"], errors="coerce")
        res = sub[sub["dose_num"].notna() & (sub["dose_num"] > MAX_DOSE_MG)].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose (EXDOSE=" + res["EXDOSE"].astype(str) + " " + res["EXDOSU"].fillna("") +
            ") exceeds protocol maximum of " + str(MAX_DOSE_MG) +
            " mg for treatment: " + res["EXTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXPRJ002")

    #EXPRJ003 : Missing administration status (EXSTAT)
    if r.get("EXPRJ003"):
        if "EXSTAT" not in ex.columns:
            print("  NOTE: EXSTAT column not found - skipping EXPRJ003.")
        else:
            res = ex[ex["EXSTAT"].isna() | (ex["EXSTAT"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Administration status (EXSTAT) is missing for treatment: " +
                res["EXTRT"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXPRJ003")

    return state
