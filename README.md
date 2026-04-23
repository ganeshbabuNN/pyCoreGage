# pyCoreGage

![version](https://img.shields.io/badge/version-0.1.0-blue)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-GPL--3.0-green)
![tests](https://img.shields.io/badge/tests-75%20passed-brightgreen)

> **Data Quality Check Framework for Clinical and Analytical Data**

pyCoreGage is a configuration-driven Python package for running
domain-level data quality checks and consolidating findings into
structured Excel reports with role-based feedback routing. It is the
Python port of the R package [rCoreGage](https://github.com/ganeshbabuNN/rCoreGage).

---

## Table of Contents

1. [Why pyCoreGage](#1-why-pycoregage)
2. [Architecture — Two Layers](#2-architecture--two-layers)
3. [Installation](#3-installation)
4. [Quick Start](#4-quick-start)
5. [Project Structure](#5-project-structure)
6. [rule\_registry.xlsx — Check Definitions](#6-rule_registryxlsx--check-definitions)
7. [How It Works](#7-how-it-works)
8. [Writing Check Scripts](#8-writing-check-scripts)
9. [API Reference](#9-api-reference)
10. [Console Output Reference](#10-console-output-reference)
11. [Publishing to PyPI](#11-publishing-to-pypi)

---

## 1. Why pyCoreGage

Clinical data quality checking typically involves:

- Running the same checks across dozens of domains (AE, LB, CM, VS …)
- Separating trial-specific rules from study-wide rules
- Routing findings to different roles (DM, MW, SDTM, ADaM) and tracking responses
- Carrying reviewer notes forward across repeated runs without losing history

| Problem | pyCoreGage solution |
|---|---|
| Engine scattered across trials | Engine installed once via `pip install pyCoreGage` |
| Hard-coded paths | Single `project_config.py` per project |
| No role separation in reports | Four separate report channels (DM / MW / SDTM / ADAM) |
| Feedback lost between runs | Structured feedback folders merged on every re-run |
| R-only tooling | Pure Python — works anywhere Python runs |

---

## 2. Architecture — Two Layers

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 1 — pyCoreGage PACKAGE  (pip install once)            │
│                                                              │
│  pyCoreGage/                                                 │
│    setup.py      setup_coregage()   reads rule_registry      │
│    runner.py     run_checks()       loops and executes scripts│
│    reporter.py   build_reports()    merges feedback + xlsx   │
│    collector.py  collect_findings() appends findings to state│
│    counter.py    count_valid()      counts observations       │
│    project.py    create_project()   scaffolds new project    │
│    utils.py      load_inputs()      reads domain data files  │
│    state.py      CoreGageState      mutable run state        │
│    _cli.py       pycoregage CLI     command-line entry point │
│                                                              │
│  pyCoreGage/data/rule_registry.xlsx   blank registry template│
│  pyCoreGage/templates/                project file templates │
└──────────────────────────────────────────────────────────────┘
                        │
          create_project("TRIAL_ABC")
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  LAYER 2 — USER PROJECT  (one folder per trial/study)        │
│                                                              │
│  TRIAL_ABC/                                                  │
│    run_coregage.py          driver — python run_coregage.py  │
│    rules/                                                    │
│      config/                                                 │
│        rule_registry.xlsx   check definitions (user fills)  │
│        project_config.py    all paths in one place          │
│      trial/                 trial-level check scripts       │
│        AE.py  LB.py  CM.py  check_AE(state, cfg) …         │
│      study/                 study-level check scripts       │
│        AE_study.py …        check_AE_study(state, cfg) …   │
│    inputs/                  drop domain CSV / SAS7BDAT here │
│    outputs/                                                  │
│      reports/               Excel reports written here      │
│      feedback/              reviewer feedback placed here   │
│        DM/  MW/  SDTM/  ADAM/                               │
└──────────────────────────────────────────────────────────────┘
```

**The key separation:** the engine (Layer 1) never changes between trials.
Only check scripts, `rule_registry.xlsx`, and `inputs/` change per trial.

---

## 3. Installation

### From PyPI (stable)

```bash
pip install pyCoreGage
```

### With SAS file support

```bash
pip install "pyCoreGage[sas]"
```

### Development install

```bash
git clone https://github.com/ganeshbabunn/pyCoreGage
cd pyCoreGage
pip install -e ".[dev]"
```

### Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pandas` | >= 1.5.0 | Data manipulation in check scripts |
| `openpyxl` | >= 3.1.0 | Read/write Excel reports |

Optional:

| Package | Purpose |
|---|---|
| `pyreadstat` | Read `.sas7bdat` files from `inputs/` |

### Requirements

- Python >= 3.9
- Works on Windows, macOS, Linux

---

## 4. Quick Start

```python
# Step 1 — Install (once)
# pip install pyCoreGage

# Step 2 — Create a new project (once per trial)
from pyCoreGage import create_project

create_project(
    name = "TRIAL_ABC",
    path = "/my/projects",
)

# Step 3 — Fill in rules/config/rule_registry.xlsx
#           (Trial sheet + Study sheet — see Section 6)

# Step 4 — Write check scripts in rules/trial/ and rules/study/
#           (copy check_template.py and implement your logic)

# Step 5 — Drop domain data files into inputs/
#           AE.csv, LB.csv, CM.csv …  (CSV or .sas7bdat)

# Step 6 — Run
# python run_coregage.py
# — or —
# pycoregage run
```

**Or via CLI:**

```bash
pycoregage create TRIAL_ABC --path /my/projects
cd /my/projects/TRIAL_ABC
# … fill registry, write checks, drop data …
pycoregage run
```

**Expected console output:**

```
=== pyCoreGage : Starting Run ===
  Project : TRIAL_ABC
>> [setup] Starting CoreGage initialisation ...
  Sheet 'Trial' rows    : 5
  Sheet 'Study' rows    : 3
  Active: 8 ON  /  0 OFF
>> [setup] Initialisation complete.
   AE.csv -> domains['ae']  (81 rows)
   LB.csv -> domains['lb']  (1003 rows)
>>>>>>>>>>>>>>>>>>>> Executing: AE <<<<<<<<<<<<<<<<<<<<
  >> [collector] Appending 5 finding(s) for: AECHK001
  >> [collector] Appending 2 finding(s) for: AECHK002
>>>>>>>>>>>>>>>>>>>> Executing: LB <<<<<<<<<<<<<<<<<<<<
  >> [collector] Appending 12 finding(s) for: LBCHK001
>> [runner] All checks executed. Total findings: 19
>> [reporter] Starting consolidation ...
  -------------------------------------------------------
  Feedback summary:
    Notes  : analyst notes: 0  |  reviewer notes: 0
    Status : open: 19  |  queried: 0  |  closed: 0
  -------------------------------------------------------
  Writing: DM_issues.xlsx
  Writing: all_open.xlsx
=== pyCoreGage : Run Complete ===
>> Reports written to: /my/projects/TRIAL_ABC/outputs/reports
```

---

## 5. Project Structure

After `create_project()`, your folder contains:

```
TRIAL_ABC/
├── run_coregage.py              ← run this
├── .gitignore
├── rules/
│   ├── config/
│   │   ├── rule_registry.xlsx   ← fill in check definitions
│   │   └── project_config.py    ← edit paths if you move the folder
│   ├── trial/
│   │   └── check_template.py    ← copy and rename for each domain
│   └── study/
├── inputs/                      ← drop AE.csv, LB.csv … here
└── outputs/
    ├── reports/                 ← Excel reports appear here
    └── feedback/
        ├── DM/                  ← DM reviewer places updated files here
        ├── MW/
        ├── SDTM/
        └── ADAM/
```

---

## 6. rule\_registry.xlsx — Check Definitions

The registry has two sheets: **Trial** and **Study**.

| Column | Type | Description |
|---|---|---|
| `Category` | str | Domain category (e.g. "Adverse Events") |
| `Subcategory` | str | Sub-category (e.g. "Date Checks") |
| `ID` | str | Unique check identifier (e.g. `AECHK001`) |
| `Active` | Yes/No | Set to `No` to disable without deleting |
| `DM_Report` | Yes/No | Include in DM report |
| `MW_Report` | Yes/No | Include in MW report |
| `SDTM_Report` | Yes/No | Include in SDTM report |
| `ADAM_Report` | Yes/No | Include in ADaM report |
| `Rule_Set` | str | Script name without `.py` (e.g. `AE`) |
| `Description` | str | Human-readable check description |
| `Notes` | str | Implementation notes |

**Rule\_Set** determines which script is sourced. If `Rule_Set = "AE"`,
the engine loads `rules/trial/AE.py` and calls `check_AE(state, cfg)`.
For the Study sheet it loads from `rules/study/`.

---

## 7. How It Works

```
setup_coregage(cfg)
       │
       ▼  reads rule_registry.xlsx → CoreGageState
load_inputs(cfg)
       │
       ▼  reads inputs/*.csv → state.domains{"ae": df, "lb": df, …}
run_checks(cfg, state)
       │
       ├─ for each active Rule_Set in Trial sheet:
       │       import rules/trial/{Rule_Set}.py
       │       call check_{Rule_Set}(state, cfg)
       │               └─ collect_findings(state, df, id="AECHK001")
       │
       └─ for each active Rule_Set in Study sheet:
               import rules/study/{Rule_Set}.py
               call check_{Rule_Set}(state, cfg)
build_reports(cfg, state)
       │
       ├─ import previously saved all_open.xlsx + all_closed.xlsx
       ├─ read feedback from feedback/DM/, MW/, SDTM/, ADAM/
       ├─ merge: status tracking, auto-close, re-open
       └─ write: DM_issues, MW_issues, SDTM_issues, ADAM_issues,
                 all_open, all_closed
```

### Smart status management

- New findings → status `open`
- Findings that disappear from data → auto-closed with tag `[auto-closed — finding no longer present]`
- Findings closed by reviewer → permanently closed
- Findings re-appearing after analyst closure → re-opened with tag `[Was closed but re-appeared]`

---

## 8. Writing Check Scripts

### Minimal example — date check (trial level)

```python
# rules/trial/AE.py

import pandas as pd
from pyCoreGage import collect_findings


def check_AE(state, cfg):
    ae = state.domains.get("ae")
    if ae is None or ae.empty:
        return state

    active_rules = state.active_rules

    if active_rules.get("AECHK001"):
        sub = ae.copy()
        sub["st"] = pd.to_datetime(sub["AESTDTC"], errors="coerce")
        sub["en"] = pd.to_datetime(sub["AEENDTC"], errors="coerce")
        result = sub[sub["en"].notna() & sub["st"].notna() & (sub["en"] < sub["st"])].copy()

        result["subj_id"]     = result["USUBJID"]
        result["vis_id"]      = float("nan")
        result["description"] = (
            "End (" + result["en"].dt.strftime("%d%b%Y") +
            ") before start (" + result["st"].dt.strftime("%d%b%Y") +
            ") for: " + result["AETERM"]
        )
        state = collect_findings(
            state,
            result[["subj_id", "vis_id", "description"]],
            id="AECHK001",
        )

    return state
```

### Cross-domain study-level check

```python
# rules/study/DM_study.py

import pandas as pd
from pyCoreGage import collect_findings


def check_DM_study(state, cfg):
    ae = state.domains.get("ae")
    dm = state.domains.get("dm")
    active_rules = state.active_rules

    if active_rules.get("DMPRJ001") and ae is not None and dm is not None:
        ae_subjects = set(ae["USUBJID"].dropna())
        dm_subjects = set(dm["USUBJID"].dropna())
        missing = ae_subjects - dm_subjects

        if missing:
            result = pd.DataFrame({
                "subj_id":     list(missing),
                "vis_id":      [float("nan")] * len(missing),
                "description": [f"Subject {s} has AE but no DM record" for s in missing],
            })
            state = collect_findings(state, result, id="DMPRJ001")

    return state
```

### Rules for check scripts

1. The file must be named `{Rule_Set}.py` — e.g. `AE.py` for `Rule_Set = "AE"`
2. The function must be named `check_{Rule_Set}(state, cfg)` — e.g. `check_AE`
3. Always return `state` at the end
4. Call `collect_findings()` once per check ID
5. The findings DataFrame must have columns: `subj_id`, `vis_id`, `description`

---

## 9. API Reference

### `setup_coregage(cfg) → CoreGageState`

Reads `rule_registry.xlsx`, builds the active-rules switch dict, returns
a fresh `CoreGageState`.

### `load_inputs(cfg) → dict[str, DataFrame]`

Reads all `.csv` (and optionally `.sas7bdat`) files from `cfg.inputs`.
Returns a dict keyed by lowercase filename stem: `{"ae": df, "lb": df}`.

### `run_checks(cfg, state) → CoreGageState`

Iterates active rule sets, dynamically imports each check script,
calls `check_{Rule_Set}(state, cfg)`.

### `collect_findings(state, df, id, desc_col="description", sobs=True, unblind_codes=None) → CoreGageState`

Validates and appends a findings DataFrame to `state.issues`.

| Parameter | Type | Description |
|---|---|---|
| `state` | `CoreGageState` | Current run state |
| `df` | `DataFrame` | Findings with `subj_id`, `vis_id`, `description` |
| `id` | `str` | Check ID matching registry |
| `desc_col` | `str` | Alternate description column name |
| `sobs` | `bool` | Flag for subject-observation limiting |
| `unblind_codes` | `list[str]` | Topic codes for unblinding protection |

### `count_valid(df, unblind_codes=None) → int`

Returns row count, optionally excluding unblinding-risk rows.

### `build_reports(cfg, state) → None`

Merges saved issues + feedback, writes six Excel reports to `cfg.reports`.

### `create_project(name, path, overwrite=False) → str`

Scaffolds a complete project folder. Returns the project root path.

### `CoreGageConfig`

```python
from pyCoreGage import CoreGageConfig

cfg = CoreGageConfig(
    project_name  = "TRIAL_ABC",
    rule_registry = "/path/to/rules/config/rule_registry.xlsx",
    trial_checks  = "/path/to/rules/trial",
    study_checks  = "/path/to/rules/study",
    inputs        = "/path/to/inputs",
    reports       = "/path/to/outputs/reports",
    feedback      = "/path/to/outputs/feedback",
)
```

---

## 10. Console Output Reference

| Message | Meaning |
|---|---|
| `Active: 8 ON / 0 OFF` | 8 checks enabled, 0 disabled |
| `AE.csv -> domains['ae'] (81 rows)` | AE domain loaded with 81 rows |
| `>> [collector] Appending 5 finding(s) for: AECHK001` | 5 findings collected |
| `WARNING: Check script not found: AE.py -- skipping.` | Script missing — check Rule_Set in registry |
| `ERROR in rule set AE: …` | Exception in check script — other checks continue |
| `[auto-closed — finding no longer present]` | Finding disappeared from data on re-run |
| `[Was closed but re-appeared]` | Previously closed finding is back in data |

---

## 11. Publishing to PyPI

See [PUBLISH.md](PUBLISH.md) for the step-by-step guide to publish pyCoreGage
to PyPI, including TestPyPI dry-run, versioning, and release checklist.

---

## License

GPL-3.0-or-later © Ganesh Babu G

## Citation

```
pyCoreGage: Data Quality Check Framework for Clinical and Analytical Data.
https://github.com/ganeshbabunn/pyCoreGage
```
