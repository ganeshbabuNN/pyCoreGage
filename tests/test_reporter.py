"""
test_reporter.py — 9 test cases for build_reports()
"""

import os
import pandas as pd
import pytest

from pyCoreGage.reporter import build_reports
from pyCoreGage.state import CoreGageConfig, CoreGageState, _empty_issues, _empty_summary_log, _empty_review_log
from pyCoreGage.collector import collect_findings
from tests.conftest import make_registry_xlsx, valid_row


def _make_state_with_findings(reports_dir, n=3):
    from tests.conftest import make_registry_xlsx, make_cfg
    import tempfile
    tmp = tempfile.mkdtemp()
    reg_path = make_registry_xlsx(tmp, trial_rows=valid_row("AECHK001", "Yes", "AE"))
    from pyCoreGage.setup import setup_coregage
    cfg = CoreGageConfig(
        project_name="TEST", rule_registry=reg_path,
        trial_checks=tmp, study_checks=tmp,
        inputs=tmp, reports=reports_dir, feedback=tmp,
    )
    state = setup_coregage(cfg)
    df = pd.DataFrame({
        "subj_id":     [f"S{i}" for i in range(1, n+1)],
        "vis_id":      [float("nan")] * n,
        "description": [f"AE end date before start for subject S{i}" for i in range(1, n+1)],
    })
    state = collect_findings(state, df, id="AECHK001")
    return cfg, state


def test_reports_directory_created_if_missing(tmp_path):
    reports_dir = str(tmp_path / "new_reports")
    cfg, state  = _make_state_with_findings(reports_dir)
    build_reports(cfg, state)
    assert os.path.isdir(reports_dir)


def test_all_open_xlsx_written(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    assert os.path.isfile(os.path.join(str(tmp_path), "all_open.xlsx"))


def test_all_closed_xlsx_written(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    assert os.path.isfile(os.path.join(str(tmp_path), "all_closed.xlsx"))


def test_dm_issues_xlsx_written(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    assert os.path.isfile(os.path.join(str(tmp_path), "DM_issues.xlsx"))


def test_role_reports_all_written(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    for fname in ["DM_issues.xlsx", "MW_issues.xlsx", "SDTM_issues.xlsx", "ADAM_issues.xlsx"]:
        assert os.path.isfile(os.path.join(str(tmp_path), fname)), f"Missing: {fname}"


def test_all_open_has_details_sheet(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    df = pd.read_excel(os.path.join(str(tmp_path), "all_open.xlsx"), sheet_name="Details", skiprows=2)
    assert "CHECK ID" in df.columns


def test_all_open_has_summary_sheet(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path))
    build_reports(cfg, state)
    df = pd.read_excel(os.path.join(str(tmp_path), "all_open.xlsx"), sheet_name="Summary", skiprows=3)
    assert len(df) > 0


def test_no_findings_writes_empty_reports(tmp_path):
    from tests.conftest import make_registry_xlsx, make_cfg
    import tempfile
    tmp2 = tempfile.mkdtemp()
    reg_path = make_registry_xlsx(tmp2, trial_rows=valid_row())
    from pyCoreGage.setup import setup_coregage
    cfg = CoreGageConfig(
        project_name="TEST", rule_registry=reg_path,
        trial_checks=tmp2, study_checks=tmp2,
        inputs=tmp2, reports=str(tmp_path), feedback=tmp2,
    )
    state = setup_coregage(cfg)
    build_reports(cfg, state)
    assert os.path.isfile(os.path.join(str(tmp_path), "all_open.xlsx"))


def test_findings_status_set_to_open(tmp_path):
    cfg, state = _make_state_with_findings(str(tmp_path), n=2)
    build_reports(cfg, state)
    df = pd.read_excel(os.path.join(str(tmp_path), "all_open.xlsx"), sheet_name="Details", skiprows=2)
    assert all(df["STATUS"].astype(str).str.lower() == "open")
