

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on-table b1)
(on b2 b9)
(on-table b3)
(on b4 b8)
(on-table b5)
(on b6 b3)
(on b7 b6)
(on b8 b1)
(on b9 b4)
(on b10 b2)
(clear b5)
(clear b7)
(clear b10)
)
(:goal
(and
(clear b1))
)
)


