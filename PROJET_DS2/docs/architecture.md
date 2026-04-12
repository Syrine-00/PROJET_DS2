# System Architecture

## Overview
This project implements a multi-agent orchestration system to analyze tourism data in Tunisia.

## Agents

### Planner
Responsible for deciding which steps to execute based on the task type.

### Executor
Executes tools such as:
- CSV reading
- KPI computation
- API calls
- Report generation

### Critic
Validates the final output to ensure correctness.

## Workflow

Plan → Execute → Validate → Report

1. Planner selects steps
2. Executor runs tools
3. Critic validates results
4. Final report is generated

## Tools

- read_csv_tool: loads tourism dataset
- compute_kpis: calculates performance indicators
- api_tool: fetches external weather data
- report: formats output

## Data Flow

CSV → KPI computation → API enrichment → Final report