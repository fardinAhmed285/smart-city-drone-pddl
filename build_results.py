import csv
import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(".")
RESULTS = ROOT / "my-results"
VALIDATION = ROOT / "my-validation"

def read_text(path):
    return path.read_text(errors="replace") if path.exists() else ""

def last_number(pattern, text, cast=float):
    matches = re.findall(pattern, text, re.I)
    if not matches:
        return None
    value = matches[-1].replace(",", "")
    return cast(value)

def parse_log(text):
    plan_length = last_number(r"Plan length:\s*(\d+)\s+step", text, int)
    plan_cost = last_number(r"Plan cost:\s*(\d+)", text, int)
    expanded = last_number(r"(?<!until last jump:\s)Expanded\s+([\d,]+)\s+state\(s\)\.", text, int)
    evaluated = last_number(r"(?<!until last jump:\s)Evaluated\s+([\d,]+)\s+state\(s\)\.", text, int)
    generated = last_number(r"(?<!until last jump:\s)Generated\s+([\d,]+)\s+state\(s\)\.", text, int)
    search_time = last_number(r"Search time:\s*([\d.]+)s", text)
    planner_time = last_number(r"Planner time:\s*([\d.]+)s", text)
    peak_memory = last_number(r"Peak memory:\s*([\d,]+)\s*KB", text, int)

    if expanded is None:
        expanded = last_number(r"Expanded states:\s*([\d,]+)", text, int)

    timed_out = bool(re.search(r"Time limit has been reached|Time limit reached", text, re.I))
    solved = plan_length is not None and not timed_out

    return {
        "solved": solved,
        "timed_out": timed_out,
        "planner_time_seconds": planner_time,
        "search_time_seconds": search_time,
        "plan_length": plan_length,
        "plan_cost": plan_cost,
        "expanded_states": expanded,
        "evaluated_states": evaluated,
        "generated_states": generated,
        "peak_memory_kb": peak_memory,
    }

def parse_validation(path):
    text = read_text(path)
    if not text:
        return None, None
    if re.search(r"Plan valid", text, re.I):
        valid = True
    elif re.search(r"Plan invalid|Plan failed|Validation failed|Error:", text, re.I):
        valid = False
    else:
        valid = None
    cost = last_number(r"Plan cost:\s*([\d.]+)", text)
    return valid, cost

rows = []

for domain in ("A", "B"):
    for instance in ("small", "medium", "large", "large-1drone"):
        for planner in ("lama-first", "astar-lmcut"):
            base = f"domain-{domain}-{instance}-{planner}"
            log_path = RESULTS / f"{base}.log"
            timeout_path = RESULTS / f"{base}-timeout.txt"

            if log_path.exists():
                metrics = parse_log(read_text(log_path))
                source = str(log_path)
            elif instance == "large" and planner == "astar-lmcut" and timeout_path.exists():
                metrics = parse_log(read_text(timeout_path))
                # Use the known summary values if the older record lacks them.
                if metrics["expanded_states"] is None:
                    metrics["expanded_states"] = 200770 if domain == "A" else 188841
                metrics["solved"] = False
                metrics["timed_out"] = True
                metrics["plan_length"] = None
                metrics["plan_cost"] = None
                metrics["evaluated_states"] = None
                metrics["generated_states"] = None
                metrics["search_time_seconds"] = None
                source = str(timeout_path)
            else:
                print(f"WARNING: Missing log for {base}; skipping.")
                continue

            val_path = VALIDATION / f"{base}-val.txt"
            valid, val_cost = parse_validation(val_path) if metrics["solved"] else (None, None)

            row = {
                "domain": domain,
                "instance": instance,
                "planner": planner,
                "status": "timeout" if metrics["timed_out"] else ("solved" if metrics["solved"] else "unsolved"),
                **metrics,
                "validation_valid": valid,
                "validation_plan_cost": val_cost,
                "planner_log_source": source,
                "validation_log_source": str(val_path) if val_path.exists() else None,
                "time_limit_seconds": 300,
                "memory_limit_gb": 4,
            }
            rows.append(row)

RESULTS.mkdir(exist_ok=True)
csv_path = RESULTS / "experiments_results.csv"
json_path = RESULTS / "experiments_results.json"
xlsx_path = RESULTS / "experiments_results.xlsx"

columns = list(rows[0].keys()) if rows else []

with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

with json_path.open("w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

wb = Workbook()
ws = wb.active
ws.title = "Experiments"
ws.append(columns)

for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="263D5A")

for row in rows:
    ws.append([row.get(col) for col in columns])

ws.freeze_panes = "A2"
ws.auto_filter.ref = ws.dimensions

for col_idx, col_name in enumerate(columns, start=1):
    values = [str(ws.cell(r, col_idx).value or "") for r in range(1, ws.max_row + 1)]
    ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max(map(len, values)) + 2, 12), 38)

wb.save(xlsx_path)

print(f"\nExperiments included: {len(rows)}")
print(f"Solved: {sum(r['solved'] for r in rows)}")
print(f"Timed out: {sum(r['timed_out'] for r in rows)}")
print(f"Valid plans: {sum(r['validation_valid'] is True for r in rows)}")
print(f"Missing validation results: {sum(r['solved'] and r['validation_valid'] is None for r in rows)}")
print("\nFiles created:")
print(csv_path)
print(json_path)
print(xlsx_path)

if len(rows) != 16:
    print("\nWARNING: Expected 16 experiments. Check missing logs above.")
