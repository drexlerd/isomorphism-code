

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b2 b3 b4 b5 )
(:init
(arm-empty)
(on-table b1)
(on-table b2)
(on b3 b1)
(on-table b4)
(on b5 b4)
(clear b2)
(clear b3)
(clear b5)
)
(:goal
(and
(clear b1))
)
)


