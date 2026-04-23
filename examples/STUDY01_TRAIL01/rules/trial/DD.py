"""DD.py — Death Details — Trial-level checks
DDCHK001 : Missing date of death (DDDTHDTC)
DDCHK002 : Missing cause of death term (DDTERM)
DDCHK003 : Missing death flag (DTHFL)
"""
from pyCoreGage import collect_findings


def check_DD(state, cfg):
    dd = state.domains.get("dd")
    if dd is None or dd.empty:
        print("  WARNING [DD]: domains['dd'] is empty - skipping.")
        return state
    r = state.active_rules
    
    for chk_id, col, msg in [
        ("DDCHK001", "DDDTHDTC", "Date of death (DDDTHDTC) is missing in the death details record"),
        ("DDCHK002", "DDTERM",   "Cause of death term (DDTERM) is missing in the death details record"),
        ("DDCHK003", "DTHFL",    "Death flag (DTHFL) is missing in the death details record"),
    ]:
        if r.get(chk_id):
            if col not in dd.columns:
                continue
            res = dd[dd[col].isna() | (dd[col].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = msg
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id=chk_id)

    return state
