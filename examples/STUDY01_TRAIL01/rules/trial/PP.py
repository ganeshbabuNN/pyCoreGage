"""PP.py — Pharmacokinetics Parameters — Trial-level checks
PPCHK001 : Missing PK parameter result (PPORRES)
PPCHK002 : Negative PK parameter value
PPCHK003 : Missing analysis date (PPDTC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_PP(state, cfg):
    pp = state.domains.get("pp")
    if pp is None or pp.empty:
        print("  WARNING [PP]: domains['pp'] is empty - skipping.")
        return state
    r = state.active_rules

    #PPCHK001 : Missing PK parameter result (PPORRES)
    if r.get("PPCHK001"):
        res = pp[pp["PPORRES"].isna() | (pp["PPORRES"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "PK parameter result (PPORRES) is missing for: " + res["PPTESTCD"]
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPCHK001")
    
    #PPCHK002 : Negative PK parameter value
    if r.get("PPCHK002"):
        sub = pp[pp["PPORRES"].notna() & (pp["PPORRES"].astype(str).str.strip() != "")].copy()
        sub["val"] = pd.to_numeric(sub["PPORRES"], errors="coerce")
        res = sub[sub["val"].notna() & (sub["val"] < 0)].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "PK parameter value (PPORRES=" + res["PPORRES"].astype(str) +
            ") is negative for parameter: " + res["PPTESTCD"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPCHK002")

    #PPCHK003 : Missing analysis date (PPDTC)
    if r.get("PPCHK003"):
        res = pp[pp["PPDTC"].isna() | (pp["PPDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Analysis date (PPDTC) is missing for parameter: " + res["PPTESTCD"]
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="PPCHK003")

    return state
