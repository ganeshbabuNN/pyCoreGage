"""DV.py — Protocol Deviations — Trial-level checks
DVCHK001 : Missing deviation date (DVSTDTC)
DVCHK002 : Missing deviation term (DVTERM)
DVCHK003 : Missing deviation category (DVCAT)
"""
from pyCoreGage import collect_findings


def check_DV(state, cfg):
    dv = state.domains.get("dv")
    if dv is None or dv.empty:
        print("  WARNING [DV]: domains['dv'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("DVCHK001"):
        res = dv[dv["DVSTDTC"].isna() | (dv["DVSTDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Deviation date (DVSTDTC) is missing for deviation: " +
            res["DVTERM"].fillna("[DVTERM missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVCHK001")

    if r.get("DVCHK002"):
        res = dv[dv["DVTERM"].isna() | (dv["DVTERM"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Protocol deviation term (DVTERM) is missing in the deviation record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVCHK002")

    if r.get("DVCHK003"):
        res = dv[dv["DVCAT"].isna() | (dv["DVCAT"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Deviation category (DVCAT) is missing for deviation: " +
            res["DVTERM"].fillna("[DVTERM missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVCHK003")

    return state
