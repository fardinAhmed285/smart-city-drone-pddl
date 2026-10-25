#!/usr/bin/env python3
"""
Validation Script: Validates all generated plan files in plans/ using VAL (Validate).
Saves individual validation outputs in validation/ and prints a summary.
"""

import subprocess
import re
from pathlib import Path

WORKSPACE = Path("/mnt/e/smart_city_pddl") if Path("/mnt/e/smart_city_pddl").exists() else Path(__file__).resolve().parent.parent
PLANS_DIR = WORKSPACE / "plans"
VALIDATION_DIR = WORKSPACE / "validation"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== VALIDATING ALL PLANS WITH VAL (Validate) ===")
    plan_files = sorted(PLANS_DIR.glob("*.plan"))
    if not plan_files:
        print("No plan files found in plans/ to validate.")
        return

    success_count = 0
    total_count = len(plan_files)

    for plan_file in plan_files:
        # e.g., small_domain-A_lama-first.plan
        name = plan_file.stem
        parts = name.split("_")
        prob_name = parts[0]
        dom_name = parts[1]

        prob_file = WORKSPACE / f"problem-{prob_name}.pddl"
        dom_file = WORKSPACE / f"{dom_name}.pddl"
        val_output_file = VALIDATION_DIR / f"{name}.val"

        if not prob_file.exists() or not dom_file.exists():
            print(f"[SKIP] Missing domain ({dom_file}) or problem ({prob_file}) for {plan_file.name}")
            continue

        cmd = ["Validate", "-v", str(dom_file), str(prob_file), str(plan_file)]
        proc = subprocess.run(cmd, cwd=str(WORKSPACE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        val_text = proc.stdout
        val_output_file.write_text(val_text, encoding="utf-8")

        is_valid = "Plan valid" in val_text
        m_cost = re.search(r"Final value:\s*([\d\.]+)", val_text)
        cost_str = m_cost.group(1) if m_cost else "unknown"

        if is_valid:
            success_count += 1
            print(f"  [VALID] {plan_file.name} -> Cost: {cost_str}")
        else:
            print(f"  [INVALID] {plan_file.name}")

    print(f"\nValidation Summary: {success_count}/{total_count} plans successfully verified with VAL.")


if __name__ == "__main__":
    main()
