

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b5)
(on b2 b7)
(on b3 b8)
(on b4 b10)
(on b5 b2)
(on-table b6)
(on b7 b3)
(on b8 b4)
(on-table b9)
(on b10 b9)
(clear b1)
(clear b6)
)
(:goal
(and
(on b1 b2))
)
)


