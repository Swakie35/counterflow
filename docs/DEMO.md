# Reproducible local walkthrough

This walkthrough does not require production data or cloud deployment. Run the commands at this repository root.

## Prerequisites

Python 3.11+; make a virtual environment and install the project test extra.

## Setup and test

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
```

## Demonstrate the main path

```bash
python -m counterflow --report reports/generated/validation.json
```

## What to look for

- Observe the console or generated report; **do not substitute copied/synthetic screenshots for actual runtime output**.
- For algorithms, inspect tests around boundary conditions and compare behavior with the README.
- For Java demos, the test runner exercises the HTTP service or core worker behavior; the README includes manual server commands.
- Open `docs/ARCHITECTURE.md` to explain design trade-offs and limits.

## Interpretation

Past observations are available during each one-step evaluation; this is not an unattended multi-step forecast. Source data is synthetic and cannot establish commercial uplift.

If a command fails, capture the exact error and runtime version rather than claiming the repository is verified.
