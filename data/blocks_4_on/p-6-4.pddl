

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b3 b4 b5 b6 )
(:init
(arm-empty)
(on b1 b2)
(on-table b2)
(on-table b3)
(on b4 b6)
(on-table b5)
(on b6 b5)
(clear b1)
(clear b3)
(clear b4)
)
(:goal
(and
(on b1 b2))
)
)


