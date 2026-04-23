"""AE.py — Adverse Events — Trial-level checks
AECHK001 : AE end date before start date
AECHK002 : Missing AE severity (AESEV)
AECHK003 : Missing AE outcome (AEOUT)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_AE(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        print("  WARNING [AE]: domains['ae'] is empty - skipping.")
        return state
    r = state.active_rules

    ###AECHK001 : AE end date before start date
    if r.get("AECHK001"):
        sub = ae.dropna(subset=["AESTDTC", "AEENDTC"]).copy()
        sub = sub[sub["AESTDTC"].str.strip() != ""]
        sub = sub[sub["AEENDTC"].str.strip() != ""]
        sub["st"] = pd.to_datetime(sub["AESTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["AEENDTC"], errors="coerce")
        res = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = float("nan")
        res["description"] = (
            "AE end date (" + res["en"].dt.strftime("%d%b%Y") +
            ") is before start date (" + res["st"].dt.strftime("%d%b%Y") +
            ") for term: " + res["AETERM"] + " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AECHK001")

    ###AECHK002 : Missing AE severity (AESEV)
    if r.get("AECHK002"):
        res = ae[ae["AESEV"].isna() | (ae["AESEV"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = float("nan")
        res["description"] = (
            "AE severity (AESEV) is missing for term: " + res["AETERM"] +
            " starting " + res["AESTDTC"].astype(str) +
            " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AECHK002")

    
    ###AECHK003 : Missing AE outcome (AEOUT)
    if r.get("AECHK003"):
        res = ae[ae["AEOUT"].isna() | (ae["AEOUT"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = float("nan")
        res["description"] = (
            "AE outcome (AEOUT) is missing for term: " + res["AETERM"] +
            " starting " + res["AESTDTC"].astype(str) +
            " (AESEQ=" + res["AESEQ"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="AECHK003")

    return state
