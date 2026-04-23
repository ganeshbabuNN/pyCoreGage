"""
project_config.py — Sample Study configuration.
Edit PROJECT_ROOT if you move this folder.
"""

import os
from pyCoreGage import CoreGageConfig

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

cfg = CoreGageConfig(
    project_name  = "SAMPLE_STUDY_01",
    rule_registry = os.path.join(PROJECT_ROOT, "rules", "config", "rule_registry.xlsx"),
    trial_checks  = os.path.join(PROJECT_ROOT, "rules", "trial"),
    study_checks  = os.path.join(PROJECT_ROOT, "rules", "study"),
    inputs        = os.path.join(PROJECT_ROOT, "inputs"),
    reports       = os.path.join(PROJECT_ROOT, "outputs", "reports"),
    feedback      = os.path.join(PROJECT_ROOT, "outputs", "feedback"),
)
