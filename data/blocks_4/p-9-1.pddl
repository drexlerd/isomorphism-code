

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b6)
(on b2 b3)
(on b3 b4)
(on b4 b8)
(on b5 b7)
(on-table b6)
(on b7 b9)
(on b8 b1)
(on-table b9)
(clear b2)
(clear b5)
)
(:goal
(and
(on b1 b5)
(on b2 b7)
(on b3 b2)
(on b4 b8)
(on b6 b9)
(on b7 b6))
)
)


