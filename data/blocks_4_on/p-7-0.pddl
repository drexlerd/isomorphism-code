

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b6)
(on b2 b3)
(on-table b3)
(on b4 b7)
(on-table b5)
(on-table b6)
(on-table b7)
(clear b1)
(clear b2)
(clear b4)
(clear b5)
)
(:goal
(and
(on b1 b2))
)
)


