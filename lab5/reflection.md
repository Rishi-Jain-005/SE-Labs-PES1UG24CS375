# Lab 5 - Reflection

**Name:** Rishi Jain  **SRN:** PES1UG24CS375

## 1. Which issues were easiest and hardest to fix?
The easy ones were the formatting and naming problems: unused imports, the
`== True` check, the camelCase function name and the blank lines Flake8
complained about. Those were quick, mostly mechanical edits. The hardest
was `eval()`. I couldn't just delete it because the program lets the user
type their own merit formula, so I had to replace it with a safer
calculation that only accepts numbers, `gpa`, `credits` and basic
arithmetic. Deciding what counts as a valid GPA, credit count and income
for the validation also took some thought.

## 2. Did the tools give false positives or miss anything?
I didn't see any false positives. Every warning pointed at something real,
even if small, like the missing docstrings. What the tools missed were
logic bugs. When I first ran the program, student U003 (GPA 12.5, negative
credits and negative income) was shortlisted with a score of 119, and none
of the three tools said anything about it. I only noticed because the
output looked wrong. This showed me that static analysis finds bad patterns
but doesn't understand what the program is supposed to do, so running and
testing the code is still necessary.

## 3. How can static analysis fit into a real workflow?
I would run Flake8, Pylint and Bandit automatically before every commit
(pre-commit hook) and again in CI, for example GitHub Actions, so a pull
request fails if Bandit finds a Medium/High issue or Pylint drops below a
set score. It still needs tests and code review next to it.

## 4. What improved after using the tools?
- Security: removing `eval()` closed a code-injection hole.
- Reliability: no shared default list, files are closed properly, and
  errors are no longer hidden by `except: pass`.
- Readability: docstrings, PEP 8 names and formatting, and no more `global`
  statements.
- Numbers: Pylint 4.69 -> 10.00, Bandit 2 issues -> 0, Flake8 12 -> 0.