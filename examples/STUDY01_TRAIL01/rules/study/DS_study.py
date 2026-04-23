"""DS_study.py — Disposition — Study-level checks
DSPRJ001 : Invalid epoch value (DSEPOCH)
DSPRJ002 : Duplicate primary disposition records per subject
DSPRJ003 : Missing site ID (SITEID)
"""
from pyCoreGage import collect_findings

ALLOWED_EPOCHS = {"SCREENING", "TREATMENT", "FOLLOW-UP"}


def check_DS_study(state, cfg):
    ds = state.domains.get("ds")
    if ds is None or ds.empty:
        print("  WARNING [DS_study]: domains['ds'] is empty - skipping.")
        return state
    r = state.active_rules

    #DSPRJ001 : Invalid epoch value (DSEPOCH)
    if r.get("DSPRJ001"):
        if "DSEPOCH" not in ds.columns:
            print("  NOTE: DSEPOCH column not found - skipping DSPRJ001.")
        else:
            sub = ds[ds["DSEPOCH"].notna() & (ds["DSEPOCH"].astype(str).str.strip() != "")].copy()
            res = sub[~sub["DSEPOCH"].str.upper().str.strip().isin(ALLOWED_EPOCHS)].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Epoch value '" + res["DSEPOCH"] +
                "' is not in the allowed list (" + "/".join(sorted(ALLOWED_EPOCHS)) + ")"
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSPRJ001")

    #DSPRJ002 : Duplicate primary disposition records per subject
    if r.get("DSPRJ002"):
        if "DSSCAT" not in ds.columns:
            print("  NOTE: DSSCAT column not found - skipping DSPRJ002.")
        else:
            primary = ds[ds["DSSCAT"].notna() & (ds["DSSCAT"].str.upper().str.strip() == "PRIMARY")]
            counts  = primary.groupby("USUBJID").size().reset_index(name="_n")
            dups    = counts[counts["_n"] > 1][["USUBJID"]]
            if not dups.empty:
                res = ds.merge(dups, on="USUBJID").drop_duplicates(subset=["USUBJID"]).copy()
                res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
                res["description"] = (
                    "More than one primary disposition (DSSCAT=PRIMARY) record found for subject"
                )
                state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSPRJ002")

    #DSPRJ003 : Missing site ID (SITEID)
    if r.get("DSPRJ003"):
        if "SITEID" not in ds.columns:
            print("  NOTE: SITEID column not found - skipping DSPRJ003.")
        else:
            res = ds[ds["SITEID"].isna() | (ds["SITEID"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = (
                "Site ID (SITEID) is missing for disposition: " +
                res["DSDECOD"].fillna("[DSDECOD missing]")
            )
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DSPRJ003")

    return state
