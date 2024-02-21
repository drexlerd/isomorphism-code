

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on-table b1)
(on b2 b3)
(on b3 b9)
(on b4 b2)
(on b5 b8)
(on b6 b4)
(on b7 b6)
(on b8 b1)
(on-table b9)
(clear b5)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


