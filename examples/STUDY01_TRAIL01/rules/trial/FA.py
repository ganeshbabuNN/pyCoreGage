"""FA.py — Findings About Events — Trial-level checks
FACHK001 : Missing finding result (FAORRES)
FACHK002 : Missing finding date (FADTC)
FACHK003 : Missing evaluator flag (FAEVAL)
"""
from pyCoreGage import collect_findings


def check_FA(state, cfg):
    fa = state.domains.get("fa")
    if fa is None or fa.empty:
        print("  WARNING [FA]: domains['fa'] is empty - skipping.")
        return state
    r = state.active_rules

    for chk_id, col, label in [
        ("FACHK001", "FAORRES", "Finding result (FAORRES)"),
        ("FACHK002", "FADTC",   "Finding date (FADTC)"),
        ("FACHK003", "FAEVAL",  "Evaluator flag (FAEVAL)"),
    ]:
        if r.get(chk_id):
            res = fa[fa[col].isna() | (fa[col].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                label + " is missing for test: " +
                res["FATESTCD"].fillna("[FATESTCD missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id=chk_id)

    return state
