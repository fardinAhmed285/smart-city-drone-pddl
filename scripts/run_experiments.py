#!/usr/bin/env python3
"""
Autonomous Drone Planning for Smart-City Emergency Response
Experiment Automation and Validation Script

Executes all required combinations of:
  - 4 Problem instances: small, medium, large, large-1drone
  - 2 Domain models: Model A (full recharge), Model B (incremental recharge)
  - 2 Planner configurations: LAMA-first, A* with LM-cut
Plus the multi-drone vs single-drone comparison using LAMA (anytime).

Collects runtime, expanded states, plan length, plan cost, and validates all plans with VAL.
Saves structured results to CSV and JSON, logs to results/, plans to plans/, and VAL outputs to validation/.
"""

import os
import sys
import time
import subprocess
import re
import csv
import json
import shutil
from pathlib import Path

WORKSPACE = Path("/mnt/e/smart_city_pddl") if Path("/mnt/e/smart_city_pddl").exists() else Path(__file__).resolve().parent.parent

PLANS_DIR = WORKSPACE / "plans"
VALIDATION_DIR = WORKSPACE / "validation"
RESULTS_DIR = WORKSPACE / "results"
SCRIPTS_DIR = WORKSPACE / "scripts"

for d in [PLANS_DIR, VALIDATION_DIR, RESULTS_DIR, SCRIPTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TIMEOUT_SECONDS = 300  # 5 minutes
MEMORY_LIMIT = "4096M"

DOMAINS = [
    ("domain-A", WORKSPACE / "domain-A.pddl"),
    ("domain-B", WORKSPACE / "domain-B.pddl"),
]

PROBLEMS = [
    ("small", WORKSPACE / "problem-small.pddl"),
    ("medium", WORKSPACE / "problem-medium.pddl"),
    ("large", WORKSPACE / "problem-large.pddl"),
    ("large-1drone", WORKSPACE / "problem-large-1drone.pddl"),
]

CONFIGURATIONS = [
    ("lama-first", ["--alias", "lama-first"]),
    ("astar-lmcut", ["--search", "astar(lmcut())"]),
]


def parse_fd_log(log_text):
    """Parse Fast Downward output for key metrics."""
    res = {
        "solved": False,
        "runtime_s": None,
        "search_time_s": None,
        "plan_length": None,
        "plan_cost": None,
        "expanded_states": None,
        "evaluated_states": None,
        "generated_states": None,
        "peak_memory_kb": None,
        "failure_reason": None,
    }

    if "Solution found" in log_text:
        res["solved"] = True

    # Runtime
    m_time = re.search(r"Planner time:\s*([\d\.]+)s", log_text)
    if m_time:
        res["runtime_s"] = float(m_time.group(1))
    else:
        m_tot = re.search(r"Total time:\s*([\d\.]+)s", log_text)
        if m_tot:
            res["runtime_s"] = float(m_tot.group(1))

    # Search time
    m_search = re.search(r"Search time:\s*([\d\.]+)s", log_text)
    if m_search:
        res["search_time_s"] = float(m_search.group(1))

    # Plan length
    m_len = re.search(r"Plan length:\s*(\d+)\s*step", log_text)
    if m_len:
        res["plan_length"] = int(m_len.group(1))

    # Plan cost
    m_cost = re.search(r"Plan cost:\s*(\d+)", log_text)
    if m_cost:
        res["plan_cost"] = int(m_cost.group(1))

    # Expanded states
    m_exp = re.search(r"Expanded\s+(\d+)\s+state", log_text)
    if m_exp:
        res["expanded_states"] = int(m_exp.group(1))

    # Evaluated states
    m_eval = re.search(r"Evaluated\s+(\d+)\s+state", log_text)
    if m_eval:
        res["evaluated_states"] = int(m_eval.group(1))

    # Generated states
    m_gen = re.search(r"Generated\s+(\d+)\s+state", log_text)
    if m_gen:
        res["generated_states"] = int(m_gen.group(1))

    # Peak memory
    m_mem = re.search(r"Peak memory:\s*(\d+)\s*KB", log_text)
    if m_mem:
        res["peak_memory_kb"] = int(m_mem.group(1))

    if not res["solved"]:
        if "Time limit exceeded" in log_text or "out of time" in log_text.lower():
            res["failure_reason"] = "Timeout (> 300s)"
        elif "Memory limit exceeded" in log_text or "out of memory" in log_text.lower() or "bad_alloc" in log_text:
            res["failure_reason"] = "Out of Memory (> 4GB)"
        else:
            res["failure_reason"] = "Unsolved / Search Exhausted without Solution"

    return res


def parse_val_log(val_text):
    """Parse VAL validator output."""
    res = {
        "val_valid": False,
        "val_cost": None,
    }
    if "Plan valid" in val_text:
        res["val_valid"] = True
    m_cost = re.search(r"Final value:\s*([\d\.]+)", val_text)
    if m_cost:
        res["val_cost"] = float(m_cost.group(1))
    return res


def run_experiment(domain_name, domain_path, problem_name, problem_path, config_name, config_args, timeout=TIMEOUT_SECONDS, skip_existing=False):
    run_id = f"{problem_name}_{domain_name}_{config_name}"
    print(f"\n==================================================")
    print(f"Running Experiment: {run_id}")
    print(f"Domain: {domain_name} | Problem: {problem_name} | Planner: {config_name}")
    print(f"==================================================")

    plan_file = WORKSPACE / f"sas_plan_{run_id}"
    log_file = RESULTS_DIR / f"{run_id}.log"
    val_file = VALIDATION_DIR / f"{run_id}.val"
    saved_plan_file = PLANS_DIR / f"{run_id}.plan"

    if skip_existing and log_file.exists():
        print(f"Log exists and skip_existing is True. Reading from: {log_file.name}")
        log_text = log_file.read_text(encoding="utf-8")
        metrics = parse_fd_log(log_text)
        val_metrics = {"val_valid": False, "val_cost": None}
        if val_file.exists():
            val_text = val_file.read_text(encoding="utf-8")
            val_metrics = parse_val_log(val_text)
        elif saved_plan_file.exists():
            val_cmd = ["Validate", "-v", str(domain_path), str(problem_path), str(saved_plan_file)]
            val_proc = subprocess.run(val_cmd, cwd=str(WORKSPACE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            val_text = val_proc.stdout
            val_file.write_text(val_text, encoding="utf-8")
            val_metrics = parse_val_log(val_text)

        return {
            "run_id": run_id,
            "problem": problem_name,
            "domain": domain_name,
            "planner": config_name,
            "solved": "Yes" if metrics["solved"] else "No",
            "runtime_s": metrics["runtime_s"],
            "search_time_s": metrics["search_time_s"],
            "plan_length": metrics["plan_length"],
            "plan_cost": metrics["plan_cost"],
            "val_valid": "Yes" if val_metrics["val_valid"] else ("No" if metrics["solved"] else "N/A"),
            "val_cost": val_metrics["val_cost"],
            "expanded_states": metrics["expanded_states"],
            "evaluated_states": metrics["evaluated_states"],
            "generated_states": metrics["generated_states"],
            "peak_memory_kb": metrics["peak_memory_kb"],
            "notes": metrics["failure_reason"] if not metrics["solved"] else "Plan validated by VAL",
        }

    # Remove stale plan files
    for p in WORKSPACE.glob(f"sas_plan_{run_id}*"):
        p.unlink()

    cmd = [
        "fast-downward.py",
        "--overall-time-limit", f"{timeout}s",
        "--overall-memory-limit", MEMORY_LIMIT,
        "--plan-file", str(plan_file),
    ]

    if "lama" in config_name:
        cmd += config_args + [str(domain_path), str(problem_path)]
    else:
        # A* lmcut
        cmd += [str(domain_path), str(problem_path)] + config_args

    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(WORKSPACE),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout + 15
        )
        elapsed = time.time() - start_time
        log_text = proc.stdout
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - start_time
        log_text = (e.stdout or "") + f"\n[Runner] Subprocess killed due to overall timeout exceeding {timeout}s\n"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_text)

    metrics = parse_fd_log(log_text)
    if metrics["runtime_s"] is None:
        metrics["runtime_s"] = round(elapsed, 2)

    val_metrics = {"val_valid": False, "val_cost": None}

    # Locate generated plan: might be sas_plan_run_id or sas_plan_run_id.1, etc.
    actual_plan = None
    if plan_file.exists():
        actual_plan = plan_file
    else:
        numbered = sorted(WORKSPACE.glob(f"sas_plan_{run_id}.*"), key=lambda x: int(x.suffix[1:]) if x.suffix[1:].isdigit() else 0)
        if numbered:
            actual_plan = numbered[-1]  # best plan for anytime planners

    if actual_plan and actual_plan.exists():
        metrics["solved"] = True
        shutil.copy(actual_plan, saved_plan_file)
        print(f"Plan found! Saved to: {saved_plan_file.name}")

        # Run VAL
        val_cmd = ["Validate", "-v", str(domain_path), str(problem_path), str(saved_plan_file)]
        val_proc = subprocess.run(
            val_cmd,
            cwd=str(WORKSPACE),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        val_text = val_proc.stdout
        with open(val_file, "w", encoding="utf-8") as f:
            f.write(val_text)

        val_metrics = parse_val_log(val_text)
        print(f"VAL Validation: {'SUCCESS (Valid)' if val_metrics['val_valid'] else 'FAILED'}")
        print(f"VAL Plan Cost: {val_metrics['val_cost']}")
    else:
        print(f"No plan found. Reason: {metrics['failure_reason']}")

    record = {
        "run_id": run_id,
        "problem": problem_name,
        "domain": domain_name,
        "planner": config_name,
        "solved": "Yes" if metrics["solved"] else "No",
        "runtime_s": metrics["runtime_s"],
        "search_time_s": metrics["search_time_s"],
        "plan_length": metrics["plan_length"],
        "plan_cost": metrics["plan_cost"],
        "val_valid": "Yes" if val_metrics["val_valid"] else ("No" if metrics["solved"] else "N/A"),
        "val_cost": val_metrics["val_cost"],
        "expanded_states": metrics["expanded_states"],
        "evaluated_states": metrics["evaluated_states"],
        "generated_states": metrics["generated_states"],
        "peak_memory_kb": metrics["peak_memory_kb"],
        "notes": metrics["failure_reason"] if not metrics["solved"] else "Plan validated by VAL",
    }

    # Clean up intermediate sas files
    for p in WORKSPACE.glob(f"sas_plan_{run_id}*"):
        p.unlink()

    return record


def main():
    skip_existing = "--skip-existing" in sys.argv
    all_records = []

    # 1. Run all 16 required combinations (4 problems x 2 domains x 2 planners)
    print("\n>>> STARTING 16 CORE BENCHMARK EXPERIMENTS <<<")
    for prob_name, prob_path in PROBLEMS:
        for dom_name, dom_path in DOMAINS:
            for cfg_name, cfg_args in CONFIGURATIONS:
                record = run_experiment(dom_name, dom_path, prob_name, prob_path, cfg_name, cfg_args, skip_existing=skip_existing)
                all_records.append(record)

    # 2. Run anytime LAMA comparison on Large 3-drone vs Large 1-drone (under Model A and Model B)
    print("\n>>> STARTING ANYTIME LAMA COMPARISON EXPERIMENTS <<<")
    lama_experiments = [
        ("domain-A", WORKSPACE / "domain-A.pddl", "large", WORKSPACE / "problem-large.pddl"),
        ("domain-A", WORKSPACE / "domain-A.pddl", "large-1drone", WORKSPACE / "problem-large-1drone.pddl"),
        ("domain-B", WORKSPACE / "domain-B.pddl", "large", WORKSPACE / "problem-large.pddl"),
        ("domain-B", WORKSPACE / "domain-B.pddl", "large-1drone", WORKSPACE / "problem-large-1drone.pddl"),
    ]

    for dom_name, dom_path, prob_name, prob_path in lama_experiments:
        record = run_experiment(dom_name, dom_path, prob_name, prob_path, "lama-anytime", ["--alias", "lama"], timeout=90, skip_existing=False)
        all_records.append(record)

    # Save results to CSV and JSON
    csv_file = RESULTS_DIR / "experiments_results.csv"
    json_file = RESULTS_DIR / "experiments_results.json"

    fieldnames = [
        "run_id", "problem", "domain", "planner", "solved", "runtime_s", "search_time_s",
        "plan_length", "plan_cost", "val_valid", "val_cost", "expanded_states",
        "evaluated_states", "generated_states", "peak_memory_kb", "notes"
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    print(f"\n==================================================")
    print(f"All experiments completed! Results saved to:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")
    print(f"==================================================")


if __name__ == "__main__":
    main()
