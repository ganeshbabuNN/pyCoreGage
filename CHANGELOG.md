## [1.0.0] — Initial Release

### Added
- `CoreGageConfig` dataclass — all project paths in one place
- `CoreGageState` dataclass — mutable run-time state passed through every function
- `setup_coregage()` — reads `rule_registry.xlsx`, builds active-rules dict
- `load_inputs()` — auto-discovers CSV and `.sas7bdat` files from `inputs/`
- `run_checks()` — dynamically imports check scripts via `importlib`, dispatches `check_{Rule_Set}(state, cfg)`
- `collect_findings()` — validates and appends findings DataFrames with full guard checks
- `count_valid()` — row counter with optional unblinding-code filtering
- `build_reports()` — merges saved issues, reads feedback, applies smart status management, writes six role-based Excel reports
- `create_project()` — scaffolds complete project folder from bundled templates
- CLI entry point: `pycoregage create` and `pycoregage run`
- 90 pytest test cases across 8 test modules (unit + integration)
- Sample study: AE, LB, DM domains with 8 check scripts and a full rule registry
- Bundled `rule_registry.xlsx` template and three project file templates
- `pyproject.toml` — PEP 517/518 compliant packaging
- `PUBLISH.md` — step-by-step PyPI publish guide with CI/CD workflow

### Notes
- Python port of [rCoreGage](https://github.com/ganeshbabuNN/rCoreGage)
- Requires Python ≥ 3.9, pandas ≥ 1.5.0, openpyxl ≥ 3.1.0
- Optional: `pyreadstat` for `.sas7bdat` support (`pip install "pyCoreGage[sas]"`)
