"""
pyCoreGage.project
==================
create_project() — scaffolds a complete pyCoreGage project folder from
bundled templates and the blank rule_registry.xlsx.
"""

from __future__ import annotations

import logging
import os
import shutil
from importlib import resources
from pathlib import Path

logger = logging.getLogger("pyCoreGage")

_DIRS = [
    "rules/config",
    "rules/trial",
    "rules/study",
    "inputs",
    "outputs/reports",
    "outputs/feedback/DM",
    "outputs/feedback/MW",
    "outputs/feedback/SDTM",
    "outputs/feedback/ADAM",
]

_GITIGNORE = """\
# pyCoreGage project .gitignore
inputs/
outputs/
__pycache__/
*.pyc
.env
"""


def create_project(name: str, path: str, overwrite: bool = False) -> str:
    """
    Scaffold a new pyCoreGage project folder.

    Creates the full directory structure, copies the bundled templates
    (``run_coregage.py``, ``project_config.py``, ``check_template.py``)
    and the blank ``rule_registry.xlsx`` into the new project.

    Parameters
    ----------
    name : str
        Project / trial name.  Used as the folder name.
    path : str
        Parent directory where the project folder will be created.
    overwrite : bool, optional
        Whether to overwrite an existing project at the same path.
        Default False.

    Returns
    -------
    str
        Absolute path to the created project root.

    Raises
    ------
    FileExistsError
        If the project folder already exists and *overwrite* is False.
    ValueError
        If *path* is empty.

    Examples
    --------
    >>> import tempfile
    >>> from pyCoreGage import create_project
    >>> root = create_project("TRIAL_ABC", tempfile.mkdtemp())
    >>> import os; os.path.isdir(root)
    True
    """
    if not path or not path.strip():
        raise ValueError(
            "'path' must be supplied. "
            "Use path=tempfile.mkdtemp() for testing or specify your project directory."
        )

    project_root = os.path.join(path, name)

    if os.path.isdir(project_root) and not overwrite:
        raise FileExistsError(
            f"Project folder already exists: {project_root}\n"
            "Set overwrite=True to overwrite."
        )

    logger.info(">> Creating pyCoreGage project '%s' at: %s", name, project_root)

    # ── Create folder structure ───────────────────────────────────────────────
    for d in _DIRS:
        os.makedirs(os.path.join(project_root, d), exist_ok=True)
    logger.info("  Created folder structure")

    # ── Copy templates from package ───────────────────────────────────────────
    try:
        # Python 3.9+
        tmpl_dir = resources.files("pyCoreGage") / "templates"
    except AttributeError:
        # Fallback for Python 3.8
        import importlib
        pkg = importlib.import_module("pyCoreGage")
        tmpl_dir = Path(pkg.__file__).parent / "templates"

    def _copy_template(src_name: str, dest_rel: str, substitutions: dict = None) -> None:
        src = os.path.join(str(tmpl_dir), src_name)
        dest = os.path.join(project_root, dest_rel)
        if not os.path.isfile(src):
            logger.warning("  Template not found: %s", src)
            return
        if substitutions:
            with open(src, encoding="utf-8") as f:
                content = f.read()
            for placeholder, value in substitutions.items():
                content = content.replace(placeholder, value)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            shutil.copy2(src, dest)
        logger.info("  Copied %s", os.path.basename(dest))

    subs = {
        "__PROJECT_NAME__": name,
        "__PROJECT_ROOT__": project_root.replace("\\", "/"),
    }

    _copy_template("run_coregage.py",    "run_coregage.py",                 subs)
    _copy_template("project_config.py",  "rules/config/project_config.py",  subs)
    _copy_template("check_template.py",  "rules/trial/check_template.py",   None)

    # ── Copy rule_registry.xlsx ───────────────────────────────────────────────
    try:
        data_dir = resources.files("pyCoreGage") / "data"
    except AttributeError:
        import importlib
        pkg = importlib.import_module("pyCoreGage")
        data_dir = Path(pkg.__file__).parent / "data"

    reg_src = os.path.join(str(data_dir), "rule_registry.xlsx")
    reg_dst = os.path.join(project_root, "rules/config/rule_registry.xlsx")
    if os.path.isfile(reg_src):
        shutil.copy2(reg_src, reg_dst)
        logger.info("  Copied rule_registry.xlsx")
    else:
        logger.warning("  rule_registry.xlsx not found in package data.")

    # ── Write .gitignore ──────────────────────────────────────────────────────
    with open(os.path.join(project_root, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(_GITIGNORE)

    logger.info("")
    logger.info("  pyCoreGage project '%s' created successfully.", name)
    logger.info("")
    logger.info("  Next steps:")
    logger.info("  1. Fill in rules/config/rule_registry.xlsx with check definitions")
    logger.info("  2. Write check scripts in rules/trial/ and rules/study/")
    logger.info("  3. Drop domain data files (.csv or .sas7bdat) into inputs/")
    logger.info("  4. Run: python run_coregage.py")

    return project_root
