

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 )
(:init
(arm-empty)
(on b1 b4)
(on-table b2)
(on-table b3)
(on-table b4)
(on-table b5)
(on-table b6)
(clear b1)
(clear b2)
(clear b3)
(clear b5)
(clear b6)
)
(:goal
(and
(on b1 b6)
(on b2 b4)
(on b4 b5)
(on b5 b1)
(on b6 b3))
)
)

