

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b3)
(on-table b2)
(on b3 b5)
(on b4 b2)
(on b5 b6)
(on b6 b7)
(on b7 b9)
(on-table b8)
(on-table b9)
(clear b1)
(clear b4)
(clear b8)
)
(:goal
(and
(clear b1))
)
)


