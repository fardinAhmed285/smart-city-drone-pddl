;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; PROBLEM SMALL: Autonomous Drone Planning for Smart-City Emergency Response
;; Specification:
;;   - 1 Drone: drone1
;;   - 5 Locations: 1 depot, 1 charging station, 3 mission sites
;;   - Battery capacity: b0-b4 (4 levels)
;;   - All edge costs: 1 level / distance 1
;;   - Goals: Inspect site1, site2; deliver med1 to site3
;;   - Design constraint: Must recharge at least once (shortest goal tour requires 6 flights > battery capacity 4)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem emergency-small)
  (:domain emergency-drone)

  (:objects
    drone1 - drone
    depot charging site1 site2 site3 - location
    med1 - medkit
    b0 b1 b2 b3 b4 - level
  )

  (:init
    ;; Action costs metric initialization
    (= (total-cost) 0)

    ;; Drone initial state
    (at drone1 depot)
    (empty drone1)
    (battery drone1 b4)

    ;; Charging stations
    (has-charging-station charging)

    ;; Accessibility (all locations accessible from the start)
    (accessible depot)
    (accessible charging)
    (accessible site1)
    (accessible site2)
    (accessible site3)

    ;; Topology (Bidirectional hub-and-spoke centered at charging station)
    (connected depot charging)
    (connected charging depot)
    (connected charging site1)
    (connected site1 charging)
    (connected charging site2)
    (connected site2 charging)
    (connected charging site3)
    (connected site3 charging)

    ;; Distances (Unit cost = 1)
    (= (distance depot charging) 1)
    (= (distance charging depot) 1)
    (= (distance charging site1) 1)
    (= (distance site1 charging) 1)
    (= (distance charging site2) 1)
    (= (distance site2 charging) 1)
    (= (distance charging site3) 1)
    (= (distance site3 charging) 1)

    ;; Symbolic flight costs (Edge cost = b1)
    (flight-cost depot charging b1)
    (flight-cost charging depot b1)
    (flight-cost charging site1 b1)
    (flight-cost site1 charging b1)
    (flight-cost charging site2 b1)
    (flight-cost site2 charging b1)
    (flight-cost charging site3 b1)
    (flight-cost site3 charging b1)

    ;; Supplies and mission requirements
    (supply-at med1 depot)
    (needs site3 med1)

    ;; Discrete battery levels and transitions
    (max-level b4)
    (next-level b0 b1)
    (next-level b1 b2)
    (next-level b2 b3)
    (next-level b3 b4)

    ;; Battery consumption transitions for flight-cost b1
    (battery-after b4 b1 b3)
    (battery-after b3 b1 b2)
    (battery-after b2 b1 b1)
    (battery-after b1 b1 b0)
  )

  (:goal (and
    (inspected site1)
    (inspected site2)
    (delivered med1 site3)
  ))

  (:metric minimize (total-cost))
)
