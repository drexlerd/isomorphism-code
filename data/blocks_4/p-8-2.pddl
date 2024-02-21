

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on-table b1)
(on-table b2)
(on b3 b5)
(on b4 b3)
(on-table b5)
(on-table b6)
(on b7 b6)
(on b8 b1)
(clear b2)
(clear b4)
(clear b7)
(clear b8)
)
(:goal
(and
(on b1 b5)
(on b4 b3)
(on b5 b7)
(on b7 b2)
(on b8 b6))
)
)


