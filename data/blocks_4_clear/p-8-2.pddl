

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on b1 b4)
(on-table b2)
(on b3 b6)
(on-table b4)
(on b5 b8)
(on-table b6)
(on-table b7)
(on b8 b3)
(clear b1)
(clear b2)
(clear b5)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


