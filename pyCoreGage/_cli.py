"""
pyCoreGage._cli
===============
Command-line entry point.

Usage
-----
    pycoregage create TRIAL_ABC --path /my/projects
    pycoregage run               (from inside a project folder)
    pycoregage --version
"""

from __future__ import annotations

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pycoregage",
        description="pyCoreGage — Data Quality Check Framework",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print version and exit."
    )
    sub = parser.add_subparsers(dest="command")

    # pycoregage create <name> [--path <dir>]
    p_create = sub.add_parser("create", help="Scaffold a new project.")
    p_create.add_argument("name", help="Project / trial name.")
    p_create.add_argument(
        "--path", default=".", help="Parent directory (default: current dir)."
    )
    p_create.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing project."
    )

    # pycoregage run [--config <path>]
    p_run = sub.add_parser("run", help="Run checks from current project directory.")
    p_run.add_argument(
        "--config",
        default="rules/config/project_config.py",
        help="Path to project_config.py (default: rules/config/project_config.py).",
    )

    args = parser.parse_args(argv)

    if args.version:
        from pyCoreGage import __version__
        print(f"pyCoreGage {__version__}")
        return 0

    if args.command == "create":
        from pyCoreGage import create_project
        import os
        root = create_project(
            name=args.name,
            path=os.path.abspath(args.path),
            overwrite=args.overwrite,
        )
        print(f"\nProject created at: {root}")
        return 0

    if args.command == "run":
        import importlib.util, os
        cfg_path = os.path.abspath(args.config)
        if not os.path.isfile(cfg_path):
            print(f"ERROR: config not found: {cfg_path}", file=sys.stderr)
            return 1
        spec = importlib.util.spec_from_file_location("_project_config", cfg_path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cfg = mod.cfg

        from pyCoreGage import setup_coregage, load_inputs, run_checks, build_reports
        print("=" * 50 + " pyCoreGage : Starting Run " + "=" * 50)
        print(f"  Project : {cfg.project_name}")
        state         = setup_coregage(cfg)
        state.domains = load_inputs(cfg)
        state         = run_checks(cfg, state)
        build_reports(cfg, state)
        print("=" * 50 + " pyCoreGage : Run Complete " + "=" * 50)
        print(f">> Reports: {cfg.reports}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
