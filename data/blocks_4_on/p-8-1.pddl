

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b7)
(on-table b2)
(on b3 b8)
(on-table b4)
(on b5 b1)
(on b6 b2)
(on b7 b6)
(on b8 b4)
(clear b3)
(clear b5)
)
(:goal
(and
(on b1 b2))
)
)


