"""
test_project.py — 7 test cases for create_project()
"""

import os
import pytest

from pyCoreGage.project import create_project


def test_create_project_makes_root_dir(tmp_path):
    root = create_project("TRIAL_ABC", str(tmp_path))
    assert os.path.isdir(root)


def test_create_project_returns_correct_path(tmp_path):
    root = create_project("TRIAL_XYZ", str(tmp_path))
    assert root == os.path.join(str(tmp_path), "TRIAL_XYZ")


def test_create_project_makes_all_required_dirs(tmp_path):
    root = create_project("MY_TRIAL", str(tmp_path))
    expected = [
        "rules/config", "rules/trial", "rules/study",
        "inputs",
        "outputs/reports",
        "outputs/feedback/DM",
        "outputs/feedback/MW",
        "outputs/feedback/SDTM",
        "outputs/feedback/ADAM",
    ]
    for d in expected:
        assert os.path.isdir(os.path.join(root, d)), f"Missing: {d}"


def test_create_project_copies_rule_registry(tmp_path):
    root = create_project("T1", str(tmp_path))
    reg = os.path.join(root, "rules", "config", "rule_registry.xlsx")
    assert os.path.isfile(reg)


def test_create_project_copies_templates(tmp_path):
    root = create_project("T2", str(tmp_path))
    assert os.path.isfile(os.path.join(root, "run_coregage.py"))
    assert os.path.isfile(os.path.join(root, "rules", "config", "project_config.py"))
    assert os.path.isfile(os.path.join(root, "rules", "trial", "check_template.py"))


def test_create_project_raises_if_exists_no_overwrite(tmp_path):
    create_project("T3", str(tmp_path))
    with pytest.raises(FileExistsError, match="already exists"):
        create_project("T3", str(tmp_path), overwrite=False)


def test_create_project_overwrites_when_flag_set(tmp_path):
    create_project("T4", str(tmp_path))
    root = create_project("T4", str(tmp_path), overwrite=True)
    assert os.path.isdir(root)
