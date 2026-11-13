# Smart City Drone Planning with PDDL

A classical AI planning project that models multi-drone delivery in a smart-city environment using the **Planning Domain Definition Language (PDDL)**. The project compares two battery-management strategies and evaluates how they affect the plans generated for scenarios of increasing complexity.

## Overview

Autonomous delivery drones must coordinate movement through a city while respecting battery constraints. A route can be geographically feasible but operationally invalid if a drone cannot complete the required actions with its available energy.

This project represents the problem symbolically so that an automated planner can generate action sequences that satisfy the delivery goals and battery constraints.

The central comparison is between:

- **Domain A — Full Recharge:** a drone must use the full-recharge strategy when replenishing its battery.
- **Domain B — Incremental Recharge:** a drone can replenish its battery in smaller increments, allowing the planner to reason about partial battery levels.

The two models are tested against small, medium, and large planning instances.

## What the project demonstrates

- Modelling a multi-drone delivery problem using PDDL.
- Representing locations, movement, battery state, and charging as planning predicates and actions.
- Encoding alternative resource-management strategies as separate planning domains.
- Designing problem instances with increasing numbers of drones, locations, and operational constraints.
- Comparing plans produced by different search configurations.
- Validating generated plans with the VAL plan validator.

## Planning model

PDDL separates a planning task into two parts:

| Component | Responsibility |
|---|---|
| Domain | Defines the available actions, their preconditions, and their effects. |
| Problem | Defines the objects, initial state, and goal conditions for one scenario. |

The planner combines a domain with a problem instance and searches for a sequence of valid actions that reaches the specified goal state.

### Battery-management strategies

**Domain A: Full Recharge**

The full-recharge model represents charging as a complete recharge operation. This provides a simpler battery-management model, but it constrains the charging decisions available to the planner.

**Domain B: Incremental Recharge**

The incremental-recharge model represents battery levels explicitly using discrete battery-state objects (`b0` to `b6`). This allows charging to be represented as smaller state transitions rather than one all-or-nothing operation.

The comparison examines how these different representations affect the planner's ability to construct valid delivery plans.

## Experimental scenarios

The project uses three instances to increase planning complexity progressively.

| Instance | Drones | Locations | Scenario characteristics |
|---|---:|---:|---|
| Small | 1 | 5 | Basic delivery and battery-management scenario. |
| Medium | 2 | 8 | Multiple drones and a charging-site constraint; site 5 follows site 4 in the scenario. |
| Large | 3 | 11 | Larger multi-drone scenario with a west–east bridge and three supply types. |

The instances are designed to test whether the two battery models remain workable as the number of agents and environmental constraints increases.

## Planning and validation

The project uses **Fast Downward** to solve the PDDL planning tasks and **VAL** to validate generated plans.

The planner configurations considered include:

- `lama-first`
- `astar(lmcut())`

Fast Downward searches for a plan that satisfies the goal conditions under the action model. VAL is then used to check whether the resulting plan is valid with respect to the PDDL domain and problem.

A planner finding a sequence of actions is not, by itself, sufficient evidence that the plan is valid. Plan validation provides a separate correctness check.

## Repository contents

The repository contains the PDDL domain and problem definitions for the two battery strategies and their planning instances.

- **Domain A:** full-recharge model.
- **Domain B:** incremental-recharge model.
- **Problem instances:** small, medium, and large scenarios.
- **Planner outputs:** generated plans used for evaluation, where included in the repository.

See the repository files for the exact domain, problem, and plan filenames.

## Tools and technologies

- **PDDL** — declarative modelling of actions, preconditions, effects, initial states, and goals.
- **Fast Downward** — automated classical planning.
- **VAL** — plan validation.

## Reproducing the experiments

You need a working installation of Fast Downward and VAL.

1. Clone this repository:

   ```bash
   git clone https://github.com/fardinAhmed285/smart-city-drone-pddl.git
   cd smart-city-drone-pddl
   ```

2. Identify the matching domain file and problem instance in the repository.

3. Run Fast Downward with the selected domain, problem, and search configuration. For example, the search configuration can be set to `lama-first` or `astar(lmcut())`.

4. Save the generated plan and validate it with VAL against the same domain and problem files.

The exact command-line paths depend on where Fast Downward and VAL are installed. Consult their documentation for installation and invocation details.

## Key AI concepts

This project applies several core concepts from classical AI planning:

- **State-space search:** exploring possible world states through action execution.
- **Action modelling:** defining preconditions and effects that determine when an action is applicable and how it changes the world.
- **Resource constraints:** representing battery capacity and charging decisions as part of the planning state.
- **Multi-agent planning:** coordinating the actions of multiple drones within a shared environment.
- **Plan validation:** independently checking whether a generated sequence of actions satisfies the formal model.

## Skills demonstrated

- PDDL domain and problem modelling
- Classical AI planning
- Automated search with Fast Downward
- Heuristic search configurations
- Resource-constrained planning
- Multi-agent scenario design
- Plan validation with VAL

## Author

**Fardin Ahmed**
