"""EX.py — Exposure — Trial-level checks
EXCHK001 : Exposure end date before start date
EXCHK002 : Missing dose amount (EXDOSE)
EXCHK003 : Missing route of administration (EXROUTE)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_EX(state, cfg):
    ex = state.domains.get("ex")
    if ex is None or ex.empty:
        print("  WARNING [EX]: domains['ex'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("EXCHK001"):
        sub = ex.dropna(subset=["EXSTDTC","EXENDTC"]).copy()
        sub = sub[(sub["EXSTDTC"].str.strip() != "") & (sub["EXENDTC"].str.strip() != "")]
        sub["st"] = pd.to_datetime(sub["EXSTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["EXENDTC"], errors="coerce")
        res = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Exposure end date (" + res["en"].dt.strftime("%d%b%Y") +
            ") is before start date (" + res["st"].dt.strftime("%d%b%Y") +
            ") for treatment: " + res["EXTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXCHK001")

    if r.get("EXCHK002"):
        res = ex[ex["EXDOSE"].isna() | (ex["EXDOSE"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose amount (EXDOSE) is missing for treatment: " +
            res["EXTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXCHK002")

    if r.get("EXCHK003"):
        res = ex[ex["EXROUTE"].isna() | (ex["EXROUTE"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Route of administration (EXROUTE) is missing for treatment: " +
            res["EXTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="EXCHK003")

    return state
