

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b9)
(on-table b3)
(on b4 b1)
(on-table b5)
(on b6 b7)
(on-table b7)
(on b8 b5)
(on b9 b8)
(clear b2)
(clear b4)
(clear b6)
)
(:goal
(and
(on b1 b2))
)
)


