"""PP_study.py — Pharmacokinetics Parameters — Study-level checks
PPPRJ001 : Missing standardised units (PPSTRESU)
PPPRJ002 : Missing specimen type (PPSPEC)
PPPRJ003 : Invalid parameter category (PPCAT not DERIVED)
"""
from pyCoreGage import collect_findings


def check_PP_study(state, cfg):
    pp = state.domains.get("pp")
    if pp is None or pp.empty:
        print("  WARNING [PP_study]: domains['pp'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("PPPRJ001"):
        if "PPSTRESU" not in pp.columns:
            print("  NOTE: PPSTRESU column not found - skipping PPPRJ001.")
        else:
            res = pp[pp["PPSTRESU"].isna() | (pp["PPSTRESU"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Standardised units (PPSTRESU) are missing for parameter: " + res["PPTESTCD"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPPRJ001")

    if r.get("PPPRJ002"):
        if "PPSPEC" not in pp.columns:
            print("  NOTE: PPSPEC column not found - skipping PPPRJ002.")
        else:
            res = pp[pp["PPSPEC"].isna() | (pp["PPSPEC"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Specimen type (PPSPEC) is missing for parameter: " + res["PPTESTCD"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPPRJ002")

    if r.get("PPPRJ003"):
        if "PPCAT" not in pp.columns:
            print("  NOTE: PPCAT column not found - skipping PPPRJ003.")
        else:
            sub = pp[pp["PPCAT"].notna() & (pp["PPCAT"].astype(str).str.strip() != "")].copy()
            res = sub[sub["PPCAT"].str.upper().str.strip() != "DERIVED"].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Parameter category (PPCAT='" + res["PPCAT"] +
                "') should be DERIVED for parameter: " + res["PPTESTCD"]
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPPRJ003")

    return state
