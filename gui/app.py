"""
Streamlit GUI — observability interface for multi-agent orchestration.

Features:
- Task launcher (select scenario + inject failures)
- Run overview (list recent runs with status)
- Step timeline (chronological trace)
- Tool-call inspector (expandable details)
- Metrics dashboard (success rate, planner stats)
"""

import streamlit as st
import json
import os
from pathlib import Path

from orchestrator.run_manager import RunManager
from workflow import scenario1, scenario2


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tunisia Tourism Orchestrator",
    page_icon="🏖️",
    layout="wide",
)

st.title("🏖️ Multi-Agent Orchestration — Tunisia Tourism Analytics")
st.markdown("**Secure tool orchestration with backtracking planner + bounded retries**")

# ── Sidebar: Task Launcher ────────────────────────────────────────────────────

st.sidebar.header("🚀 Task Launcher")

scenario_choice = st.sidebar.selectbox(
    "Select Scenario",
    ["Scenario 1: CSV Analysis", "Scenario 2: API Integration"],
)

inject_failure = st.sidebar.checkbox("Inject Failure (missing file)", value=False)

if st.sidebar.button("▶️ Run Task"):
    if "Scenario 1" in scenario_choice:
        task = scenario1.build_task()
        if inject_failure:
            task["file"] = "PROJET_DS2/data_synthetic/MISSING_FILE.csv"
    else:
        task = scenario2.build_task()

    with st.spinner("Running orchestration..."):
        manager = RunManager(max_steps=10, max_retries_per_step=2)
        result = manager.run(task)

    st.session_state["last_run_id"] = manager.run_id
    st.session_state["last_result"] = result
    st.success(f"✅ Run completed: {manager.run_id}")

# ── Main: Run Overview ────────────────────────────────────────────────────────

st.header("📋 Recent Runs")

log_dir = Path("logs")
if log_dir.exists():
    log_files = sorted(log_dir.glob("RUN-*.json"), key=os.path.getmtime, reverse=True)
    
    if log_files:
        runs_data = []
        for log_file in log_files[:10]:  # show last 10
            with open(log_file) as f:
                logs = json.load(f)
            
            run_id = logs[0]["run_id"] if logs else "unknown"
            status = "✅ SUCCESS" if any("VALIDATED" in log.get("event", "") for log in logs) else "❌ FAILED"
            duration = "N/A"
            
            runs_data.append({"Run ID": run_id, "Status": status, "Duration": duration})
        
        st.dataframe(runs_data, use_container_width=True)
    else:
        st.info("No runs yet. Launch a task from the sidebar.")
else:
    st.info("No runs yet. Launch a task from the sidebar.")

# ── Step Timeline ─────────────────────────────────────────────────────────────

if "last_run_id" in st.session_state:
    st.header("🔍 Step Timeline")
    
    run_id = st.session_state["last_run_id"]
    log_path = Path(f"logs/{run_id}.json")
    
    if log_path.exists():
        with open(log_path) as f:
            logs = json.load(f)
        
        for log in logs:
            step_name = log.get("step_name", "unknown")
            event = log.get("event", "")
            timestamp = log.get("timestamp", "")
            
            if "SUCCESS" in event:
                st.success(f"✅ **{step_name}** — {event} — {timestamp}")
            elif "FAILED" in event:
                st.error(f"❌ **{step_name}** — {event} — {timestamp}")
            elif "STARTED" in event:
                st.info(f"▶️ **{step_name}** — {event} — {timestamp}")
            else:
                st.write(f"📌 **{step_name}** — {event} — {timestamp}")
            
            # Expandable metadata
            if "metadata" in log:
                with st.expander(f"🔎 Details for {step_name}"):
                    st.json(log["metadata"])

# ── Metrics Dashboard ─────────────────────────────────────────────────────────

st.header("📊 Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Runs", len(list(log_dir.glob("RUN-*.json"))) if log_dir.exists() else 0)

with col2:
    st.metric("Success Rate", "N/A")  # TODO: compute from logs

with col3:
    st.metric("Avg Steps", "N/A")  # TODO: compute from logs

st.markdown("---")
st.caption("Built with Streamlit • Secure Multi-Agent Orchestration for Tunisia Economy")
