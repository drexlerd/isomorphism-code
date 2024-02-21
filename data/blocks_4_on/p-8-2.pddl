

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b5)
(on-table b2)
(on b3 b2)
(on b4 b8)
(on b5 b4)
(on b6 b1)
(on-table b7)
(on b8 b3)
(clear b6)
(clear b7)
)
(:goal
(and
(on b1 b2))
)
)


