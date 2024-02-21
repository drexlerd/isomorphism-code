

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b5)
(on b2 b10)
(on b3 b4)
(on b4 b1)
(on b5 b7)
(on b6 b8)
(on-table b7)
(on b8 b3)
(on-table b9)
(on b10 b9)
(clear b2)
(clear b6)
)
(:goal
(and
(on b1 b2))
)
)


