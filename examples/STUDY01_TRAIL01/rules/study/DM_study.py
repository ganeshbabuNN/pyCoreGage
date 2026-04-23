"""DM_study.py — Demographics — Study-level checks
DMPRJ001 : Missing country (COUNTRY)
DMPRJ002 : Reference end date before reference start date
DMPRJ003 : Missing birth date (BRTHDTC)
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_DM_study(state, cfg):
    dm = state.domains.get("dm")
    if dm is None or dm.empty:
        print("  WARNING [DM_study]: domains['dm'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("DMPRJ001"):
        res = dm[dm["COUNTRY"].isna() | (dm["COUNTRY"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = "Country (COUNTRY) is missing in the demographics record"
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMPRJ001")

    if r.get("DMPRJ002"):
        sub = dm[
            dm["RFSTDTC"].notna() & (dm["RFSTDTC"].astype(str).str.strip() != "") &
            dm["RFENDTC"].notna() & (dm["RFENDTC"].astype(str).str.strip() != "")
        ].copy()
        sub["rf_st"] = pd.to_datetime(sub["RFSTDTC"], errors="coerce")
        sub["rf_en"] = pd.to_datetime(sub["RFENDTC"], errors="coerce")
        res = sub[sub["rf_st"].notna() & sub["rf_en"].notna() & (sub["rf_en"] < sub["rf_st"])].copy()
        res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
        res["description"] = (
            "Reference end date (RFENDTC=" + res["rf_en"].dt.strftime("%d%b%Y") +
            ") is before reference start date (RFSTDTC=" + res["rf_st"].dt.strftime("%d%b%Y") + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMPRJ002")

    if r.get("DMPRJ003"):
        if "BRTHDTC" not in dm.columns:
            print("  NOTE: BRTHDTC column not found - skipping DMPRJ003.")
        else:
            res = dm[dm["BRTHDTC"].isna() | (dm["BRTHDTC"].astype(str).str.strip() == "")].copy()
            res["subj_id"] = res["USUBJID"]; res["vis_id"] = float("nan")
            res["description"] = "Birth date (BRTHDTC) is missing in the demographics record"
            state = collect_findings(state, res[["subj_id","vis_id","description"]], id="DMPRJ003")

    return state
