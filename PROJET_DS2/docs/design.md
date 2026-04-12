# System Design

## Backtracking (BT)
If a step fails (e.g., API call), the system can:
- stop execution safely
- log the error
- allow retry in future improvements

## Pruning
Avoid unnecessary computations:
- Skip steps if data already available
- Prevent redundant processing

## Dynamic Programming (DP)
Store intermediate results:
- KPIs can be cached
- Avoid recomputation when data unchanged

## Threat Model

### Potential Risks
- Invalid file path
- Corrupted CSV data
- API failure or timeout
- Unexpected data format

### Mitigation
- Input validation
- Error handling
- Logging system