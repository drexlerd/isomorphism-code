

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b8)
(on-table b2)
(on b3 b6)
(on b4 b5)
(on-table b5)
(on b6 b1)
(on b7 b4)
(on b8 b2)
(on-table b9)
(on b10 b7)
(clear b3)
(clear b9)
(clear b10)
)
(:goal
(and
(on b1 b2))
)
)

