"""
run_coregage.py — Sample Study driver script.

Run from the sample_study/ folder:
    python run_coregage.py

Expected findings
-----------------
AECHK001 : S001, S004  — AE end date before start date
AECHK002 : S001, S005  — Missing AESEV
AECHK003 : S002        — Missing AEOUT
LBCHK001 : S001 (Na), S001 K, S002 (Glucose), S005 (Hgb) — out of range
LBCHK002 : S002        — Missing LBDTC
AEPRJ001 : S004        — Serious AE missing AEACN
AEPRJ002 : S004        — Missing AEDECOD
LBPRJ001 : S002        — Study-level LBDTC missing
"""

import logging
import sys
import os

# Allow running directly from sample_study/ or from pyCoreGage root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pyCoreGage import setup_coregage, load_inputs, run_checks, build_reports
from rules.config.project_config import cfg

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    print("=" * 55 + " pyCoreGage : Starting Run " + "=" * 55)
    print(f"  Project : {cfg.project_name}")

    state          = setup_coregage(cfg)
    state.domains  = load_inputs(cfg)
    print(f"   Domains: {', '.join(k.upper() for k in state.domains)}")

    state          = run_checks(cfg, state)
    build_reports(cfg, state)

    print("=" * 55 + " pyCoreGage : Run Complete " + "=" * 55)
    print(f">> Reports written to: {cfg.reports}")
    print(f">> Total findings    : {len(state.issues)}")


if __name__ == "__main__":
    main()
