

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b2)
(on b2 b7)
(on b3 b5)
(on-table b4)
(on-table b5)
(on b6 b1)
(on-table b7)
(clear b3)
(clear b4)
(clear b6)
)
(:goal
(and
(clear b1))
)
)


