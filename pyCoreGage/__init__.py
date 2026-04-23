"""
pyCoreGage — Data Quality Check Framework for Clinical and Analytical Data
==========================================================================

A configuration-driven Python package for running domain-level data quality
checks and consolidating findings into structured Excel reports with
role-based feedback routing.

Quick start
-----------
>>> from pyCoreGage import (
...     CoreGageConfig, CoreGageState,
...     setup_coregage, load_inputs, run_checks,
...     collect_findings, count_valid, build_reports,
...     create_project,
... )

See the README for the complete usage guide.
"""

from .state import CoreGageConfig, CoreGageState
from .setup import setup_coregage
from .utils import load_inputs, cleanup_text
from .runner import run_checks
from .collector import collect_findings
from .counter import count_valid
from .reporter import build_reports
from .project import create_project

__version__ = "0.1.0"
__author__  = "Ganesh Babu G"
__email__   = "ganeshbabu346@gmail.com"
__license__ = "GPL-3.0"

__all__ = [
    # Data structures
    "CoreGageConfig",
    "CoreGageState",
    # Engine functions
    "setup_coregage",
    "load_inputs",
    "run_checks",
    "collect_findings",
    "count_valid",
    "build_reports",
    # Project scaffolding
    "create_project",
    # Utilities
    "cleanup_text",
    # Metadata
    "__version__",
]
