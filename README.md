# Secure Multi-Agent Tool Orchestration — Tunisia Tourism Analytics

**Problem Solving Course — 2BIS — Academic Year 2025-2026**

---

## Overview

This project implements a **multi-agent orchestration system** for analyzing tourism data in Tunisia, with:

- **Backtracking planner** — constrained search with pruning
- **Schema-validated tools** — pydantic input/output validation
- **Safety enforcement** — allow-lists for paths and HTTP hosts
- **Bounded retries** — tenacity-based retry with exponential backoff
- **Failure injection** — test mode for error recovery
- **Streamlit GUI** — observability interface for runs, traces, and metrics

---

## Architecture

```
Plan → Execute → Validate → Report
```

### Agents

- **Planner** — backtracking search over feasible step sequences
- **Executor** — runs schema-validated tools with isolated state per run
- **Critic** — validates final output for correctness

### Tools

- `read_csv_tool` — loads CSV from sandbox with path validation
- `compute_kpis` — calculates tourism KPIs (occupancy, revenue, top regions)
- `api_tool` — fetches weather data (Open-Meteo) with allow-list enforcement
- `report` — builds structured output + saves chart to disk

---

## Installation

```bash
# 1. Install dependencies (Windows)
py -m pip install -r requirements.txt

# For Linux/Mac:
python -m pip install -r requirements.txt
```

---

## Usage

### Run Scenario 1 (CSV Analysis)

```bash
cd PROJET_DS2
py main.py
# Choose: 1
```

### Run Scenario 2 (API Integration)

```bash
cd PROJET_DS2
py main.py
# Choose: 2
```

### Launch GUI

```bash
cd PROJET_DS2
py -m streamlit run gui/app.py
```

Then open http://localhost:8501 in your browser.

---

## Testing

```bash
cd PROJET_DS2
py -m pytest tests/ -v
```

### Test Coverage

- `test_security.py` — allow-list, path validation, redaction
- `test_tools.py` — schema validation, error handling
- `test_planner.py` — backtracking, pruning, stats
- `test_failure_injection.py` — missing file, path traversal, schema errors

---

## Project Structure

```
PROJET_DS2/
├── orchestrator/
│   ├── planner.py          # Backtracking planner
│   ├── executor.py         # Tool executor (isolated state)
│   ├── critic.py           # Output validator
│   └── run_manager.py      # Main orchestration loop
├── tools/
│   ├── schemas.py          # Pydantic input/output models
│   ├── read_csv_tool.py    # CSV loader with safety checks
│   ├── compute_kpis.py     # KPI computation
│   ├── api_tool.py         # HTTP client with allow-list
│   ├── report.py           # Report builder
│   └── visualisation.py    # Chart generation (non-blocking)
├── security/
│   └── allow_list.py       # Path/host validation + redaction
├── workflow/
│   ├── scenario1.py        # CSV analysis task
│   └── scenario2.py        # API integration task
├── tests/
│   ├── test_security.py
│   ├── test_tools.py
│   ├── test_planner.py
│   └── test_failure_injection.py
├── gui/
│   └── app.py              # Streamlit interface
├── data_synthetic/
│   ├── tourism_big.csv     # Main dataset (465 rows)
│   └── tourism_kpis.csv    # Smaller test dataset
├── logs/                   # Run logs (JSON)
├── main.py                 # CLI entry point
├── requirements.txt
└── README.md
```

---

## Evidence — Scenario 1 with Failure Injection

### Normal Run

```bash
py main.py
# Choose: 1
# Output: {"status": "success", "data": {...}}
```

### Injected Failure (missing file)

```bash
# Edit workflow/scenario1.py:
# file: "PROJET_DS2/data_synthetic/MISSING_FILE.csv"

py main.py
# Choose: 1
# Output: {"error": "FILE_NOT_FOUND: ...", "run_id": "RUN-...", "failed_step": "read_csv"}
```

Logs are saved to `logs/RUN-<uuid>.json` with full trace.

---

## Key Features

### 1. Backtracking Planner

- State: `(step_index, satisfied_objectives, budget_remaining)`
- Pruning rules:
  - Budget exhausted → prune
  - Step not feasible for task type → prune
  - Required objective already satisfied → skip
- Stats: `branches_explored`, `branches_pruned`, `depth_reached`

### 2. Schema Validation (Pydantic)

Every tool input/output is validated:

```python
class ReadCsvInput(BaseModel):
    file: str
    required_columns: list[str] = ["region", "occupancy_rate", "revenue"]
```

### 3. Safety Enforcement

- **Path validation** — blocks `../../etc/passwd` style attacks
- **HTTP allow-list** — only `api.open-meteo.com`, `localhost` allowed
- **Redaction** — secrets masked in logs and GUI

### 4. Bounded Retries

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _get_with_retry(url, timeout):
    ...
```

### 5. Concurrency Safety

Each `RunManager` instance has isolated state:
- Separate `Executor` per run
- No shared mutable state
- Per-run logs with unique `run_id`

---

## Limitations

- DP/memoization layer not yet implemented (Week 3 deliverable)
- Concurrency stress tests not yet added (Week 3 deliverable)
- GUI metrics dashboard shows placeholders (Week 4 deliverable)

---

## Authors

**Group:** [Your group name]  
**Course:** Problem Solving — 2BIS  
**Institution:** Higher Institute of Management of Tunis  
**Academic Year:** 2025-2026

---

## License

This project is for educational purposes only. Synthetic data is used throughout.
