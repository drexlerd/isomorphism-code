

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b2)
(on-table b2)
(on b3 b1)
(on-table b4)
(on-table b5)
(on b6 b5)
(on b7 b6)
(clear b3)
(clear b4)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


