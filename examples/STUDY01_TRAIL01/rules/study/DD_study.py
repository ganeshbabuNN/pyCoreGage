"""DD_study.py — Death Details — Study-level checks
DDPRJ001 : Missing coded cause of death (DDDECOD)
DDPRJ002 : Unconfirmed death status (DDSTAT != CONFIRMED)
DDPRJ003 : Missing site ID (SITEID)
"""
from pyCoreGage import collect_findings


def check_DD_study(state, cfg):
    dd = state.domains.get("dd")
    if dd is None or dd.empty:
        print("  WARNING [DD_study]: domains['dd'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("DDPRJ001"):
        sub = dd[dd["DDTERM"].notna() & (dd["DDTERM"].astype(str).str.strip() != "")].copy()
        res = sub[sub["DDDECOD"].isna() | (sub["DDDECOD"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Coded cause of death (DDDECOD) is missing for term: " + res["DDTERM"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DDPRJ001")

    if r.get("DDPRJ002"):
        if "DDSTAT" not in dd.columns:
            print("  NOTE: DDSTAT column not found - skipping DDPRJ002.")
        else:
            res = dd[
                dd["DDSTAT"].notna() & (dd["DDSTAT"].astype(str).str.strip() != "") &
                (dd["DDSTAT"].astype(str).str.upper().str.strip() != "CONFIRMED")
            ].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Death status (DDSTAT='" + res["DDSTAT"].astype(str) +
                "') is not CONFIRMED for cause: " +
                res["DDTERM"].fillna("[DDTERM missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DDPRJ002")

    if r.get("DDPRJ003"):
        if "SITEID" not in dd.columns:
            print("  NOTE: SITEID column not found - skipping DDPRJ003.")
        else:
            res = dd[dd["SITEID"].isna() | (dd["SITEID"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = "Site ID (SITEID) is missing in the death details record"
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DDPRJ003")

    return state
