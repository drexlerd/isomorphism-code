

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on-table b1)
(on b2 b1)
(on b3 b6)
(on b4 b3)
(on-table b5)
(on b6 b5)
(on-table b7)
(clear b2)
(clear b4)
(clear b7)
)
(:goal
(and
(on b1 b2))
)
)


