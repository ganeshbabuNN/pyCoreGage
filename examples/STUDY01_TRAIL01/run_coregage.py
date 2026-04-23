"""
run_coregage.py — STUDY01_TRAIL01 driver script (Python / pyCoreGage) 

Run from the STUDY01_TRAIL01/ folder:
    python run_coregage.py
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pyCoreGage import setup_coregage, load_inputs, run_checks, build_reports
from rules.config.project_config import cfg

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    print("=" * 50 + " pyCoreGage : Starting Run " + "=" * 50)
    print(f"  Project : {cfg.project_name}")

    state         = setup_coregage(cfg)
    state.domains = load_inputs(cfg)
    print(f"   Domains: {', '.join(k.upper() for k in state.domains)}")

    state         = run_checks(cfg, state)
    build_reports(cfg, state)

    print("=" * 50 + " pyCoreGage : Run Complete " + "=" * 50)
    print(f">> Reports : {cfg.reports}")
    print(f">> Findings: {len(state.issues)}")


if __name__ == "__main__":
    main()
