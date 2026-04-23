"""EC_study.py — Exposure as Collected — Study-level checks
ECPRJ001 : ECOCCUR occurrence flag missing
ECPRJ002 : Dose exceeds protocol maximum (40 mg)
ECPRJ003 : Reason not provided when ECOCCUR = N
"""
import pandas as pd
from pyCoreGage import collect_findings

MAX_DOSE_MG = 40


def check_EC_study(state, cfg):
    ec = state.domains.get("ec")
    if ec is None or ec.empty:
        print("  WARNING [EC_study]: domains['ec'] is empty - skipping.")
        return state
    r = state.active_rules

    #ECPRJ001 : ECOCCUR occurrence flag missing
    if r.get("ECPRJ001"):
        if "ECOCCUR" not in ec.columns:
            print("  NOTE: ECOCCUR column not found - skipping ECPRJ001.")
        else:
            res = ec[ec["ECOCCUR"].isna() | (ec["ECOCCUR"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Occurrence flag (ECOCCUR) is missing for treatment: " +
                res["ECTRT"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECPRJ001")

    #ECPRJ002 : Dose exceeds protocol maximum (40 mg)
    if r.get("ECPRJ002"):
        sub = ec[ec["ECDOSE"].notna() & (ec["ECDOSE"].astype(str).str.strip() != "")].copy()
        sub["dose_num"] = pd.to_numeric(sub["ECDOSE"], errors="coerce")
        res = sub[sub["dose_num"].notna() & (sub["dose_num"] > MAX_DOSE_MG)].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose (ECDOSE=" + res["ECDOSE"].astype(str) + " " + res["ECDOSU"].fillna("") +
            ") exceeds protocol maximum of " + str(MAX_DOSE_MG) +
            " mg for treatment: " + res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECPRJ002")

    #ECPRJ003 : Reason not provided when ECOCCUR = N
    if r.get("ECPRJ003"):
        if not all(c in ec.columns for c in ["ECOCCUR","ECREASND"]):
            print("  NOTE: ECOCCUR or ECREASND column not found - skipping ECPRJ003.")
        else:
            res = ec[
                ec["ECOCCUR"].notna() &
                (ec["ECOCCUR"].astype(str).str.upper().str.strip() == "N") &
                (ec["ECREASND"].isna() | (ec["ECREASND"].astype(str).str.strip() == ""))
            ].copy()
            res["subj_id"] = res["USUBJID"]
            res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
            res["description"] = (
                "Treatment not given (ECOCCUR=N) but reason (ECREASND) is missing" +
                " for treatment: " + res["ECTRT"] + " at visit " + res["VISIT"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECPRJ003")

    return state
