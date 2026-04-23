"""
test_runner.py — 12 test cases for run_checks()
Mirrors the original R test-runner.R scenario by scenario.
"""

import os
import pandas as pd
import pytest

from pyCoreGage.runner import run_checks
from pyCoreGage.state import CoreGageConfig
from tests.conftest import make_state


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_cfg(trial_dir, study_dir=None) -> CoreGageConfig:
    return CoreGageConfig(
        project_name  = "TEST",
        rule_registry = "/unused",
        trial_checks  = trial_dir,
        study_checks  = study_dir or trial_dir,
        inputs        = trial_dir,
        reports       = trial_dir,
        feedback      = trial_dir,
    )


def _write_check(directory, rule_set, n=2, fn_name=None, crash=False):
    """Write a minimal check script to directory/{rule_set}.py"""
    fn = fn_name or f"check_{rule_set}"
    path = os.path.join(directory, f"{rule_set}.py")
    if crash:
        content = f"def {fn}(state, cfg):\n    raise RuntimeError('deliberate')\n"
    else:
        content = (
            f"import pandas as pd\n"
            f"from pyCoreGage import collect_findings\n\n"
            f"def {fn}(state, cfg):\n"
            f"    if {n} > 0:\n"
            f"        df = pd.DataFrame({{\n"
            f"            'subj_id': [f'S{{i}}' for i in range(1, {n}+1)],\n"
            f"            'vis_id': [float('nan')] * {n},\n"
            f"            'description': [f'Issue {{i}}' for i in range(1, {n}+1)],\n"
            f"        }})\n"
            f"        state = collect_findings(state, df, id='{rule_set}')\n"
            f"    return state\n"
        )
    with open(path, "w") as f:
        f.write(content)
    return path


def _reg_row(id, rule_set, active="YES", sheet="Trial"):
    return {
        "id": id, "active": active, "rule_set": rule_set, "sheet": sheet,
        "category": "T", "subcategory": "T", "description": "T",
        "dm_report": "NO", "mw_report": "NO", "sdtm_report": "NO",
        "adam_report": "NO", "notes": "",
    }


# ── tests ─────────────────────────────────────────────────────────────────────

def test_no_active_rules_state_unchanged(tmp_path):
    reg = pd.DataFrame([_reg_row("CHK001", "TESTCHECK", active="NO")])
    st  = make_state(reg)
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 0


def test_missing_check_file_skipped(tmp_path, caplog):
    st  = make_state()
    cfg = _make_cfg("/nonexistent/dir", str(tmp_path))
    import logging
    with caplog.at_level(logging.WARNING, logger="pyCoreGage"):
        st2 = run_checks(cfg, st)
    assert len(st2.issues) == 0


def test_valid_check_script_findings_appended(tmp_path):
    _write_check(str(tmp_path), "TESTCHECK", n=3)
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 3


def test_trial_sheet_rules_from_trial_dir(tmp_path):
    _write_check(str(tmp_path), "TESTCHECK", n=2)
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 2


def test_study_sheet_rules_from_study_dir(tmp_path):
    study_dir = str(tmp_path / "study")
    os.makedirs(study_dir, exist_ok=True)
    _write_check(study_dir, "STUDYCHK", n=1)
    reg = pd.DataFrame([_reg_row("SPRJ001", "STUDYCHK", sheet="Study")])
    st  = make_state(reg)
    cfg = _make_cfg(str(tmp_path), study_dir=study_dir)
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 1


def test_error_in_check_caught_runner_continues(tmp_path, caplog):
    _write_check(str(tmp_path), "TESTCHECK", crash=True)
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    import logging
    with caplog.at_level(logging.ERROR, logger="pyCoreGage"):
        st2 = run_checks(cfg, st)
    assert "ERROR" in caplog.text
    assert isinstance(st2, type(st))


def test_wrong_function_name_caught_gracefully(tmp_path, caplog):
    _write_check(str(tmp_path), "TESTCHECK", fn_name="check_WRONGNAME")
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    import logging
    with caplog.at_level(logging.ERROR, logger="pyCoreGage"):
        st2 = run_checks(cfg, st)
    assert len(st2.issues) == 0


def test_multiple_rule_sets_both_executed(tmp_path):
    _write_check(str(tmp_path), "ZZZ", n=1)
    _write_check(str(tmp_path), "AAA", n=1)
    reg = pd.DataFrame([
        _reg_row("ZZZ001", "ZZZ"),
        _reg_row("AAA001", "AAA"),
    ])
    st  = make_state(reg)
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 2
    assert set(st2.issues["id"].tolist()) == {"ZZZ", "AAA"}


def test_active_no_rule_sets_not_executed(tmp_path):
    _write_check(str(tmp_path), "TESTCHECK", n=5)
    reg = pd.DataFrame([_reg_row("CHK001", "TESTCHECK", active="NO")])
    st  = make_state(reg)
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 0


def test_total_findings_count_logged(tmp_path, caplog):
    _write_check(str(tmp_path), "TESTCHECK", n=7)
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    import logging
    with caplog.at_level(logging.INFO, logger="pyCoreGage"):
        run_checks(cfg, st)
    assert "Total findings: 7" in caplog.text


def test_returns_updated_state_object(tmp_path):
    _write_check(str(tmp_path), "TESTCHECK", n=1)
    st  = make_state()
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert hasattr(st2, "issues")
    assert hasattr(st2, "rule_registry")
    assert hasattr(st2, "active_rules")


def test_domains_accessible_inside_check(tmp_path):
    check_code = (
        "import pandas as pd\n"
        "from pyCoreGage import collect_findings\n\n"
        "def check_TESTCHECK(state, cfg):\n"
        "    ae = state.domains.get('ae')\n"
        "    if ae is not None and not ae.empty:\n"
        "        df = pd.DataFrame({\n"
        "            'subj_id': ae['USUBJID'].tolist(),\n"
        "            'vis_id': [float('nan')] * len(ae),\n"
        "            'description': ['Found row'] * len(ae),\n"
        "        })\n"
        "        state = collect_findings(state, df, id='TESTCHECK')\n"
        "    return state\n"
    )
    with open(os.path.join(str(tmp_path), "TESTCHECK.py"), "w") as f:
        f.write(check_code)
    st = make_state()
    st.domains["ae"] = pd.DataFrame({"USUBJID": ["S1", "S2"]})
    cfg = _make_cfg(str(tmp_path))
    st2 = run_checks(cfg, st)
    assert len(st2.issues) == 2
