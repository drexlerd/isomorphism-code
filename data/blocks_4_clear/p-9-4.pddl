

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b2)
(on b2 b6)
(on b3 b1)
(on-table b4)
(on b5 b4)
(on b6 b7)
(on-table b7)
(on b8 b5)
(on-table b9)
(clear b3)
(clear b8)
(clear b9)
)
(:goal
(and
(clear b1))
)
)


