"""
test_utils.py — 14 test cases for load_inputs() and cleanup_text()
Mirrors the original R test-utils.R scenario by scenario.
"""

import os

import pandas as pd
import pytest

from pyCoreGage.utils import load_inputs, cleanup_text
from pyCoreGage.state import CoreGageConfig


def _cfg(inputs_dir: str) -> CoreGageConfig:
    return CoreGageConfig(inputs=inputs_dir)


def _write_csv(directory, name, df):
    df.to_csv(os.path.join(directory, name), index=False, na_rep="")


# ── load_inputs ───────────────────────────────────────────────────────────────

def test_nonexistent_dir_returns_empty(tmp_path):
    cfg = _cfg("/nonexistent/path/inputs")
    result = load_inputs(cfg)
    assert result == {}


def test_empty_inputs_dir_returns_empty(tmp_path):
    cfg = _cfg(str(tmp_path))
    result = load_inputs(cfg)
    assert result == {}


def test_single_csv_loaded_with_lowercase_name(tmp_path):
    _write_csv(str(tmp_path), "AE.csv", pd.DataFrame({"USUBJID": ["S1"], "AETERM": ["Rash"]}))
    result = load_inputs(_cfg(str(tmp_path)))
    assert "ae" in result


def test_multiple_csvs_loaded_as_separate_elements(tmp_path):
    _write_csv(str(tmp_path), "AE.csv", pd.DataFrame({"X": [1]}))
    _write_csv(str(tmp_path), "LB.csv", pd.DataFrame({"Y": [2]}))
    _write_csv(str(tmp_path), "CM.csv", pd.DataFrame({"Z": [3]}))
    result = load_inputs(_cfg(str(tmp_path)))
    assert sorted(result.keys()) == ["ae", "cm", "lb"]


def test_ae_csv_name_converted_to_lowercase_key(tmp_path):
    _write_csv(str(tmp_path), "AE.csv", pd.DataFrame({"USUBJID": ["S1"]}))
    result = load_inputs(_cfg(str(tmp_path)))
    assert "ae" in result
    assert "AE" not in result


def test_uppercase_extension_handled(tmp_path):
    _write_csv(str(tmp_path), "AE.CSV", pd.DataFrame({"USUBJID": ["S1"]}))
    result = load_inputs(_cfg(str(tmp_path)))
    assert len(result) == 1


def test_loaded_df_has_correct_row_count(tmp_path):
    df = pd.DataFrame({"USUBJID": [f"S{i}" for i in range(1, 11)]})
    _write_csv(str(tmp_path), "AE.csv", df)
    result = load_inputs(_cfg(str(tmp_path)))
    assert len(result["ae"]) == 10


def test_loaded_df_preserves_column_names(tmp_path):
    df = pd.DataFrame({"USUBJID": ["S1"], "AETERM": ["Rash"], "AESTDTC": ["2022-01-01"]})
    _write_csv(str(tmp_path), "AE.csv", df)
    result = load_inputs(_cfg(str(tmp_path)))
    for col in ["USUBJID", "AETERM", "AESTDTC"]:
        assert col in result["ae"].columns


def test_empty_csv_loads_as_zero_row_df(tmp_path):
    df = pd.DataFrame({"USUBJID": pd.Series(dtype=str)})
    _write_csv(str(tmp_path), "AE.csv", df)
    result = load_inputs(_cfg(str(tmp_path)))
    assert len(result["ae"]) == 0


def test_empty_string_in_csv_becomes_na(tmp_path):
    csv_content = "USUBJID,AETERM\nS1,\n"
    with open(os.path.join(str(tmp_path), "AE.csv"), "w") as f:
        f.write(csv_content)
    result = load_inputs(_cfg(str(tmp_path)))
    assert pd.isna(result["ae"]["AETERM"].iloc[0])


def test_na_string_in_csv_becomes_na(tmp_path):
    csv_content = "USUBJID,AETERM\nS1,NA\n"
    with open(os.path.join(str(tmp_path), "AE.csv"), "w") as f:
        f.write(csv_content)
    result = load_inputs(_cfg(str(tmp_path)))
    assert pd.isna(result["ae"]["AETERM"].iloc[0])


# ── cleanup_text ──────────────────────────────────────────────────────────────

def test_cleanup_removes_control_chars():
    x = "Hello\x01\x07World"
    assert cleanup_text(x) == "HelloWorld"


def test_cleanup_replaces_newline_with_space():
    assert cleanup_text("line1\nline2") == "line1 line2"


def test_cleanup_collapses_multiple_spaces():
    assert cleanup_text("too   many    spaces") == "too many spaces"


def test_cleanup_trims_whitespace():
    assert cleanup_text("  padded  ") == "padded"
