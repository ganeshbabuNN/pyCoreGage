"""
test_collector.py — 10 test cases for collect_findings()
"""

import math
import pandas as pd
import pytest

from pyCoreGage.collector import collect_findings
from pyCoreGage.state import CoreGageState, _empty_issues, _empty_summary_log, _empty_review_log


def _fresh_state():
    return CoreGageState(
        issues      = _empty_issues(),
        summary_log = _empty_summary_log(),
        review_log  = _empty_review_log(),
        session     = {"sdate": "01Jan2024", "stime": "00:00"},
    )


def _df(n=2, desc_col="description"):
    return pd.DataFrame({
        "subj_id":  [f"S{i}" for i in range(1, n+1)],
        "vis_id":   [float("nan")] * n,
        desc_col:   [f"Issue {i}" for i in range(1, n+1)],
    })


def test_none_input_returns_state_unchanged():
    st = _fresh_state()
    st2 = collect_findings(st, None, id="CHK001")
    assert len(st2.issues) == 0


def test_missing_subj_id_returns_state_unchanged():
    st  = _fresh_state()
    df  = pd.DataFrame({"description": ["x"]})
    st2 = collect_findings(st, df, id="CHK001")
    assert len(st2.issues) == 0


def test_missing_description_col_returns_state_unchanged():
    st  = _fresh_state()
    df  = pd.DataFrame({"subj_id": ["S1"]})
    st2 = collect_findings(st, df, id="CHK001")
    assert len(st2.issues) == 0


def test_empty_description_returns_state_unchanged():
    st  = _fresh_state()
    df  = pd.DataFrame({"subj_id": ["S1"], "vis_id": [float("nan")], "description": [""]})
    st2 = collect_findings(st, df, id="CHK001")
    assert len(st2.issues) == 0


def test_valid_findings_appended_to_issues():
    st  = _fresh_state()
    st2 = collect_findings(st, _df(3), id="AECHK001")
    assert len(st2.issues) == 3
    assert all(st2.issues["id"] == "AECHK001")


def test_review_column_set_to_analyst():
    st  = _fresh_state()
    st2 = collect_findings(st, _df(2), id="CHK001")
    assert all(st2.issues["review"] == "ANALYST")


def test_summary_log_updated():
    st  = _fresh_state()
    st2 = collect_findings(st, _df(4), id="CHK001")
    assert len(st2.summary_log) == 1
    assert int(st2.summary_log.iloc[0]["nu"]) == 4


def test_description_truncated_to_200_chars():
    st  = _fresh_state()
    long_desc = "A" * 300
    df  = pd.DataFrame({"subj_id": ["S1"], "vis_id": [float("nan")], "description": [long_desc]})
    st2 = collect_findings(st, df, id="CHK001")
    assert len(st2.issues.iloc[0]["description"]) == 200


def test_custom_desc_col_renamed():
    st  = _fresh_state()
    df  = _df(2, desc_col="finding_text")
    st2 = collect_findings(st, df, id="CHK001", desc_col="finding_text")
    assert "description" in st2.issues.columns
    assert len(st2.issues) == 2


def test_duplicate_findings_deduplicated():
    st  = _fresh_state()
    df  = _df(2)
    st2 = collect_findings(st, df, id="CHK001")
    st3 = collect_findings(st2, df, id="CHK001")  # same df again
    assert len(st3.issues) == 2  # no new rows added
