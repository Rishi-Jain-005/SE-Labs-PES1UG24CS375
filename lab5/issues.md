# Lab 5 – Static Code Analysis: Issues Found and Fixed

**Name:** Rishi Jain  **SRN:** PES1UG24CS375
**File analysed:** `scholarship_system.py` (Student Scholarship Eligibility Screener)

**Results:** Pylint 4.69/10 → 10.00/10 · Bandit 2 issues (1 Medium, 1 Low) → 0 · Flake8 12 findings → 0

Line numbers refer to the **original** file. Ordered by severity.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| `eval()` on a user-supplied formula | Security (Bandit B307 Medium; Pylint W0123) | 12 (input at 55–56) | `eval(MERIT_FORMULA)` runs whatever the user types at the "Merit formula" prompt, so typing `__import__("os").system(...)` executes arbitrary commands (code injection / RCE). | Replaced `eval` with an AST-based evaluator that allows only numbers, the names `gpa`/`credits`, and `+ - * /`. Anything else raises `ValueError`. The formula is also validated before use and falls back to the default if invalid. |
| Missing input validation (not flagged by any tool) | Logic bug | 15–19, 53 | Applicant U003 (GPA 12.5, credits −3, income −1) gets a score of 119 and is **shortlisted**. Out-of-range GPA, negative credits and negative income were accepted. | Added `validate_scores()`: GPA must be 0–10, credits ≥ 0, income ≥ 0, all numeric. Invalid applicants are stored as not eligible with an error message and logged. |
| Missing income silently treated as 0 (not flagged) | Logic bug | 17, 54 | `test_scores.get("income", 0)` means an applicant with no income data (U004) passes the income check as if they earned nothing. | Income is now required; a missing value is rejected with "income is missing or not a number". |
| Mutable default argument `logs=[]` | Bug (Pylint W0102) | 14 | The same list is shared across every call, so logs from different calls leak into one another. | Default changed to `None`; a fresh list is created inside the function. `main()` now passes its own list and prints it. |
| Bare `except:` with `pass` | Bug / Security (Bandit B110 Low; Pylint W0702; Flake8 E722) | 36–38 | Swallows every error, including `KeyboardInterrupt`, and silently hides corrupted or unreadable files. | Catch `FileNotFoundError` (normal first run) and `(OSError, json.JSONDecodeError)` separately, with a warning on stderr for real failures. |
| Files opened without `with` / encoding | Bug (Pylint R1732, W1514) | 29–31, 36 | `open()` without `with` can leak the file handle if an error occurs before `close()`; no encoding is specified. | Used `with open(..., encoding="utf-8")` and `json.dump`/`json.load`. |
| `global` statements / mutable global state | Design (Pylint W0603) | 25, 34 | `change_formula` and `load_results` rebind module globals, which makes the code hard to test and reason about. | Removed `change_formula`; the formula is passed as a parameter. `load_results` uses `results.clear()` / `results.update()` instead of rebinding. |
| Redefining built-in `credits` | Style (Pylint W0622) | 11, 16 | Parameter and variable named `credits` shadow Python's built-in. | Renamed to `credit_points` (the formula variable stays `credits` for users). |
| Unused imports `math`, `sys` | Style (Pylint W0611; Flake8 F401) | 2, 3 | Dead imports clutter the file. | Removed `math`; `sys` is now used for the warning on stderr. |
| `== True` comparison | Style (Pylint C0121; Flake8 E712) | 43 | Redundant comparison to a boolean. | Changed to `if record["eligible"]:`. |
| Non-snake_case name `printShortlist` | Style (Pylint C0103) | 40 | Violates PEP 8 naming. | Renamed to `print_shortlist`. |
| Missing module and function docstrings | Documentation (Pylint C0114, C0116) | 1, 11, 14, 24, 28, 33, 40, 46 | No explanation of what the module or functions do. | Added a module docstring and one-line docstrings to every function. |
| `%` string formatting | Style (Pylint C0209) | 21 | Old-style formatting. | Replaced with an f-string. |
| Missing blank lines between definitions | Formatting (Flake8 E302 ×6, E305) | 11, 14, 24, 28, 33, 40, 46, 59 | PEP 8 requires two blank lines around top-level functions. | Added the blank lines. |
| `main()` runs on import (not flagged) | Design | 59 | Importing the module immediately runs the program and waits for `input()`. | Wrapped in `if __name__ == "__main__":`. |

## Commits made (one per tool)

1. **Bandit** – replace `eval` with a safe evaluator and remove the `except: pass`.
2. **Pylint** – docstrings, mutable default, validation, `with open`, naming, globals, unused imports (score 4.69 → 10.00).
3. **Flake8** – PEP 8 blank-line formatting (12 → 0 findings).
