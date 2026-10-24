# Contact List Cleaner

Merges messy contact exports (CRM dumps, event sign-ups, old spreadsheets) into **one clean, de-duplicated list**. Problem rows go to a separate file instead of being silently dropped.

```
python clean_contacts.py sample_data/crm_export.csv sample_data/event_signups.csv
```

## Before → after

Two exports with different column names and a mess of formats:

| Before | After |
|---|---|
| `  john SMITH ` | `John Smith` |
| `"O'BRIEN, PATRICK"` | `Patrick O'Brien` |
| `John.Smith@Gmail.com ` | `john.smith@gmail.com` |
| `555.201.3344`, `+1 555 772 0145`, `5554410099` | `(555) 201-3344`, `(555) 772-0145`, `(555) 441-0099` |
| `california`, `wa`, `New York` | `CA`, `WA`, `NY` |
| `03/14/2025`, `Feb 9 2025`, `9/3/25`, `2025/01/22` | `2025-03-14`, `2025-02-09`, `2025-09-03`, `2025-01-22` |
| `E-mail Address` / `email`, `Phone #` / `mobile` | One consistent set of columns |

```
Files read:        2
Rows read:         14
Blank rows:        1
Duplicates merged: 4
Needs review:      2
Clean contacts:    7
```

## Output

- **`clean_contacts.csv`**: one row per person, sorted by last name. Opens directly in Excel or Google Sheets.
- **`needs_review.csv`**: rows a person should check, with the reason (for example `invalid email`, `phone is not 10 digits`, `unreadable or impossible date` for 04/31/2025).
- **`report.txt`**: a line for every merge and flag, so nothing changes without a record.

## How duplicates are handled

Rows match on email first, then phone. When two rows are the same person, blanks are filled from the other row (for example, a missing company name), so no information is lost.

## Notes

- Original files are never modified.
- Recognizes common header spellings automatically (`E-mail Address`, `Phone #`, `date_joined`, `organization`, ...).
- Standard library only, Python 3.9+.
