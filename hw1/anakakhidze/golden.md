# Golden questions · HW1 free-event finder

Run in a new PowerShell window from `C:\Users\Administrator\goLocal-AI`. Exit codes were read with `echo $LASTEXITCODE` straight after each command.

## Golden question 1: free events in a normal week

- **Input:** `python hw1/anakakhidze/src/cli.py --from 2026-10-20 --to 2026-10-31`
- **Expected:** a JSON array with ids 3, 1 and 5, in that order. Paid events (2, 7) and the unknown-price event (4) are absent; id 6 is outside the range.
- **Actual:**
  ```json
  [
    {
      "id": 3,
      "title": "Open Studio Morning (fictional)",
      "venue": "Sample Makers Studio",
      "start": "2026-10-21T10:00:00+04:00",
      "source_url": "https://example.com/events/3"
    },
    {
      "id": 1,
      "title": "Riverside Film Night (fictional)",
      "venue": "Sample Riverside Yard",
      "start": "2026-10-24T19:00:00+04:00",
      "source_url": "https://example.com/events/1"
    },
    {
      "id": 5,
      "title": "Free Walk Downtown (fictional)",
      "venue": "Sample Old Town Square",
      "start": "2026-10-31T11:00:00+04:00",
      "source_url": "https://example.com/events/5"
    }
  ]
  ```
- **Exit code:** `0`
- **Pass or fail:** PASS
- **How I ran it:** PowerShell, `python ...cli.py --from 2026-10-20 --to 2026-10-31`, then `echo $LASTEXITCODE`.

## Golden question 2: no matches

- **Input:** `python hw1/anakakhidze/src/cli.py --from 2030-01-01 --to 2030-01-02`
- **Expected:** `[]` and exit code `0`.
- **Actual:** `[]`
- **Exit code:** `0`
- **Pass or fail:** PASS
- **How I ran it:** PowerShell, the command above, then `echo $LASTEXITCODE`.

## Golden question 3: a reversed date range is rejected

- **Input:** `python hw1/anakakhidze/src/cli.py --from 2026-10-31 --to 2026-10-20`
- **Expected:** an error message, no JSON, and exit code `2`.
- **Actual:** `error: --from must be on or before --to`
- **Exit code:** `2`
- **Pass or fail:** PASS
- **How I ran it:** PowerShell, the command above, then `echo $LASTEXITCODE`.

## Test suite

- **Command:** `python -m pytest hw1/anakakhidze -p no:cacheprovider -q`
- **Actual:** `18 passed in 0.47s`
- **Pass or fail:** PASS
