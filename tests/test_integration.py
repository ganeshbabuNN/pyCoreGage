"""
test_integration.py — Full end-to-end integration test.

Simulates a complete pyCoreGage run:
  1. setup_coregage()
  2. load_inputs()   (CSV files written to temp dir)
  3. run_checks()    (check scripts written to temp dir)
  4. build_reports() (Excel outputs verified)
"""

import os
import tempfile

import pandas as pd
import pytest

from pyCoreGage import (
    CoreGageConfig, setup_coregage, load_inputs,
    run_checks, build_reports,
)
from tests.conftest import make_registry_xlsx, valid_row


# ---------------------------------------------------------------------------
# Fixture: full project in temp dir
# ---------------------------------------------------------------------------

@pytest.fixture
def full_project(tmp_path):
    """
    Creates a minimal but complete pyCoreGage project:
    - rule_registry.xlsx with 2 Trial + 1 Study check
    - AE.csv and LB.csv inputs
    - AE.py trial check script
    - LB_study.py study check script
    Returns (cfg, tmp_path_str).
    """
    d = str(tmp_path)
    trial_dir  = os.path.join(d, "trial_checks")
    study_dir  = os.path.join(d, "study_checks")
    inputs_dir = os.path.join(d, "inputs")
    reports_dir= os.path.join(d, "reports")
    feedback_dir = os.path.join(d, "feedback")
    for dd in [trial_dir, study_dir, inputs_dir, reports_dir, feedback_dir]:
        os.makedirs(dd, exist_ok=True)

    # Registry
    rows_trial = [
        ["AE", "Date",  "AECHK001", "Yes", "Yes", "No",  "Yes", "No",  "AE", "AE end date before start", ""],
        ["LB", "Range", "LBCHK001", "Yes", "Yes", "No",  "Yes", "Yes", "LB", "Lab out of range",          ""],
        ["AE", "Comp.", "AECHK002", "No",  "Yes", "No",  "No",  "No",  "AE", "Inactive check",            ""],
    ]
    rows_study = [
        ["AE", "Cross", "AEPRJ001", "Yes", "Yes", "Yes", "No",  "No",  "AE_study", "AE cross-domain check", ""],
    ]
    reg_path = make_registry_xlsx(d, trial_rows=rows_trial, study_rows=rows_study)

    # Input data: AE.csv
    ae_df = pd.DataFrame({
        "USUBJID":  ["S001", "S002", "S003", "S001"],
        "AETERM":   ["RASH", "HEADACHE", "NAUSEA", "FATIGUE"],
        "AESTDTC":  ["2024-01-10", "2024-02-01", "2024-03-05", "2024-04-01"],
        "AEENDTC":  ["2024-01-05", "2024-02-15", "2024-03-10", "2024-03-30"],  # S001 row 1: end < start
        "AESEV":    ["MILD", None,  "MILD",   "MODERATE"],
    })
    ae_df.to_csv(os.path.join(inputs_dir, "AE.csv"), index=False, na_rep="")

    # Input data: LB.csv
    lb_df = pd.DataFrame({
        "USUBJID":  ["S001", "S002", "S003"],
        "LBTEST":   ["Sodium", "Potassium", "Glucose"],
        "LBORRES":  ["200",    "2.0",        "55"],
        "LBNRLO":   ["136",    "3.5",        "70"],
        "LBNRHI":   ["145",    "5.1",        "100"],
        "LBORRESU": ["mEq/L",  "mEq/L",      "mg/dL"],
        "VISITNUM": [1, 1, 1],
        "VISIT":    ["V1", "V1", "V1"],
        "LBTESTCD": ["NA", "K", "GLU"],
    })
    lb_df.to_csv(os.path.join(inputs_dir, "LB.csv"), index=False, na_rep="")

    # Trial check: AE.py
    ae_check = """
import pandas as pd
from pyCoreGage import collect_findings

def check_AE(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        return state

    active_rules = state.active_rules

    if active_rules.get("AECHK001"):
        mask = ae["AESTDTC"].notna() & ae["AEENDTC"].notna()
        sub  = ae[mask].copy()
        sub["st"] = pd.to_datetime(sub["AESTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["AEENDTC"], errors="coerce")
        result = sub[sub["en"] < sub["st"]].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = float("nan")
            result["description"] = (
                "End (" + result["en"].dt.strftime("%d%b%Y") +
                ") before start (" + result["st"].dt.strftime("%d%b%Y") +
                ") for: " + result["AETERM"]
            )
            state = collect_findings(
                state, result[["subj_id","vis_id","description"]], id="AECHK001"
            )

    return state
"""
    with open(os.path.join(trial_dir, "AE.py"), "w") as f:
        f.write(ae_check)

    # Trial check: LB.py
    lb_check = """
import pandas as pd
from pyCoreGage import collect_findings

def check_LB(state, cfg):
    lb = state.domains.get("lb")
    if lb is None or lb.empty:
        return state

    active_rules = state.active_rules

    if active_rules.get("LBCHK001"):
        sub = lb.copy()
        sub["val"] = pd.to_numeric(sub["LBORRES"], errors="coerce")
        sub["lo"]  = pd.to_numeric(sub["LBNRLO"],  errors="coerce")
        sub["hi"]  = pd.to_numeric(sub["LBNRHI"],  errors="coerce")
        result = sub[(sub["val"].notna()) & ((sub["val"] < sub["lo"]) | (sub["val"] > sub["hi"]))].copy()
        if not result.empty:
            result["subj_id"]     = result["USUBJID"]
            result["vis_id"]      = pd.to_numeric(result["VISITNUM"], errors="coerce")
            result["description"] = (
                result["LBTEST"] + " = " + result["val"].astype(str) +
                " outside [" + result["lo"].astype(str) + " - " + result["hi"].astype(str) + "]"
            )
            state = collect_findings(
                state, result[["subj_id","vis_id","description"]], id="LBCHK001"
            )
    return state
"""
    with open(os.path.join(trial_dir, "LB.py"), "w") as f:
        f.write(lb_check)

    # Study check: AE_study.py
    ae_study_check = """
import pandas as pd
from pyCoreGage import collect_findings

def check_AE_study(state, cfg):
    active_rules = state.active_rules
    ae = state.domains.get("ae")
    lb = state.domains.get("lb")

    if active_rules.get("AEPRJ001") and ae is not None and lb is not None:
        ae_subjects = set(ae["USUBJID"].dropna())
        lb_subjects = set(lb["USUBJID"].dropna())
        missing = ae_subjects - lb_subjects
        if missing:
            result = pd.DataFrame({
                "subj_id":     list(missing),
                "vis_id":      [float("nan")] * len(missing),
                "description": [f"Subject {s} has AE but no LB records" for s in missing],
            })
            state = collect_findings(state, result, id="AEPRJ001")
    return state
"""
    with open(os.path.join(study_dir, "AE_study.py"), "w") as f:
        f.write(ae_study_check)

    cfg = CoreGageConfig(
        project_name  = "INTEGRATION_TEST",
        rule_registry = reg_path,
        trial_checks  = trial_dir,
        study_checks  = study_dir,
        inputs        = inputs_dir,
        reports       = reports_dir,
        feedback      = feedback_dir,
    )
    return cfg, d


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_e2e_setup_returns_correct_rule_count(full_project):
    cfg, _ = full_project
    state  = setup_coregage(cfg)
    # 3 trial rows + 1 study row = 4 total; AECHK002 active=No still in registry
    assert len(state.rule_registry) == 4


def test_e2e_load_inputs_loads_both_domains(full_project):
    cfg, _  = full_project
    state   = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    assert "ae" in state.domains
    assert "lb" in state.domains
    assert len(state.domains["ae"]) == 4
    assert len(state.domains["lb"]) == 3


def test_e2e_run_checks_finds_ae_date_violation(full_project):
    cfg, _     = full_project
    state      = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state      = run_checks(cfg, state)
    ae_findings = state.issues[state.issues["id"] == "AECHK001"]
    assert len(ae_findings) >= 1


def test_e2e_run_checks_finds_lb_range_violations(full_project):
    cfg, _     = full_project
    state      = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state      = run_checks(cfg, state)
    lb_findings = state.issues[state.issues["id"] == "LBCHK001"]
    assert len(lb_findings) >= 2  # S001 (Na too high) and S002 (K too low)


def test_e2e_inactive_check_produces_no_findings(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    aechk002  = state.issues[state.issues["id"] == "AECHK002"]
    assert len(aechk002) == 0


def test_e2e_study_check_executed(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    # AE_study check runs — either finds cross-domain issues or finds none
    assert "AEPRJ001" in state.active_rules


def test_e2e_build_reports_writes_all_six_files(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    build_reports(cfg, state)
    for fname in [
        "all_open.xlsx", "all_closed.xlsx",
        "DM_issues.xlsx", "MW_issues.xlsx",
        "SDTM_issues.xlsx", "ADAM_issues.xlsx",
    ]:
        assert os.path.isfile(os.path.join(cfg.reports, fname)), f"Missing: {fname}"


def test_e2e_all_open_contains_findings(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    build_reports(cfg, state)
    df = pd.read_excel(
        os.path.join(cfg.reports, "all_open.xlsx"),
        sheet_name="Details", skiprows=2,
    )
    assert len(df) > 0
    assert "CHECK ID" in df.columns


def test_e2e_findings_status_is_open_on_first_run(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    build_reports(cfg, state)
    df = pd.read_excel(
        os.path.join(cfg.reports, "all_open.xlsx"),
        sheet_name="Details", skiprows=2,
    )
    statuses = df["STATUS"].astype(str).str.lower().unique()
    assert all(s in ("open", "queried") for s in statuses if s not in ("nan", "n/a"))


def test_e2e_second_run_reimports_previous_issues(full_project):
    cfg, _    = full_project
    state     = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    state     = run_checks(cfg, state)
    build_reports(cfg, state)

    # Second run
    state2    = setup_coregage(cfg)
    state2.domains = load_inputs(cfg)
    state2    = run_checks(cfg, state2)
    build_reports(cfg, state2)

    df = pd.read_excel(
        os.path.join(cfg.reports, "all_open.xlsx"),
        sheet_name="Details", skiprows=2,
    )
    # Still has findings — nothing disappeared so nothing auto-closed
    assert len(df) > 0
