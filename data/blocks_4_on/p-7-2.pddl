

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b7)
(on b2 b5)
(on b3 b1)
(on b4 b6)
(on b5 b3)
(on-table b6)
(on-table b7)
(clear b2)
(clear b4)
)
(:goal
(and
(on b1 b2))
)
)


