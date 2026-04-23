"""
test_counter.py — 7 test cases for count_valid()
"""

import pandas as pd
import pytest

from pyCoreGage.counter import count_valid


def _df(subj_ids, descs=None):
    n = len(subj_ids)
    if descs is None:
        descs = [f"Issue {i}" for i in range(n)]
    return pd.DataFrame({"subj_id": subj_ids, "description": descs})


def test_empty_df_returns_zero():
    assert count_valid(pd.DataFrame()) == 0


def test_none_returns_zero():
    assert count_valid(None) == 0


def test_all_positive_ids_counted():
    df = _df(["001", "002", "003"])
    assert count_valid(df) == 3


def test_no_unblind_codes_negative_ids_included():
    df = _df(["001", "-002"])
    assert count_valid(df) == 2


def test_negative_id_excluded_when_code_absent():
    df = _df(["001", "-002"], ["Normal issue", "Other issue"])
    assert count_valid(df, unblind_codes=["SENSITIVE_CODE"]) == 1


def test_negative_id_retained_when_code_present():
    df = _df(["001", "-002"], ["Normal issue", "Contains SENSITIVE_CODE here"])
    assert count_valid(df, unblind_codes=["SENSITIVE_CODE"]) == 2


def test_empty_unblind_codes_no_filtering():
    df = _df(["-001", "-002"])
    assert count_valid(df, unblind_codes=[]) == 2
