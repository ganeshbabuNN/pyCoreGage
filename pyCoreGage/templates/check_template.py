"""
check_template.py — Blank check script scaffold.

Instructions
------------
1. Copy this file to rules/trial/ or rules/study/
2. Rename it to match the Rule_Set value in rule_registry.xlsx
   e.g. rules/trial/AE.py  for Rule_Set = "AE"
3. Rename the function below to match: check_{Rule_Set}
4. Implement your checks inside the function body
5. Call collect_findings() for each check block

The function receives:
  state : CoreGageState  — contains state.domains and state.active_rules
  cfg   : CoreGageConfig — contains project paths

Return the (possibly updated) state object.
"""

from pyCoreGage import collect_findings
import pandas as pd


def check_MYRULESET(state, cfg):
    """Replace MYRULESET with your actual Rule_Set name."""

    domains      = state.domains
    active_rules = state.active_rules

    # Guard: exit early if the domain data is not loaded
    if "ae" not in domains or domains["ae"].empty:
        return state

    ae = domains["ae"].copy()

    # ── Check block template ─────────────────────────────────────────────────
    # if active_rules.get("AECHK001"):
    #     result = ae.loc[
    #         ae["AESTDTC"].notna() & ae["AEENDTC"].notna()
    #     ].copy()
    #     result["subj_id"]     = result["USUBJID"]
    #     result["vis_id"]      = float("nan")
    #     result["description"] = "Your finding description here"
    #     state = collect_findings(
    #         state,
    #         result[["subj_id", "vis_id", "description"]],
    #         id="AECHK001",
    #     )

    return state
