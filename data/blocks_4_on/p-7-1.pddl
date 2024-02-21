

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b6)
(on b3 b5)
(on-table b4)
(on b5 b7)
(on-table b6)
(on b7 b2)
(clear b1)
(clear b3)
)
(:goal
(and
(on b1 b2))
)
)


