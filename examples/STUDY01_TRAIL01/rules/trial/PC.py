"""PC.py — Pharmacokinetics Concentrations — Trial-level checks
PCCHK001 : Missing concentration result (PCORRES)
PCCHK002 : Negative concentration value
PCCHK003 : Missing sample collection date (PCDTC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_PC(state, cfg):
    pc = state.domains.get("pc")
    if pc is None or pc.empty:
        print("  WARNING [PC]: domains['pc'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("PCCHK001"):
        res = pc[pc["PCORRES"].isna() | (pc["PCORRES"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Concentration result (PCORRES) is missing for test: " +
            res["PCTESTCD"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCCHK001")

    if r.get("PCCHK002"):
        sub = pc[pc["PCORRES"].notna() & (pc["PCORRES"].astype(str).str.strip() != "")].copy()
        sub["val"] = pd.to_numeric(sub["PCORRES"], errors="coerce")
        res = sub[sub["val"].notna() & (sub["val"] < 0)].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Concentration value (PCORRES=" + res["PCORRES"].astype(str) +
            ") is negative for test: " + res["PCTESTCD"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCCHK002")

    if r.get("PCCHK003"):
        res = pc[pc["PCDTC"].isna() | (pc["PCDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Sample collection date (PCDTC) is missing for test: " +
            res["PCTESTCD"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PCCHK003")

    return state
