

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b3 b4 b5 b6 )
(:init
(arm-empty)
(on-table b1)
(on b2 b6)
(on b3 b4)
(on b4 b5)
(on-table b5)
(on-table b6)
(clear b1)
(clear b2)
(clear b3)
)
(:goal
(and
(clear b1))
)
)


