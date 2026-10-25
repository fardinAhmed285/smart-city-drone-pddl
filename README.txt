================================================================================
AUTONOMOUS DRONE PLANNING FOR SMART-CITY EMERGENCY RESPONSE
Planning and Approximate Reasoning (MIA-MESIIA)
PDDL Technical Deliverables & Reproduction Guide
================================================================================

1. PROJECT OVERVIEW
--------------------------------------------------------------------------------
This project implements an automated AI planning system for autonomous drone 
emergency response across smart-city disaster environments using PDDL (Planning 
Domain Definition Language).

Two alternative domain models are implemented:
  - domain-A.pddl: Model A — Full Recharge. A single recharge action at a 
    charging station restores a drone's battery directly to maximum capacity (max-level).
  - domain-B.pddl: Model B — Incremental Recharge. Each recharge action raises 
    the battery level by exactly one symbolic unit (next-level). Multiple recharge 
    steps are required to reach higher capacity.

Four problem instances are evaluated:
  - problem-small.pddl: 1 drone, 5 locations, battery b0-b4, unit flight costs.
    Recharging is unavoidable (tour requires 6 flights > capacity 4).
  - problem-medium.pddl: 2 drones, 8 locations, battery b0-b6, flight costs 1-2.
    Locked location (site5) requires prior inspection of neighboring site4.
  - problem-large.pddl: 3 drones, 11 locations, battery b0-b6, 3 supply types.
    Locked location (site_e4) requires prior emergency supply delivery at site_e2.
  - problem-large-1drone.pddl: Single-drone variant on the exact same map, edge 
    costs, initial supplies, and goals as problem-large.pddl.

All problem instances adhere to strict Fast Downward-compatible PDDL without 
numeric fluents, modeling discrete battery levels symbolically and optimizing 
total mission cost via :action-costs (:metric minimize (total-cost)).


2. REPOSITORY STRUCTURE
--------------------------------------------------------------------------------
  ├── domain-A.pddl              # Domain Model A (instant full recharge)
  ├── domain-B.pddl              # Domain Model B (incremental stepped recharge)
  ├── problem-small.pddl         # Small problem instance
  ├── problem-medium.pddl        # Medium problem instance
  ├── problem-large.pddl         # Large problem instance (3 drones)
  ├── problem-large-1drone.pddl  # Large problem instance (1 drone variant)
  ├── README.txt                 # Exact setup, execution, and validation instructions
  ├── TECHNICAL_NOTES.txt        # Comprehensive technical report data & analysis
  ├── plans/                     # Generated planner plans (*.plan)
  ├── validation/                # Actual VAL validation outputs (*.val)
  ├── results/                   # Raw planner execution logs and summary CSV/JSON
  │     ├── experiments_results.csv
  │     ├── experiments_results.json
  │     └── *.log
  └── scripts/                   # Automated execution, validation, and checking tools
        ├── run_experiments.py           # Automated suite for all 16+ runs
        ├── validate_all.py              # Batch VAL validation runner
        └── check_instance_constraints.py # Formal PDDL & constraint verifier


3. ENVIRONMENT & TOOL SETUP
--------------------------------------------------------------------------------
The tools require Fast Downward (22.06+) and VAL (Plan Validation Tool).

Option A: WSL2 (Ubuntu 22.04 / 24.04 LTS) [Recommended & Tested]
  1. Install build dependencies:
       sudo apt-get update
       sudo apt-get install -y cmake g++ make flex bison python3 git

  2. Install Fast Downward:
       git clone --depth 1 https://github.com/aibasel/downward.git /opt/downward
       python3 /opt/downward/build.py
       sudo ln -sf /opt/downward/fast-downward.py /usr/local/bin/fast-downward.py

  3. Install VAL (Validate):
       git clone --depth 1 https://github.com/KCL-Planning/VAL.git /opt/val
       cd /opt/val && cmake -B build && cmake --build build -j4
       sudo ln -sf /opt/val/build/bin/Validate /usr/local/bin/Validate

Option B: Docker (Official Fast Downward Container)
  Run in the workspace folder:
       docker run --rm -v "$PWD":/work aibasel/downward \
         --plan-file /work/sas_plan --alias lama-first \
         /work/domain-A.pddl /work/problem-small.pddl


4. REPRODUCING EXPERIMENTS
--------------------------------------------------------------------------------
To run the automated suite across all 16 benchmark configurations plus the 
multi-drone anytime comparison:
  wsl -d Ubuntu -e bash -c "cd /mnt/e/smart_city_pddl && python3 scripts/run_experiments.py"

To run individual configurations manually:

A. LAMA-first (Satisficing, fast greedy heuristic search):
  fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G \
    --plan-file sas_plan --alias lama-first domain-A.pddl problem-small.pddl

B. A* with LM-cut (Cost-optimal admissible search):
  fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G \
    --plan-file sas_plan domain-A.pddl problem-small.pddl --search "astar(lmcut())"

C. LAMA Anytime (Iteratively improving cost optimization):
  fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G \
    --plan-file sas_plan --alias lama domain-A.pddl problem-large.pddl


5. PLAN VALIDATION WITH VAL
--------------------------------------------------------------------------------
To validate any generated plan using the standard VAL validator:
  Validate -v <domain.pddl> <problem.pddl> <plan_file>

Example:
  Validate -v domain-A.pddl problem-small.pddl plans/small_domain-A_lama-first.plan

To batch re-validate all generated plans in plans/:
  wsl -d Ubuntu -e bash -c "cd /mnt/e/smart_city_pddl && python3 scripts/validate_all.py"


6. CONSISTENCY & CONSTRAINT CHECKS
--------------------------------------------------------------------------------
To run the automated formal design verification script (checks graph symmetry, 
cost consistency, battery object bounds, reachability, and instance constraints):
  wsl -d Ubuntu -e bash -c "cd /mnt/e/smart_city_pddl && python3 scripts/check_instance_constraints.py"

================================================================================
