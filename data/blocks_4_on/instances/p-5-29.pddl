

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b3 b4 b5 )
(:init
(arm-empty)
(on b1 b3)
(on-table b2)
(on b3 b4)
(on-table b4)
(on-table b5)
(clear b1)
(clear b2)
(clear b5)
)
(:goal
(and
(on b1 b2))
)
)


