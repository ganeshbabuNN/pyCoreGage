"""
test_setup.py — 20 test cases for setup_coregage()
Mirrors the original R test-setup.R scenario by scenario.
"""

import os
import pytest
from openpyxl import Workbook

from pyCoreGage.setup import setup_coregage
from tests.conftest import make_registry_xlsx, make_cfg, valid_row


# ── helpers ──────────────────────────────────────────────────────────────────

def _setup(tmp_path, **kwargs):
    path = make_registry_xlsx(str(tmp_path), **kwargs)
    return setup_coregage(make_cfg(path, str(tmp_path)))


# ── tests ─────────────────────────────────────────────────────────────────────

def test_missing_registry_raises(tmp_path):
    cfg = make_cfg("/nonexistent/path/reg.xlsx", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="not found"):
        setup_coregage(cfg)


def test_trial_only_registry_returns_state(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    assert isinstance(st.rule_registry, __import__("pandas").DataFrame)
    assert "rule_registry" in st.__dataclass_fields__


def test_study_only_registry_returns_state(tmp_path):
    st = _setup(tmp_path, study_rows=valid_row("AEPRJ001", "Yes", "AE_study"))
    assert len(st.rule_registry) == 1
    assert st.rule_registry.iloc[0]["sheet"] == "Study"


def test_trial_and_study_combined(tmp_path):
    st = _setup(
        tmp_path,
        trial_rows=valid_row("AECHK001", "Yes", "AE"),
        study_rows=valid_row("AEPRJ001", "Yes", "AE_study"),
    )
    assert len(st.rule_registry) == 2
    assert "Trial" in st.rule_registry["sheet"].values
    assert "Study" in st.rule_registry["sheet"].values


def test_active_yes_is_true_in_active_rules(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row("AECHK001", "Yes", "AE"))
    assert st.active_rules.get("AECHK001") is True


def test_active_no_is_false_in_active_rules(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row("AECHK001", "No", "AE"))
    assert st.active_rules.get("AECHK001") is False


def test_active_rules_names_match_registry_ids(tmp_path):
    st = _setup(
        tmp_path,
        trial_rows=[valid_row("AECHK001", "Yes", "AE"), valid_row("LBCHK001", "No", "LB")],
    )
    assert "AECHK001" in st.active_rules
    assert "LBCHK001" in st.active_rules


def test_ids_are_uppercased(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row("aechk001", "Yes", "AE"))
    assert "AECHK001" in st.active_rules


def test_blank_id_rows_filtered_out(tmp_path):
    rows = [valid_row("AECHK001", "Yes", "AE"), ["AE", "Date", "", "Yes", "Yes", "No", "Yes", "No", "AE", "Blank", ""]]
    st = _setup(tmp_path, trial_rows=rows)
    assert len(st.rule_registry) == 1


def test_yourid_placeholder_filtered_out(tmp_path):
    rows = [valid_row("AECHK001", "Yes", "AE"), ["AE", "Date", "YOURID", "Yes", "Yes", "No", "Yes", "No", "AE", "Tmpl", ""]]
    st = _setup(tmp_path, trial_rows=rows)
    assert len(st.rule_registry) == 1


def test_issues_empty_with_correct_columns(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    assert len(st.issues) == 0
    for col in ["id", "subj_id", "vis_id", "description", "review"]:
        assert col in st.issues.columns


def test_summary_log_empty_with_correct_columns(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    assert len(st.summary_log) == 0
    for col in ["headlink", "nu", "rule_set", "sobs"]:
        assert col in st.summary_log.columns


def test_review_log_empty_with_correct_columns(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    assert len(st.review_log) == 0
    for col in ["id", "subj_id", "vis_id", "status", "analyst_note", "review_note"]:
        assert col in st.review_log.columns


def test_session_contains_sdate_and_stime(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    assert "sdate" in st.session
    assert "stime" in st.session
    assert isinstance(st.session["sdate"], str)
    assert isinstance(st.session["stime"], str)


def test_rule_registry_has_all_required_columns(tmp_path):
    st = _setup(tmp_path, trial_rows=valid_row())
    for col in ["id", "active", "rule_set", "dm_report", "mw_report", "sdtm_report", "adam_report", "sheet"]:
        assert col in st.rule_registry.columns


def test_rule_registry_sorted_by_rule_set_then_id(tmp_path):
    rows = [
        valid_row("LBCHK001", "Yes", "LB"),
        valid_row("AECHK001", "Yes", "AE"),
        valid_row("AECHK002", "Yes", "AE"),
    ]
    st = _setup(tmp_path, trial_rows=rows)
    assert st.rule_registry.iloc[0]["rule_set"] == "AE"
    ae_rows = st.rule_registry[st.rule_registry["rule_set"] == "AE"]
    assert ae_rows.iloc[0]["id"] == "AECHK001"


def test_sheet_with_only_blank_ids_raises(tmp_path):
    blank = ["AE", "Date", "", "Yes", "Yes", "No", "Yes", "No", "AE", "", ""]
    path = make_registry_xlsx(str(tmp_path), trial_rows=blank)
    cfg = make_cfg(path, str(tmp_path))
    with pytest.raises(ValueError, match="No valid check definitions"):
        setup_coregage(cfg)


def test_extra_unknown_columns_handled_gracefully(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Trial"
    from tests.conftest import COLS
    extra_cols = COLS + ["EXTRA_COL"]
    ws.append(extra_cols)
    ws.append(["AE", "Date", "AECHK001", "Yes", "Yes", "No", "Yes", "No", "AE", "Chk", "", "extra"])
    path = os.path.join(str(tmp_path), "reg_extra.xlsx")
    wb.save(path)
    cfg = make_cfg(path, str(tmp_path))
    st = setup_coregage(cfg)
    assert len(st.rule_registry) == 1


def test_mixed_active_case_values_handled(tmp_path):
    rows = [
        valid_row("CHK001", "YES", "AE"),
        valid_row("CHK002", "yes", "LB"),
        valid_row("CHK003", "No",  "CM"),
    ]
    st = _setup(tmp_path, trial_rows=rows)
    assert st.active_rules["CHK001"] is True
    assert st.active_rules["CHK002"] is True
    assert st.active_rules["CHK003"] is False


def test_session_sdate_is_today(tmp_path):
    from datetime import date
    st = _setup(tmp_path, trial_rows=valid_row())
    expected = date.today().strftime("%d%b%Y")
    assert st.session["sdate"] == expected
