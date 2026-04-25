# Week 2 Implementation Summary

## Deliverables Completed

### ✅ 1. Tool Executors + Schema Validation + Safety Allow-Lists

**Files created:**
- `security/allow_list.py` — path validation, HTTP allow-list, redaction
- `tools/schemas.py` — Pydantic models for all tool inputs/outputs
- `tools/read_csv_tool.py` — CSV loader with safety checks
- `tools/compute_kpis.py` — KPI computation with schema validation
- `tools/api_tool.py` — HTTP client with allow-list + bounded retries (tenacity)
- `tools/report.py` — Report builder
- `tools/visualisation.py` — Chart generation (non-blocking, saves to disk)

**Key features:**
- Every tool input/output validated with Pydantic
- Path traversal protection (sandbox enforcement)
- HTTP host allow-list (`api.open-meteo.com`, `localhost` only)
- Secret redaction in logs and GUI
- Bounded retries with exponential backoff (tenacity)

---

### ✅ 2. Baseline Loop with Bounded Retries/Steps

**Files created/updated:**
- `orchestrator/run_manager.py` — main orchestration loop
- `orchestrator/executor.py` — tool executor with isolated state
- `orchestrator/critic.py` — output validator

**Key features:**
- Max-step policy enforcement (default: 10 steps)
- Bounded retries per step (default: 2 retries, exponential backoff)
- Per-run isolated state (no shared mutable state)
- Structured logging with redaction
- Graceful failure handling (early exit on error)

---

### ✅ 3. Backtracking Planner with Pruning

**Files created:**
- `orchestrator/planner.py` — backtracking search over feasible plans

**Algorithm:**
- **State:** `(step_index, satisfied_objectives, budget_remaining)`
- **Decision:** which tool to call next from candidate sequences
- **Pruning rules:**
  - Budget exhausted → prune
  - Step not feasible for task type → prune
  - Required objective already satisfied → skip
- **Stats tracked:** branches_explored, branches_pruned, depth_reached, plan_found

**Candidate sequences:**
- CSV tasks: `[read_csv, compute_kpis, report]` or `[read_csv, report]` (fallback)
- API tasks: `[call_api, report]` or `[call_api, fetch_weather, report]` (enriched)

---

### ✅ 4. Scenario 1 End-to-End + Failure Injection Evidence

**Files created:**
- `docs/EVIDENCE_SCENARIO1.md` — full evidence document with 4 test cases

**Test cases:**
1. **Normal execution** — 465-row CSV → KPIs → report (SUCCESS)
2. **Missing file** — FILE_NOT_FOUND error, safe stop
3. **Path traversal** — SAFETY_BLOCK, no file system access
4. **Schema mismatch** — SCHEMA_ERROR, validation failure

**Metrics:**
- Task success rate: 100% (normal runs)
- Tool grounding score: 100% (all calls validated)
- Failure recovery: 100% (all injected failures stopped safely)
- Security blocks: 1 (path traversal blocked)

---

### ✅ 5. Unit Tests

**Files created:**
- `tests/test_security.py` — allow-list, path validation, redaction
- `tests/test_tools.py` — schema validation, error handling
- `tests/test_planner.py` — backtracking, pruning, stats
- `tests/test_failure_injection.py` — missing file, path traversal, schema errors

**Test coverage:**
- Security layer: 6 tests
- Tool layer: 5 tests
- Planner: 4 tests
- Failure injection: 3 tests
- **Total: 18 unit tests**

---

### ✅ 6. Initial GUI Skeleton

**Files created:**
- `gui/app.py` — Streamlit interface

**Features implemented:**
- Task launcher (select scenario + inject failures)
- Run overview (list recent runs with status)
- Step timeline (chronological trace with expandable metadata)
- Metrics dashboard (placeholders for Week 4)

**To run:**
```bash
streamlit run gui/app.py
```

---

## Project Structure (Updated)

```
PROJET_DS2/
├── orchestrator/
│   ├── planner.py          ✅ NEW — Backtracking planner
│   ├── executor.py         ✅ REWRITTEN — Isolated state + step name fix
│   ├── critic.py           ✅ FIXED — Explicit return True
│   └── run_manager.py      ✅ REWRITTEN — Bounded retries + max steps
├── tools/
│   ├── schemas.py          ✅ NEW — Pydantic models
│   ├── read_csv_tool.py    ✅ REWRITTEN — Safety checks
│   ├── compute_kpis.py     ✅ REWRITTEN — Schema validation
│   ├── api_tool.py         ✅ REWRITTEN — Allow-list + retries
│   ├── report.py           ✅ REWRITTEN — Non-blocking
│   └── visualisation.py    ✅ REWRITTEN — Saves to disk
├── security/               ✅ NEW
│   └── allow_list.py       ✅ NEW — Path/host validation + redaction
├── workflow/
│   ├── scenario1.py        ✅ FIXED — Correct file path
│   └── scenario2.py        (unchanged)
├── tests/                  ✅ NEW
│   ├── test_security.py    ✅ NEW
│   ├── test_tools.py       ✅ NEW
│   ├── test_planner.py     ✅ NEW
│   └── test_failure_injection.py ✅ NEW
├── gui/                    ✅ NEW
│   └── app.py              ✅ NEW — Streamlit interface
├── docs/
│   ├── EVIDENCE_SCENARIO1.md ✅ NEW
│   └── WEEK2_IMPLEMENTATION.md ✅ NEW (this file)
├── data_synthetic/         (unchanged)
├── logs/                   (auto-generated)
├── main.py                 ✅ FIXED — Better output formatting
├── requirements.txt        ✅ NEW
├── README.md               ✅ NEW
├── run_tests.sh            ✅ NEW
└── run_tests.bat           ✅ NEW
```

---

## Bugs Fixed

1. ✅ **File path in scenario1.py** — changed to `PROJET_DS2/data_synthetic/tourism_big.csv`
2. ✅ **Executor state bug** — `self.kpis` now set correctly in `compute_kpis` step
3. ✅ **Step name mismatch** — removed `process_api`, kept `call_api` and `fetch_weather`
4. ✅ **Critic return value** — explicit `return True` added
5. ✅ **Visualization blocking** — `plt.show()` removed, chart saved to disk
6. ✅ **Missing return statements** — Executor now returns result for all steps

---

## Dependencies Added

```
pandas>=2.0.0
pydantic>=2.0.0
tenacity>=8.2.0
requests>=2.31.0
pytest>=7.4.0
matplotlib>=3.7.0
streamlit>=1.28.0
structlog>=23.1.0
```

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Scenario 1 (CLI)

```bash
python main.py
# Choose: 1
```

### 3. Run tests

```bash
pytest tests/ -v
```

### 4. Launch GUI

```bash
streamlit run gui/app.py
```

---

## Next Steps (Week 3)

- [ ] Implement DP/memoization layer
- [ ] Add BT vs DP empirical comparison
- [ ] Implement Scenario 2 end-to-end + failure injection
- [ ] Add concurrency stress tests
- [ ] Improve GUI metrics dashboard (compute from logs)

---

## Evidence Checklist

✅ Scenario 1 transcript + output  
✅ Scenario 1 failure-injection evidence (4 test cases)  
✅ Tool schemas validated (Pydantic)  
✅ Backtracking implemented with pruning  
✅ Unit tests (18 tests across 4 files)  
✅ GUI skeleton (Streamlit)  
✅ README with reproducible commands  
✅ Logs saved to disk (JSON format)  

**Week 2 deliverables: 100% complete**
