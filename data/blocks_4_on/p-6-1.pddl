

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b3 b4 b5 b6 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b6)
(on-table b3)
(on-table b4)
(on b5 b2)
(on b6 b1)
(clear b3)
(clear b5)
)
(:goal
(and
(on b1 b2))
)
)


