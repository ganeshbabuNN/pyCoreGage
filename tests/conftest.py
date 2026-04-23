"""
conftest.py — shared pytest fixtures for all pyCoreGage test modules.
"""

import os
import tempfile

import pandas as pd
import pytest
from openpyxl import Workbook

from pyCoreGage.state import CoreGageConfig, CoreGageState, _empty_issues, _empty_summary_log, _empty_review_log

# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

COLS = [
    "Category", "Subcategory", "ID", "Active",
    "DM_Report", "MW_Report", "SDTM_Report", "ADAM_Report",
    "Rule_Set", "Description", "Notes",
]


def valid_row(id="AECHK001", active="Yes", rule_set="AE"):
    """Return one registry row as a list matching COLS order."""
    return ["AE", "Date", id, active, "Yes", "No", "Yes", "No", rule_set, "Check desc", ""]


def make_registry_xlsx(tmp_path, trial_rows=None, study_rows=None) -> str:
    """Write a rule_registry.xlsx to tmp_path and return its path."""
    path = os.path.join(tmp_path, "rule_registry.xlsx")
    wb = Workbook()
    wb.remove(wb.active)

    def _add_sheet(name, rows):
        ws = wb.create_sheet(name)
        ws.append(COLS)
        if rows:
            # rows may be a single list or a list-of-lists
            if rows and not isinstance(rows[0], list):
                rows = [rows]
            for r in rows:
                ws.append(r)

    if trial_rows is not None:
        _add_sheet("Trial", trial_rows)
    if study_rows is not None:
        _add_sheet("Study", study_rows)

    wb.save(path)
    return path


def make_cfg(reg_path, tmp_path=None) -> CoreGageConfig:
    d = tmp_path or tempfile.mkdtemp()
    return CoreGageConfig(
        project_name  = "TEST_PROJECT",
        rule_registry = reg_path,
        trial_checks  = d,
        study_checks  = d,
        inputs        = d,
        reports       = d,
        feedback      = d,
    )


# ---------------------------------------------------------------------------
# State helper
# ---------------------------------------------------------------------------

def make_state(registry_df=None) -> CoreGageState:
    if registry_df is None:
        registry_df = pd.DataFrame([{
            "id": "CHK001", "active": "YES", "rule_set": "TESTCHECK",
            "sheet": "Trial", "category": "Test", "subcategory": "Test",
            "description": "Test", "dm_report": "YES", "mw_report": "NO",
            "sdtm_report": "NO", "adam_report": "NO", "notes": "",
        }])
    active_rules = {
        row["id"]: row["active"].startswith("Y")
        for _, row in registry_df.iterrows()
    }
    return CoreGageState(
        rule_registry = registry_df,
        active_rules  = active_rules,
        issues        = _empty_issues(),
        summary_log   = _empty_summary_log(),
        review_log    = _empty_review_log(),
        domains       = {},
        session       = {"sdate": "01Jan2024", "stime": "09:00"},
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp(tmp_path):
    """Return a string temp directory path."""
    return str(tmp_path)


@pytest.fixture
def basic_reg(tmp_path):
    """A minimal valid registry file with one active Trial row."""
    return make_registry_xlsx(str(tmp_path), trial_rows=valid_row())


@pytest.fixture
def basic_cfg(basic_reg, tmp_path):
    return make_cfg(basic_reg, str(tmp_path))


@pytest.fixture
def basic_state():
    return make_state()
