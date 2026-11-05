1. PROJECT OVERVIEW

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




2. REPOSITORY STRUCTURE
--------------------------------------------------------------------------------
  ├── domain-A.pddl              # Domain Model A (instant full recharge)
  ├── domain-B.pddl              # Domain Model B (incremental stepped recharge)
  ├── problem-small.pddl         # Small problem instance
  ├── problem-medium.pddl        # Medium problem instance
  ├── problem-large.pddl         # Large problem instance (3 drones)
  ├── problem-large-1drone.pddl  # Large problem instance (1 drone variant)
  ├── README.txt                 # Exact setup, execution, and validation instructions
  ├── my-plans/                     # Generated planner plans (*.plan)
  ├── my-validation/                # VAL validation outputs (*.txt)
  ├── my-results/                   # Raw planner execution logs and summary CSV/JSON
  │     ├── experiments_results.csv
  │     ├── experiments_results.json
  │     └── *.log
  

3. ENVIRONMENT & TOOL SETUP

The tools require Fast Downward and VAL (Plan Validation Tool).

WSL2 
  a. Install build dependencies:
       sudo apt-get update
       sudo apt-get install -y cmake g++ make flex bison python3 git

  b. Install Fast Downward:
       git clone --depth 1 https://github.com/aibasel/downward.git /opt/downward
       python3 /opt/downward/build.py
       sudo ln -sf /opt/downward/fast-downward.py /usr/local/bin/fast-downward.py

  c. Install VAL (Validate):
       git clone --depth 1 https://github.com/KCL-Planning/VAL.git /opt/val
       cd /opt/val && cmake -B build && cmake --build build -j4
       sudo ln -sf /opt/val/build/bin/Validate /usr/local/bin/Validate



4. REPRODUCING EXPERIMENTS

Open the Ubuntu terminal from PowerShell:

wsl -d Ubuntu

Run all the following commands from the project directory.

A. LAMA-first

Domain A
fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-small-lama-first.plan --alias lama-first domain-A.pddl problem-small.pddl 2>&1 | tee my-results/domain-A-small-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-medium-lama-first.plan --alias lama-first domain-A.pddl problem-medium.pddl 2>&1 | tee my-results/domain-A-medium-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-large-lama-first.plan --alias lama-first domain-A.pddl problem-large.pddl 2>&1 | tee my-results/domain-A-large-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-large-1drone-lama-first.plan --alias lama-first domain-A.pddl problem-large-1drone.pddl 2>&1 | tee my-results/domain-A-large-1drone-lama-first.log

Domain B

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-small-lama-first.plan --alias lama-first domain-B.pddl problem-small.pddl 2>&1 | tee my-results/domain-B-small-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-medium-lama-first.plan --alias lama-first domain-B.pddl problem-medium.pddl 2>&1 | tee my-results/domain-B-medium-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-large-lama-first.plan --alias lama-first domain-B.pddl problem-large.pddl 2>&1 | tee my-results/domain-B-large-lama-first.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-large-1drone-lama-first.plan --alias lama-first domain-B.pddl problem-large-1drone.pddl 2>&1 | tee my-results/domain-B-large-1drone-lama-first.log


B. A* with LM-cut
Domain A

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-small-astar-lmcut.plan domain-A.pddl problem-small.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-A-small-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-medium-astar-lmcut.plan domain-A.pddl problem-medium.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-A-medium-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-large-astar-lmcut.plan domain-A.pddl problem-large.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-A-large-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-A-large-1drone-astar-lmcut.plan domain-A.pddl problem-large-1drone.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-A-large-1drone-astar-lmcut.log

Domain B

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-small-astar-lmcut.plan domain-B.pddl problem-small.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-B-small-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-medium-astar-lmcut.plan domain-B.pddl problem-medium.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-B-medium-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-large-astar-lmcut.plan domain-B.pddl problem-large.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-B-large-astar-lmcut.log

fast-downward.py --overall-time-limit 5m --overall-memory-limit 4G --plan-file my-plans/domain-B-large-1drone-astar-lmcut.plan domain-B.pddl problem-large-1drone.pddl --search "astar(lmcut())" 2>&1 | tee my-results/domain-B-large-1drone-astar-lmcut.log

5. PLAN VALIDATION WITH VAL

Domain A

Validate -v domain-A.pddl problem-small.pddl my-plans/domain-A-small-lama-first.plan 2>&1 | tee my-validation/domain-A-small-lama-first-val.txt

Validate -v domain-A.pddl problem-medium.pddl my-plans/domain-A-medium-lama-first.plan 2>&1 | tee my-validation/domain-A-medium-lama-first-val.txt

Validate -v domain-A.pddl problem-large.pddl my-plans/domain-A-large-lama-first.plan 2>&1 | tee my-validation/domain-A-large-lama-first-val.txt

Validate -v domain-A.pddl problem-large-1drone.pddl my-plans/domain-A-large-1drone-lama-first.plan 2>&1 | tee my-validation/domain-A-large-1drone-lama-first-val.txt

Validate -v domain-A.pddl problem-small.pddl my-plans/domain-A-small-astar-lmcut.plan 2>&1 | tee my-validation/domain-A-small-astar-lmcut-val.txt

Validate -v domain-A.pddl problem-medium.pddl my-plans/domain-A-medium-astar-lmcut.plan 2>&1 | tee my-validation/domain-A-medium-astar-lmcut-val.txt

Validate -v domain-A.pddl problem-large-1drone.pddl my-plans/domain-A-large-1drone-astar-lmcut.plan 2>&1 | tee my-validation/domain-A-large-1drone-astar-lmcut-val.txt


Domain B

Validate -v domain-B.pddl problem-small.pddl my-plans/domain-B-small-lama-first.plan 2>&1 | tee my-validation/domain-B-small-lama-first-val.txt

Validate -v domain-B.pddl problem-medium.pddl my-plans/domain-B-medium-lama-first.plan 2>&1 | tee my-validation/domain-B-medium-lama-first-val.txt

Validate -v domain-B.pddl problem-large.pddl my-plans/domain-B-large-lama-first.plan 2>&1 | tee my-validation/domain-B-large-lama-first-val.txt

Validate -v domain-B.pddl problem-large-1drone.pddl my-plans/domain-B-large-1drone-lama-first.plan 2>&1 | tee my-validation/domain-B-large-1drone-lama-first-val.txt

Validate -v domain-B.pddl problem-small.pddl my-plans/domain-B-small-astar-lmcut.plan 2>&1 | tee my-validation/domain-B-small-astar-lmcut-val.txt

Validate -v domain-B.pddl problem-medium.pddl my-plans/domain-B-medium-astar-lmcut.plan 2>&1 | tee my-validation/domain-B-medium-astar-lmcut-val.txt

Validate -v domain-B.pddl problem-medium.pddl my-plans/domain-B-medium-astar-lmcut.plan 2>&1 | tee my-validation/domain-B-medium-astar-lmcut-val.txt

Note: The two Large instances with three drones using A* (LM-cut) timed out. Therefore, their plans could not be validated with VAL. All other generated plans listed above were submitted for validation.
