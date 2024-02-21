

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b8)
(on-table b3)
(on-table b4)
(on b5 b7)
(on b6 b2)
(on b7 b1)
(on b8 b3)
(clear b5)
(clear b6)
)
(:goal
(and
(on b1 b2))
)
)


