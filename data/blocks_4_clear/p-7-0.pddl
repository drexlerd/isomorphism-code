

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on-table b1)
(on-table b2)
(on-table b3)
(on b4 b7)
(on-table b5)
(on-table b6)
(on b7 b1)
(clear b2)
(clear b3)
(clear b4)
(clear b5)
(clear b6)
)
(:goal
(and
(clear b1))
)
)


