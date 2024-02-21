

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b8)
(on b2 b3)
(on b3 b7)
(on b4 b1)
(on b5 b2)
(on b6 b5)
(on-table b7)
(on b8 b6)
(clear b4)
)
(:goal
(and
(on b1 b3)
(on b3 b6)
(on b4 b8)
(on b5 b1)
(on b6 b4)
(on b8 b2))
)
)


