;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; DOMAIN B: Autonomous Drone Planning for Smart-City Emergency Response
;; Model B: Each recharge action increments battery by one symbolic level.
;;          Multiple recharge actions are required to reach higher capacity.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain emergency-drone)
  (:requirements :strips :typing :negative-preconditions :conditional-effects :action-costs)

  (:types
    drone location supply level - object
    medkit water comms - supply
  )

  (:predicates
    ;; Drone state
    (at ?d - drone ?l - location)
    (empty ?d - drone)
    (carrying ?d - drone ?s - supply)
    (battery ?d - drone ?l - level)

    ;; City topology & accessibility
    (connected ?from ?to - location)
    (accessible ?l - location)

    ;; Mission site status & unlocking dependencies
    (inspected ?l - location)
    (unlocked-by-inspection ?source ?target - location)
    (unlocked-by-delivery ?source ?target - location)

    ;; Supply management
    (supply-at ?s - supply ?l - location)
    (needs ?l - location ?s - supply)
    (delivered ?s - supply ?l - location)

    ;; Charging infrastructure
    (has-charging-station ?l - location)

    ;; Discrete battery levels and transitions
    (flight-cost ?from ?to - location ?c - level)
    (battery-after ?before ?c ?left - level)
    (next-level ?l1 ?l2 - level)
    (max-level ?l - level)
  )

  (:functions
    (total-cost) - number
    (distance ?from ?to - location) - number
  )

  ;; Action 1: Fly between connected and accessible locations
  ;; Decreases drone battery by flight cost; increases total-cost by edge distance.
  (:action fly
    :parameters (?d - drone ?from ?to - location ?before ?c ?left - level)
    :precondition (and
      (at ?d ?from)
      (connected ?from ?to)
      (accessible ?to)
      (battery ?d ?before)
      (flight-cost ?from ?to ?c)
      (battery-after ?before ?c ?left)
    )
    :effect (and
      (not (at ?d ?from))
      (at ?d ?to)
      (not (battery ?d ?before))
      (battery ?d ?left)
      (increase (total-cost) (distance ?from ?to))
    )
  )

  ;; Action 2: Inspect a location
  ;; Drone must be present; inspecting may unlock dependent locations.
  (:action inspect
    :parameters (?d - drone ?l - location)
    :precondition (and
      (at ?d ?l)
      (not (inspected ?l))
    )
    :effect (and
      (inspected ?l)
      (forall (?y - location)
        (when (unlocked-by-inspection ?l ?y)
          (accessible ?y)
        )
      )
      (increase (total-cost) 1)
    )
  )

  ;; Action 3: Pick up a supply package
  ;; Drone must be co-located with the supply and currently empty.
  (:action pick-up-supply
    :parameters (?d - drone ?s - supply ?l - location)
    :precondition (and
      (at ?d ?l)
      (supply-at ?s ?l)
      (empty ?d)
    )
    :effect (and
      (not (supply-at ?s ?l))
      (not (empty ?d))
      (carrying ?d ?s)
      (increase (total-cost) 1)
    )
  )

  ;; Action 4: Deliver a supply package to a location that needs it
  ;; Delivers the carried supply; fulfilling a delivery may unlock dependent locations.
  (:action deliver-supply
    :parameters (?d - drone ?s - supply ?l - location)
    :precondition (and
      (at ?d ?l)
      (carrying ?d ?s)
      (needs ?l ?s)
    )
    :effect (and
      (not (carrying ?d ?s))
      (empty ?d)
      (delivered ?s ?l)
      (supply-at ?s ?l)
      (not (needs ?l ?s))
      (forall (?y - location)
        (when (unlocked-by-delivery ?l ?y)
          (accessible ?y)
        )
      )
      (increase (total-cost) 1)
    )
  )

  ;; Action 5 (Model B): Incremental recharge
  ;; Each execution raises the drone's battery by exactly one symbolic level (next-level).
  (:action recharge
    :parameters (?d - drone ?l - location ?cur ?next - level)
    :precondition (and
      (at ?d ?l)
      (has-charging-station ?l)
      (battery ?d ?cur)
      (next-level ?cur ?next)
    )
    :effect (and
      (not (battery ?d ?cur))
      (battery ?d ?next)
      (increase (total-cost) 1)
    )
  )
)
