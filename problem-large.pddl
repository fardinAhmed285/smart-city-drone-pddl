;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; PROBLEM LARGE: Autonomous Drone Planning for Smart-City Emergency Response
;; Specification:
;;   - 3 Drones: drone1 (West), drone2 (East charging), drone3 (East depot)
;;   - 11 Locations: 2 depots (depot_west, depot_east), 
;;                   2 charging stations (ch_west, ch_east),
;;                   7 mission sites (site_w1, site_w2, site_w3, site_e1, site_e2, site_e3, site_e4)
;;   - Battery capacity: b0-b6 (6 levels)
;;   - Flight costs: 1, 2, and 3 (cross-sector transit)
;;   - Supplies of 3 types: medkit (med1, med2), water (water1), comms (comm1)
;;   - Goals (7 total):
;;       * Inspections: site_w1, site_e1, site_e3
;;       * Deliveries: med1 -> site_w2, water1 -> site_w3, med2 -> site_e2, comm1 -> site_e4
;;   - Design constraint: site_e4 is locked until med2 is delivered to site_e2
;;                        (unlocked-by-delivery site_e2 site_e4)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem emergency-large)
  (:domain emergency-drone)

  (:objects
    drone1 drone2 drone3 - drone
    depot_west depot_east ch_west ch_east - location
    site_w1 site_w2 site_w3 - location
    site_e1 site_e2 site_e3 site_e4 - location
    med1 med2 - medkit
    water1 - water
    comm1 - comms
    b0 b1 b2 b3 b4 b5 b6 - level
  )

  (:init
    ;; Action costs metric initialization
    (= (total-cost) 0)

    ;; Drone initial state distributed across the city sectors
    (at drone1 depot_west)
    (empty drone1)
    (battery drone1 b6)

    (at drone2 ch_east)
    (empty drone2)
    (battery drone2 b6)

    (at drone3 depot_east)
    (empty drone3)
    (battery drone3 b6)

    ;; Charging infrastructure
    (has-charging-station ch_west)
    (has-charging-station ch_east)

    ;; Accessibility: site_e4 is locked initially until emergency relief is delivered to site_e2
    (accessible depot_west)
    (accessible depot_east)
    (accessible ch_west)
    (accessible ch_east)
    (accessible site_w1)
    (accessible site_w2)
    (accessible site_w3)
    (accessible site_e1)
    (accessible site_e2)
    (accessible site_e3)
    ;; Unlocking condition: delivery at site_e2 unlocks site_e4
    (unlocked-by-delivery site_e2 site_e4)

    ;; Topology - West Sector
    (connected depot_west ch_west)
    (connected ch_west depot_west)

    (connected ch_west site_w1)
    (connected site_w1 ch_west)

    (connected ch_west site_w2)
    (connected site_w2 ch_west)

    (connected site_w1 site_w2)
    (connected site_w2 site_w1)

    (connected site_w2 site_w3)
    (connected site_w3 site_w2)

    (connected ch_west site_w3)
    (connected site_w3 ch_west)

    ;; Topology - Inter-Sector Long Corridor (Distance 3)
    (connected ch_west ch_east)
    (connected ch_east ch_west)

    ;; Topology - East Sector
    (connected depot_east ch_east)
    (connected ch_east depot_east)

    (connected ch_east site_e1)
    (connected site_e1 ch_east)

    (connected ch_east site_e2)
    (connected site_e2 ch_east)

    (connected site_e1 site_e2)
    (connected site_e2 site_e1)

    (connected site_e2 site_e3)
    (connected site_e3 site_e2)

    (connected ch_east site_e3)
    (connected site_e3 ch_east)

    (connected site_e2 site_e4)
    (connected site_e4 site_e2)

    (connected ch_east site_e4)
    (connected site_e4 ch_east)

    ;; Action cost distances
    ;; West Sector
    (= (distance depot_west ch_west) 1)
    (= (distance ch_west depot_west) 1)

    (= (distance ch_west site_w1) 1)
    (= (distance site_w1 ch_west) 1)

    (= (distance ch_west site_w2) 1)
    (= (distance site_w2 ch_west) 1)

    (= (distance site_w1 site_w2) 1)
    (= (distance site_w2 site_w1) 1)

    (= (distance site_w2 site_w3) 1)
    (= (distance site_w3 site_w2) 1)

    (= (distance ch_west site_w3) 2)
    (= (distance site_w3 ch_west) 2)

    ;; Inter-sector bridge
    (= (distance ch_west ch_east) 3)
    (= (distance ch_east ch_west) 3)

    ;; East Sector
    (= (distance depot_east ch_east) 1)
    (= (distance ch_east depot_east) 1)

    (= (distance ch_east site_e1) 1)
    (= (distance site_e1 ch_east) 1)

    (= (distance ch_east site_e2) 1)
    (= (distance site_e2 ch_east) 1)

    (= (distance site_e1 site_e2) 1)
    (= (distance site_e2 site_e1) 1)

    (= (distance site_e2 site_e3) 1)
    (= (distance site_e3 site_e2) 1)

    (= (distance ch_east site_e3) 2)
    (= (distance site_e3 ch_east) 2)

    (= (distance site_e2 site_e4) 1)
    (= (distance site_e4 site_e2) 1)

    (= (distance ch_east site_e4) 2)
    (= (distance site_e4 ch_east) 2)

    ;; Flight battery costs
    ;; West Sector
    (flight-cost depot_west ch_west b1)
    (flight-cost ch_west depot_west b1)

    (flight-cost ch_west site_w1 b1)
    (flight-cost site_w1 ch_west b1)

    (flight-cost ch_west site_w2 b1)
    (flight-cost site_w2 ch_west b1)

    (flight-cost site_w1 site_w2 b1)
    (flight-cost site_w2 site_w1 b1)

    (flight-cost site_w2 site_w3 b1)
    (flight-cost site_w3 site_w2 b1)

    (flight-cost ch_west site_w3 b2)
    (flight-cost site_w3 ch_west b2)

    ;; Inter-sector bridge
    (flight-cost ch_west ch_east b3)
    (flight-cost ch_east ch_west b3)

    ;; East Sector
    (flight-cost depot_east ch_east b1)
    (flight-cost ch_east depot_east b1)

    (flight-cost ch_east site_e1 b1)
    (flight-cost site_e1 ch_east b1)

    (flight-cost ch_east site_e2 b1)
    (flight-cost site_e2 ch_east b1)

    (flight-cost site_e1 site_e2 b1)
    (flight-cost site_e2 site_e1 b1)

    (flight-cost site_e2 site_e3 b1)
    (flight-cost site_e3 site_e2 b1)

    (flight-cost ch_east site_e3 b2)
    (flight-cost site_e3 ch_east b2)

    (flight-cost site_e2 site_e4 b1)
    (flight-cost site_e4 site_e2 b1)

    (flight-cost ch_east site_e4 b2)
    (flight-cost site_e4 ch_east b2)

    ;; Supplies and destination demands
    (supply-at med1 depot_west)
    (supply-at water1 depot_west)
    (supply-at med2 depot_east)
    (supply-at comm1 depot_east)

    (needs site_w2 med1)
    (needs site_w3 water1)
    (needs site_e2 med2)
    (needs site_e4 comm1)

    ;; Discrete battery levels and transitions
    (max-level b6)
    (next-level b0 b1)
    (next-level b1 b2)
    (next-level b2 b3)
    (next-level b3 b4)
    (next-level b4 b5)
    (next-level b5 b6)

    ;; Battery transitions for cost b1
    (battery-after b6 b1 b5)
    (battery-after b5 b1 b4)
    (battery-after b4 b1 b3)
    (battery-after b3 b1 b2)
    (battery-after b2 b1 b1)
    (battery-after b1 b1 b0)

    ;; Battery transitions for cost b2
    (battery-after b6 b2 b4)
    (battery-after b5 b2 b3)
    (battery-after b4 b2 b2)
    (battery-after b3 b2 b1)
    (battery-after b2 b2 b0)

    ;; Battery transitions for cost b3
    (battery-after b6 b3 b3)
    (battery-after b5 b3 b2)
    (battery-after b4 b3 b1)
    (battery-after b3 b3 b0)
  )

  (:goal (and
    (inspected site_w1)
    (inspected site_e1)
    (inspected site_e3)
    (delivered med1 site_w2)
    (delivered water1 site_w3)
    (delivered med2 site_e2)
    (delivered comm1 site_e4)
  ))

  (:metric minimize (total-cost))
)
