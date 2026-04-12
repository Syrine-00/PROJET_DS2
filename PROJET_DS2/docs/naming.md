# Naming Conventions

## Run ID
Each execution has a unique identifier:
- Format: UUID
- Example: 3f8c1c2e-9a3e-4d2a-bc7f-123456789abc

## Step Names
Steps follow simple naming:
- read_csv
- compute_kpis
- api_call
- report

## Journal Events
Each step produces a log entry

### Status values:
- success
- error

### Example:
{
  "step": "read_csv",
  "status": "success"
}