"""DS.py — Disposition — Trial-level checks
DSCHK001 : Missing disposition date (DSSTDTC)
DSCHK002 : Missing disposition decision (DSDECOD)
DSCHK003 : Missing disposition term (DSTERM)
"""
from pyCoreGage import collect_findings


def check_DS(state, cfg):
    ds = state.domains.get("ds")
    if ds is None or ds.empty:
        print("  WARNING [DS]: domains['ds'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("DSCHK001"):
        res = ds[ds["DSSTDTC"].isna() | (ds["DSSTDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Disposition date (DSSTDTC) is missing for disposition: " +
            res["DSDECOD"].fillna("[DSDECOD missing]")
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSCHK001")

    if r.get("DSCHK002"):
        res = ds[ds["DSDECOD"].isna() | (ds["DSDECOD"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Disposition decision (DSDECOD) is missing in the disposition record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSCHK002")

    if r.get("DSCHK003"):
        res = ds[ds["DSTERM"].isna() | (ds["DSTERM"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Disposition verbatim term (DSTERM) is missing in the disposition record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSCHK003")

    return state
