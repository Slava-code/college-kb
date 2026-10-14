# Thresholds

Tunables that agents read before maintenance and writes. Scripts keep their own
copies where noted (`scripts/kb-schema.json`). Change a value here, not in a prompt.

```text
TRIAGE_MAX_DROPS_PER_RUN = 10          # inbox drops absorbed per triage run
TRIAGE_BATCH_MODE = true               # read the whole batch before writing any page
NEEDS_OWNER_MAX_QUESTIONS = 3          # questions a run may ask the student at the end
REMINDER_TIMEZONE = Etc/UTC            # set to your IANA zone, e.g. America/New_York
REMINDER_RELATIVE_ANCHOR = capture_or_triage_timestamp   # what "tomorrow" is relative to
REMINDER_DEFAULT_MORNING = 08:00       # time used for date-only reminders
REMINDER_DEFAULT_BEFORE_MINUTES = 30   # lead time before a timed event
READ_LATER_DEFAULT = next_morning      # when an undated read-later item comes due
WEEKEND_REFERENCE_DEFAULT = Saturday 10:00   # "this weekend"
STALE_ACTIVE_DAYS = 60                 # status: active page untouched this long → gardener flags it
OVERSIZED_LINES = 300                  # page longer than this → propose a split
MIN_LINES = 10                         # page shorter than this → propose merge or enrichment
NEW_PAGE_MIN_SENTENCES = 3             # minimum content before a new page is created
SEED_TEST_MIN_PAGES = 3                # pages that must want a new folder before it is created
ARCHIVE_STALE_MONTHS = 4               # finished-semester material older than this → propose archive
DIFF_CAP_FILES = 15                    # maintenance run aborts above this many changed files
DIFF_CAP_LINES = 600                   # ... or above this many changed lines
RETRIEVAL_FAILURES_PER_MONTH = 3       # misses in runs/retrieval-failures.md before adding search tooling
INDEX_GLOSSARY_BUDGET_LINES = 200      # INDEX.md + GLOSSARY.md together; above it, split per folder
DESCRIPTION_MAX_CHARS = 120            # mirrored in scripts/kb-schema.json description_max_chars
```
