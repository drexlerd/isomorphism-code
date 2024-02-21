

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b3 b4 b5 b6 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b5)
(on b3 b1)
(on-table b4)
(on-table b5)
(on b6 b3)
(clear b2)
(clear b6)
)
(:goal
(and
(on b1 b2))
)
)


