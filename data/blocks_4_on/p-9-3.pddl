

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b4)
(on-table b2)
(on b3 b1)
(on b4 b2)
(on b5 b6)
(on b6 b3)
(on b7 b8)
(on-table b8)
(on b9 b5)
(clear b7)
(clear b9)
)
(:goal
(and
(on b1 b2))
)
)


