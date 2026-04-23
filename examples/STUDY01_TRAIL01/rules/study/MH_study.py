"""MH_study.py — Medical History — Study-level checks
MHPRJ001 : Missing dictionary coded term (MHDECOD)
MHPRJ002 : Invalid medical history status (MHSTAT)
MHPRJ003 : Missing body system (MHBODSYS)
"""
from pyCoreGage import collect_findings

ALLOWED_STAT = {"ONGOING", "RESOLVED", "UNKNOWN"}


def check_MH_study(state, cfg):
    mh = state.domains.get("mh")
    if mh is None or mh.empty:
        print("  WARNING [MH_study]: domains['mh'] is empty - skipping.")
        return state
    r = state.active_rules

    #MHPRJ001 : Missing dictionary coded term (MHDECOD)
    if r.get("MHPRJ001"):
        if "MHDECOD" not in mh.columns:
            print("  NOTE: MHDECOD column not found - skipping MHPRJ001.")
        else:
            sub = mh[mh["MHTERM"].notna() & (mh["MHTERM"].astype(str).str.strip() != "")].copy()
            res = sub[sub["MHDECOD"].isna() | (sub["MHDECOD"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Dictionary coded term (MHDECOD) is missing for condition: " + res["MHTERM"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHPRJ001")

    #MHPRJ002 : Invalid medical history status (MHSTAT)
    if r.get("MHPRJ002"):
        if "MHSTAT" not in mh.columns:
            print("  NOTE: MHSTAT column not found - skipping MHPRJ002.")
        else:
            sub = mh[mh["MHSTAT"].notna() & (mh["MHSTAT"].astype(str).str.strip() != "")].copy()
            res = sub[~sub["MHSTAT"].str.upper().str.strip().isin(ALLOWED_STAT)].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Medical history status '" + res["MHSTAT"] +
                "' is not in allowed list (" + "/".join(sorted(ALLOWED_STAT)) + ")" +
                " for condition: " + res["MHTERM"].fillna("[MHTERM missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHPRJ002")

    #MHPRJ003 : Missing body system (MHBODSYS)
    if r.get("MHPRJ003"):
        if "MHBODSYS" not in mh.columns:
            print("  NOTE: MHBODSYS column not found - skipping MHPRJ003.")
        else:
            res = mh[mh["MHBODSYS"].isna() | (mh["MHBODSYS"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Body system (MHBODSYS) is missing for condition: " +
                res["MHTERM"].fillna("[MHTERM missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="MHPRJ003")

    return state
