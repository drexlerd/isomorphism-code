

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b5)
(on b2 b9)
(on-table b3)
(on b4 b1)
(on-table b5)
(on b6 b4)
(on b7 b3)
(on b8 b7)
(on b9 b6)
(clear b2)
(clear b8)
)
(:goal
(and
(on b1 b2))
)
)


