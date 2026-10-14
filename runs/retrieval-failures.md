# Retrieval failures

Append one line whenever the KB plausibly should have answered a question but did not
(AGENTS.md §Read). A cheap eval: repeated misses say which page, alias, or tool is missing.
More than `RETRIEVAL_FAILURES_PER_MONTH` (THRESHOLDS.md) is the signal to add search tooling.

Format:

```text
- YYYY-MM-DD · question asked · looked in: pages/folders checked · miss: no-page | stale | alias-missing | in-inbox-only
```

When a later page fixes a miss, add a resolution stamp to that line:
`**Resolved YYYY-MM-DD → [[folder/page]]:** what now answers it`.

## Log

