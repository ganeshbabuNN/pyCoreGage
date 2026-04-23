"""
project_config.py — STUDY01_TRAIL01 path configuration.
Edit PROJECT_ROOT if you move this project to a different machine.
"""
import os
from pyCoreGage import CoreGageConfig

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

cfg = CoreGageConfig(
    project_name  = "STUDY01_TRAIL01",
    rule_registry = os.path.join(PROJECT_ROOT, "rules", "config", "rule_registry.xlsx"),
    trial_checks  = os.path.join(PROJECT_ROOT, "rules", "trial"),
    study_checks  = os.path.join(PROJECT_ROOT, "rules", "study"),
    inputs        = os.path.join(PROJECT_ROOT, "inputs"),
    reports       = os.path.join(PROJECT_ROOT, "outputs", "reports"),
    feedback      = os.path.join(PROJECT_ROOT, "outputs", "feedback"),
)
