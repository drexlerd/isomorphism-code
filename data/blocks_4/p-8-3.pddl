

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b6)
(on b3 b4)
(on b4 b7)
(on-table b5)
(on-table b6)
(on b7 b2)
(on b8 b1)
(clear b5)
(clear b8)
)
(:goal
(and
(on b2 b6)
(on b4 b3)
(on b5 b4)
(on b6 b8)
(on b7 b5)
(on b8 b7))
)
)


