

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on-table b1)
(on b2 b5)
(on-table b3)
(on b4 b2)
(on-table b5)
(on-table b6)
(on b7 b6)
(on b8 b7)
(on b9 b4)
(clear b1)
(clear b3)
(clear b8)
(clear b9)
)
(:goal
(and
(clear b1))
)
)


