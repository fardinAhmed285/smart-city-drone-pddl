;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; PROBLEM MEDIUM: Autonomous Drone Planning for Smart-City Emergency Response
;; Specification:
;;   - 2 Drones: drone1, drone2
;;   - 8 Locations: 1 depot, 2 charging stations (ch1, ch2), 5 mission sites (site1-site5)
;;   - Battery capacity: b0-b6 (6 levels)
;;   - Flight costs vary between 1 and 2
;;   - Goals: Inspect 4 locations (site1, site2, site3, site4);
;;            Deliver 3 supplies of 2 types (med1, med2, water1)
;;   - Design constraint: site5 is initially locked until neighbor site4 is inspected
;;                        (unlocked-by-inspection site4 site5)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem emergency-medium)
  (:domain emergency-drone)

  (:objects
    drone1 drone2 - drone
    depot ch1 ch2 site1 site2 site3 site4 site5 - location
    med1 med2 - medkit
    water1 - water
    b0 b1 b2 b3 b4 b5 b6 - level
  )

  (:init
    ;; Action costs metric initialization
    (= (total-cost) 0)

    ;; Drone initial state
    (at drone1 depot)
    (empty drone1)
    (battery drone1 b6)

    (at drone2 ch2)
    (empty drone2)
    (battery drone2 b6)

    ;; Charging infrastructure
    (has-charging-station ch1)
    (has-charging-station ch2)

    ;; Accessibility: site5 is initially locked, all others open
    (accessible depot)
    (accessible ch1)
    (accessible ch2)
    (accessible site1)
    (accessible site2)
    (accessible site3)
    (accessible site4)
    ;; site5 is unlocked by inspecting neighbor site4
    (unlocked-by-inspection site4 site5)

    ;; Topology (Bidirectional connections)
    (connected depot ch1)
    (connected ch1 depot)

    (connected ch1 site1)
    (connected site1 ch1)

    (connected ch1 site2)
    (connected site2 ch1)

    (connected site1 site2)
    (connected site2 site1)

    (connected site2 ch2)
    (connected ch2 site2)

    (connected ch2 site3)
    (connected site3 ch2)

    (connected ch2 site4)
    (connected site4 ch2)

    (connected site4 site5)
    (connected site5 site4)

    (connected ch2 site5)
    (connected site5 ch2)

    ;; Action cost distances (values 1 and 2)
    (= (distance depot ch1) 1)
    (= (distance ch1 depot) 1)

    (= (distance ch1 site1) 1)
    (= (distance site1 ch1) 1)

    (= (distance ch1 site2) 2)
    (= (distance site2 ch1) 2)

    (= (distance site1 site2) 2)
    (= (distance site2 site1) 2)

    (= (distance site2 ch2) 1)
    (= (distance ch2 site2) 1)

    (= (distance ch2 site3) 1)
    (= (distance site3 ch2) 1)

    (= (distance ch2 site4) 2)
    (= (distance site4 ch2) 2)

    (= (distance site4 site5) 1)
    (= (distance site5 site4) 1)

    (= (distance ch2 site5) 2)
    (= (distance site5 ch2) 2)

    ;; Flight battery costs (b1 and b2)
    (flight-cost depot ch1 b1)
    (flight-cost ch1 depot b1)

    (flight-cost ch1 site1 b1)
    (flight-cost site1 ch1 b1)

    (flight-cost ch1 site2 b2)
    (flight-cost site2 ch1 b2)

    (flight-cost site1 site2 b2)
    (flight-cost site2 site1 b2)

    (flight-cost site2 ch2 b1)
    (flight-cost ch2 site2 b1)

    (flight-cost ch2 site3 b1)
    (flight-cost site3 ch2 b1)

    (flight-cost ch2 site4 b2)
    (flight-cost site4 ch2 b2)

    (flight-cost site4 site5 b1)
    (flight-cost site5 site4 b1)

    (flight-cost ch2 site5 b2)
    (flight-cost site5 ch2 b2)

    ;; Supplies and destination demands
    (supply-at med1 depot)
    (supply-at med2 depot)
    (supply-at water1 depot)

    (needs site1 med1)
    (needs site3 med2)
    (needs site5 water1)

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
  )

  (:goal (and
    (inspected site1)
    (inspected site2)
    (inspected site3)
    (inspected site4)
    (delivered med1 site1)
    (delivered med2 site3)
    (delivered water1 site5)
  ))

  (:metric minimize (total-cost))
)
