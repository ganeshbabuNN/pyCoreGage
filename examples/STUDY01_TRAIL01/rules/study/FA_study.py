"""FA_study.py — Findings About Events — Study-level checks
FAPRJ001 : Missing parent domain reference object (FAOBJ)
FAPRJ002 : Missing test code (FATESTCD)
FAPRJ003 : Missing finding status (FASTAT)
"""
from pyCoreGage import collect_findings


def check_FA_study(state, cfg):
    fa = state.domains.get("fa")
    if fa is None or fa.empty:
        print("  WARNING [FA_study]: domains['fa'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("FAPRJ001"):
        if "FAOBJ" not in fa.columns:
            print("  NOTE: FAOBJ column not found - skipping FAPRJ001.")
        else:
            res = fa[fa["FAOBJ"].isna() | (fa["FAOBJ"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Parent domain reference object (FAOBJ) is missing for test: " +
                res["FATESTCD"].fillna("[FATESTCD missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="FAPRJ001")

    if r.get("FAPRJ002"):
        res = fa[fa["FATESTCD"].isna() | (fa["FATESTCD"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Finding test code (FATESTCD) is missing in the findings about record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="FAPRJ002")

    if r.get("FAPRJ003"):
        if "FASTAT" not in fa.columns:
            print("  NOTE: FASTAT column not found - skipping FAPRJ003.")
        else:
            res = fa[fa["FASTAT"].isna() | (fa["FASTAT"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Finding status (FASTAT) is missing for test: " +
                res["FATESTCD"].fillna("[FATESTCD missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="FAPRJ003")

    return state
