"""SV.py — Subject Visits — Trial-level checks
SVCHK001 : Missing visit start date (SVSTDTC)
SVCHK002 : Visit end date before visit start date
SVCHK003 : Visit dates not in chronological order within subject
"""
import pandas as pd
from pyCoreGage import collect_findings


def check_SV(state, cfg):
    sv = state.domains.get("sv")
    if sv is None or sv.empty:
        print("  WARNING [SV]: domains['sv'] is empty - skipping.")
        return state
    r = state.active_rules

    if r.get("SVCHK001"):
        res = sv[sv["SVSTDTC"].isna() | (sv["SVSTDTC"].astype(str).str.strip() == "")].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Visit start date (SVSTDTC) is missing for visit: " +
            res["VISIT"] + " (VISITNUM=" + res["VISITNUM"].astype(str) + ")"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVCHK001")

    if r.get("SVCHK002"):
        sub = sv.dropna(subset=["SVSTDTC","SVENDTC"]).copy()
        sub = sub[(sub["SVSTDTC"].astype(str).str.strip() != "") &
                  (sub["SVENDTC"].astype(str).str.strip() != "")]
        sub["sv_st"] = pd.to_datetime(sub["SVSTDTC"], errors="coerce")
        sub["sv_en"] = pd.to_datetime(sub["SVENDTC"],  errors="coerce")
        res = sub[sub["sv_st"].notna() & sub["sv_en"].notna() & (sub["sv_en"] < sub["sv_st"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = pd.to_numeric(res["VISITNUM"], errors="coerce")
        res["description"] = (
            "Visit end date (SVENDTC=" + res["sv_en"].dt.strftime("%d%b%Y") +
            ") is before start date (SVSTDTC=" + res["sv_st"].dt.strftime("%d%b%Y") +
            ") for visit: " + res["VISIT"]
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVCHK002")

    if r.get("SVCHK003"):
        sub = sv[sv["SVSTDTC"].notna() & (sv["SVSTDTC"].astype(str).str.strip() != "")].copy()
        sub["sv_dt"]  = pd.to_datetime(sub["SVSTDTC"], errors="coerce")
        sub["vis_num"] = pd.to_numeric(sub["VISITNUM"], errors="coerce")
        sub = sub[sub["sv_dt"].notna()].sort_values(["USUBJID","vis_num"])
        sub["prev_dt"]  = sub.groupby("USUBJID")["sv_dt"].shift(1)
        sub["prev_vis"] = sub.groupby("USUBJID")["VISIT"].shift(1)
        res = sub[sub["prev_dt"].notna() & (sub["sv_dt"] < sub["prev_dt"])].copy()
        res["subj_id"] = res["USUBJID"]
        res["vis_id"]  = res["vis_num"]
        res["description"] = (
            "Visit date (" + res["VISIT"] + " = " + res["sv_dt"].dt.strftime("%d%b%Y") +
            ") is before the previous visit (" + res["prev_vis"].fillna("") +
            " = " + res["prev_dt"].dt.strftime("%d%b%Y") +
            ") - visits are not in chronological order"
        )
        state = collect_findings(state, res[["subj_id","vis_id","description"]], id="SVCHK003")

    return state
