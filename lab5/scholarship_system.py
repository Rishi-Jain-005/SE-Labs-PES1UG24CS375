"""Student scholarship eligibility screener.

Computes a merit score from GPA and extracurricular credits, checks family
income against a limit, and saves the shortlist to a JSON file.
"""
import ast
import json
import operator
import sys

results = {}
DEFAULT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85
GPA_MAX = 10.0
RESULTS_FILE = "scholarships.json"

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node, variables):
    """Evaluate an AST node, allowing only numbers, known names and + - * /."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    if (isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        return _BINARY_OPS[type(node.op)](
            _eval_node(node.left, variables),
            _eval_node(node.right, variables),
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand, variables))
    raise ValueError("formula may only use gpa, credits, numbers and + - * /")


def calculate_merit_score(gpa, credit_points, formula=DEFAULT_FORMULA):
    """Return the merit score for the given formula without using eval()."""
    try:
        tree = ast.parse(formula, mode="eval")
        return _eval_node(tree, {"gpa": gpa, "credits": credit_points})
    except SyntaxError as err:
        raise ValueError(f"formula is not valid syntax: {err.msg}") from err
    except ZeroDivisionError as err:
        raise ValueError("formula divides by zero") from err


def _number(scores, key, default=None):
    """Fetch a numeric field from the scores dict or raise ValueError."""
    value = scores.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} is missing or not a number")
    return value


def validate_scores(test_scores):
    """Return (gpa, credit_points, income) after range checks."""
    gpa = _number(test_scores, "gpa")
    credit_points = _number(test_scores, "credits", 0)
    income = _number(test_scores, "income")
    if not 0 <= gpa <= GPA_MAX:
        raise ValueError(f"gpa must be between 0 and {GPA_MAX}")
    if credit_points < 0:
        raise ValueError("credits cannot be negative")
    if income < 0:
        raise ValueError("income cannot be negative")
    return gpa, credit_points, income


def evaluate_applicant(student_id, test_scores, logs=None,
                       formula=DEFAULT_FORMULA):
    """Score one applicant, store the outcome and return eligibility."""
    if logs is None:
        logs = []
    try:
        gpa, credit_points, income = validate_scores(test_scores)
        score = round(calculate_merit_score(gpa, credit_points, formula), 2)
    except ValueError as err:
        results[student_id] = {"score": None, "eligible": False,
                               "error": str(err)}
        logs.append(f"{student_id} rejected: {err}")
        return False
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    logs.append(f"{student_id} scored {score}")
    return eligible


def persist_results(file=RESULTS_FILE):
    """Write the results dictionary to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(results, handle)


def load_results(file=RESULTS_FILE):
    """Load results from a JSON file; keep current ones if it can't be read."""
    try:
        with open(file, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except FileNotFoundError:
        return
    except (OSError, json.JSONDecodeError) as err:
        print(f"Warning: could not load {file}: {err}", file=sys.stderr)
        return
    results.clear()
    results.update(loaded)


def print_shortlist():
    """Print every eligible applicant with their score."""
    print("Shortlisted applicants:")
    for student_id, record in results.items():
        if record["eligible"]:
            print(" ", student_id, "score =", record["score"])


def main():
    """Run the sample applicants and let the user change the formula."""
    logs = []
    evaluate_applicant("U001", {"gpa": 9.1, "credits": 4, "income": 450000},
                       logs)
    evaluate_applicant("U002", {"gpa": 7.2, "credits": 1, "income": 300000},
                       logs)
    evaluate_applicant("U003", {"gpa": 12.5, "credits": -3, "income": -1},
                       logs)
    evaluate_applicant("U004", {"gpa": 6.5}, logs)

    formula = DEFAULT_FORMULA
    user_formula = input("Merit formula (Enter to keep default): ").strip()
    if user_formula:
        try:
            calculate_merit_score(1.0, 1.0, user_formula)
            formula = user_formula
        except ValueError as err:
            print(f"Invalid formula ({err}); keeping the default.")

    evaluate_applicant("U005", {"gpa": 8.4, "credits": 3, "income": 600000},
                       logs, formula)
    persist_results()
    load_results()
    print_shortlist()
    print("Evaluation log:")
    for entry in logs:
        print(" ", entry)


if __name__ == "__main__":
    main()
