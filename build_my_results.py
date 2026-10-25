
import csv
import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "my-results"
PLANS_DIR = ROOT / "my-plans"
VALIDATION_DIR = ROOT / "my-validation"

DOMAINS = ["domain-A", "domain-B"]
INSTANCES = ["small", "medium", "large", "large-1drone"]
PLANNERS = ["lama-first", "astar-lmcut"]

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path):
    """Read a text file safely. Return an empty string if it is missing."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def get_num(pattern, text, flags=re.IGNORECASE):
    """Extract the first number matching a regular expression."""
    match = re.search(pattern, text, flags)
    if not match:
        return None

    value = match.group(1).replace(",", "")

    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (ValueError, AttributeError):
        return None


def get_last_num(pattern, text, flags=re.IGNORECASE):
    """Extract the last number matching a regular expression."""
    matches = re.findall(pattern, text, flags)
    if not matches:
        return None

    value = matches[-1].replace(",", "")

    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (ValueError, AttributeError):
        return None


def parse_plan_length(plan_text):
    """Count actions in a Fast Downward plan file."""
    if not plan_text.strip():
        return None

    actions = 0

    for line in plan_text.splitlines():
        line = line.strip()

        if not line or line.startswith(";"):
            continue

        if line.startswith("(") and line.endswith(")"):
            actions += 1

    return actions if actions > 0 else None


def parse_plan_cost(log_text, plan_text):
    """Extract the planner-reported plan cost."""
    cost = get_last_num(
        r"Plan cost:\s*([\d,]+(?:\.\d+)?)",
        log_text,
    )

    if cost is not None:
        return cost

    cost = get_last_num(
        r";\s*cost\s*=\s*([\d,]+(?:\.\d+)?)",
        plan_text,
    )

    if cost is not None:
        return cost

    return None


def parse_validation_cost(validation_text):
    """
    Extract the cost reported by VAL.

    Prefer 'Final value:' because it reports the final value after
    executing the plan. Fall back to the successful-plan 'Value:' line.
    """
    cost = get_last_num(
        r"Final value:\s*([\d,]+(?:\.\d+)?)",
        validation_text,
    )

    if cost is not None:
        return cost

    successful_section = re.search(
        r"Successful plans:\s*(.*)",
        validation_text,
        re.IGNORECASE | re.DOTALL,
    )

    if successful_section:
        cost = get_last_num(
            r"^\s*Value:\s*([\d,]+(?:\.\d+)?)",
            successful_section.group(1),
            re.IGNORECASE | re.MULTILINE,
        )

    return cost


def parse_search_counts(log_text):
    """
    Extract the latest evaluated and expanded counts from Fast Downward
    progress lines. For timed-out searches, these are the last reported
    counts, not completed-search totals.
    """
    matches = re.findall(
        r"([\d,]+)\s+evaluated,\s*"
        r"([\d,]+)\s+expanded",
        log_text,
        re.IGNORECASE,
    )

    if not matches:
        return None, None

    evaluated, expanded = matches[-1]

    return (
        int(evaluated.replace(",", "")),
        int(expanded.replace(",", "")),
    )


def build_record(domain, instance, planner):
    base = f"{domain}-{instance}-{planner}"

    log_path = RESULTS_DIR / f"{base}.log"
    plan_path = PLANS_DIR / f"{base}.plan"
    validation_path = VALIDATION_DIR / f"{base}-val.txt"

    log_text = read_text(log_path)
    plan_text = read_text(plan_path)
    validation_text = read_text(validation_path)

    timeout = (
        "Time limit has been reached" in log_text
        or "out of time" in log_text.lower()
        or "timeout" in log_text.lower()
    )

    evaluated, expanded = parse_search_counts(log_text)

    planner_time = get_last_num(
        r"INFO\s+Planner time:\s*([\d.]+)\s*s?",
        log_text,
    )

    if planner_time is None:
        planner_time = get_last_num(
            r"Planner time:\s*([\d.]+)\s*s?",
            log_text,
        )

    search_time = get_last_num(
        r"Search time:\s*([\d.]+)\s*s?",
        log_text,
    )

    peak_memory = get_last_num(
        r"Peak memory:\s*([\d,]+)\s*KB",
        log_text,
    )

    plan_length = parse_plan_length(plan_text)
    plan_cost = parse_plan_cost(log_text, plan_text)

    validation_valid = None
    validation_cost = None

    if validation_text:
        if re.search(r"\bPlan valid\b", validation_text, re.IGNORECASE):
            validation_valid = True
            validation_cost = parse_validation_cost(validation_text)

        elif re.search(
            r"\bPlan failed\b|\bPlan invalid\b|\bPlan is invalid\b",
            validation_text,
            re.IGNORECASE,
        ):
            validation_valid = False

    if timeout:
        status = "timeout"
        plan_length = None
        plan_cost = None
        validation_valid = None
        validation_cost = None

    elif plan_path.exists() and plan_text.strip():
        status = "solved"

    elif log_text and re.search(
        r"Search stopped without finding a solution|"
        r"No solution|"
        r"Search failed",
        log_text,
        re.IGNORECASE,
    ):
        status = "unsolved"

    elif not log_text:
        status = "missing_log"

    else:
        status = "unknown"

    return {
        "domain": domain,
        "instance": instance,
        "planner": planner,
        "status": status,
        "runtime_seconds": planner_time,
        "search_time_seconds": search_time,
        "plan_length": plan_length,
        "plan_cost": plan_cost,
        "expanded_states": expanded,
        "evaluated_states": evaluated,
        "peak_memory_kb": peak_memory,
        "validation_valid": validation_valid,
        "validation_cost": validation_cost,
        "log_file": str(log_path.relative_to(ROOT))
        if log_path.exists() else None,
        "plan_file": str(plan_path.relative_to(ROOT))
        if plan_path.exists() else None,
        "validation_file": str(validation_path.relative_to(ROOT))
        if validation_path.exists() else None,
    }


def write_csv(records, output_path):
    if not records:
        return

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(records[0].keys()),
        )
        writer.writeheader()
        writer.writerows(records)


def write_json(records, output_path):
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def write_excel(records, output_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Experiments"

    if not records:
        workbook.save(output_path)
        return

    headers = list(records[0].keys())
    sheet.append(headers)

    for record in records:
        sheet.append([record.get(header) for header in headers])

    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="244062",
        )

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    for column_cells in sheet.columns:
        max_length = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        column_letter = get_column_letter(column_cells[0].column)
        sheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            35,
        )

    workbook.save(output_path)


def main():
    records = []

    for domain in DOMAINS:
        for instance in INSTANCES:
            for planner in PLANNERS:
                records.append(
                    build_record(domain, instance, planner)
                )

    csv_path = RESULTS_DIR / "my_experiments.csv"
    json_path = RESULTS_DIR / "my_experiments.json"
    excel_path = RESULTS_DIR / "my_experiments.xlsx"

    write_csv(records, csv_path)
    write_json(records, json_path)
    write_excel(records, excel_path)

    solved = sum(r["status"] == "solved" for r in records)
    timeouts = sum(r["status"] == "timeout" for r in records)
    valid = sum(r["validation_valid"] is True for r in records)
    invalid = sum(r["validation_valid"] is False for r in records)
    missing_validation_cost = sum(
        r["status"] == "solved"
        and r["validation_valid"] is True
        and r["validation_cost"] is None
        for r in records
    )

    print(f"Total experiments: {len(records)}")
    print(f"Solved: {solved}")
    print(f"Timeouts: {timeouts}")
    print(f"Validations passed: {valid}")
    print(f"Validations failed: {invalid}")
    print(f"Valid plans missing validation cost: {missing_validation_cost}")
    print()
    print("Files created in my-results/:")
    print(f"  {csv_path.name}")
    print(f"  {json_path.name}")
    print(f"  {excel_path.name}")


if __name__ == "__main__":
    main()
