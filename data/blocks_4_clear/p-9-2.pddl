

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b5)
(on b2 b1)
(on b3 b8)
(on b4 b9)
(on-table b5)
(on b6 b4)
(on b7 b3)
(on-table b8)
(on b9 b2)
(clear b6)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


