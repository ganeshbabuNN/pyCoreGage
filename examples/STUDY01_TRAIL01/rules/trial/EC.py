"""EC.py — Exposure as Collected — Trial-level checks
ECCHK001 : EC end date before start date
ECCHK002 : Missing dose amount (ECDOSE)
ECCHK003 : Dose unit missing when dose is present
ECCHK004 : Invalid dose form — not in allowed list
ECCHK005 : Missing administration status (ECSTAT)
"""
import pandas as pd
from pyCoreGage import collect_findings

ALLOWED_FORMS = {"TABLET", "CAPSULE"}


def check_EC(state, cfg):
    ec = state.domains.get("ec")
    if ec is None or ec.empty:
        print("  WARNING [EC]: domains['ec'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("ECCHK001"):
        sub = ec.dropna(subset=["ECSTDTC","ECENDTC"]).copy()
        sub = sub[(sub["ECSTDTC"].str.strip() != "") & (sub["ECENDTC"].str.strip() != "")]
        sub["st"] = pd.to_datetime(sub["ECSTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["ECENDTC"], errors="coerce")
        res = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "EC end date (" + res["en"].dt.strftime("%d%b%Y") +
            ") is before start date (" + res["st"].dt.strftime("%d%b%Y") +
            ") for treatment: " + res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECCHK001")

    if r.get("ECCHK002"):
        res = ec[ec["ECDOSE"].isna() | (ec["ECDOSE"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose amount (ECDOSE) is missing for treatment: " +
            res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECCHK002")

    if r.get("ECCHK003"):
        sub = ec[ec["ECDOSE"].notna() & (ec["ECDOSE"].astype(str).str.strip() != "")].copy()
        res = sub[sub["ECDOSU"].isna() | (sub["ECDOSU"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose unit (ECDOSU) is missing although dose (ECDOSE=" +
            res["ECDOSE"].astype(str) + ") is present for treatment: " +
            res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECCHK003")

    if r.get("ECCHK004"):
        sub = ec[ec["ECDOSFRM"].notna() & (ec["ECDOSFRM"].astype(str).str.strip() != "")].copy()
        res = sub[~sub["ECDOSFRM"].str.upper().str.strip().isin(ALLOWED_FORMS)].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Dose form '" + res["ECDOSFRM"] +
            "' not in allowed list (" + "/".join(ALLOWED_FORMS) + ")" +
            " for treatment: " + res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECCHK004")

    if r.get("ECCHK005"):
        res = ec[ec["ECSTAT"].isna() | (ec["ECSTAT"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Administration status (ECSTAT) is missing for treatment: " +
            res["ECTRT"] + " at visit " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="ECCHK005")

    return state
