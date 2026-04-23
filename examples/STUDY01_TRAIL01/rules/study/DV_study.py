"""DV_study.py — Protocol Deviations — Study-level checks
DVPRJ001 : Missing reason for deviation (DVREASND)
DVPRJ002 : Missing dictionary coded term (DVDECOD)
DVPRJ003 : Missing site ID (SITEID)
"""
from pyCoreGage import collect_findings


def check_DV_study(state, cfg):
    dv = state.domains.get("dv")
    if dv is None or dv.empty:
        print("  WARNING [DV_study]: domains['dv'] is empty - skipping.")
        return state
    r = state.active_rules

    #DVPRJ001 : Missing reason for deviation (DVREASND)
    if r.get("DVPRJ001"):
        if "DVREASND" not in dv.columns:
            print("  NOTE: DVREASND column not found - skipping DVPRJ001.")
        else:
            res = dv[dv["DVREASND"].isna() | (dv["DVREASND"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Reason for deviation (DVREASND) is missing for: " +
                res["DVTERM"].fillna("[DVTERM missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVPRJ001")

    #DVPRJ002 : Missing dictionary coded term (DVDECOD)
    if r.get("DVPRJ002"):
        if "DVDECOD" not in dv.columns:
            print("  NOTE: DVDECOD column not found - skipping DVPRJ002.")
        else:
            sub = dv[dv["DVTERM"].notna() & (dv["DVTERM"].astype(str).str.strip() != "")].copy()
            res = sub[sub["DVDECOD"].isna() | (sub["DVDECOD"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Dictionary coded term (DVDECOD) is missing for deviation: " + res["DVTERM"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVPRJ002")

    #DVPRJ003 : Missing site ID (SITEID)
    if r.get("DVPRJ003"):
        if "SITEID" not in dv.columns:
            print("  NOTE: SITEID column not found - skipping DVPRJ003.")
        else:
            res = dv[dv["SITEID"].isna() | (dv["SITEID"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Site ID (SITEID) is missing for deviation: " +
                res["DVTERM"].fillna("[DVTERM missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DVPRJ003")

    return state
