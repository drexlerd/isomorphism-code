

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b6)
(on-table b2)
(on-table b3)
(on b4 b10)
(on b5 b1)
(on-table b6)
(on b7 b4)
(on b8 b3)
(on b9 b5)
(on b10 b8)
(clear b2)
(clear b7)
(clear b9)
)
(:goal
(and
(on b1 b2))
)
)


