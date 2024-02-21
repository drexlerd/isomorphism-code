

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on-table b1)
(on b2 b1)
(on b3 b8)
(on b4 b5)
(on b5 b2)
(on-table b6)
(on b7 b4)
(on b8 b6)
(on b9 b7)
(clear b3)
(clear b9)
)
(:goal
(and
(on b1 b2))
)
)


