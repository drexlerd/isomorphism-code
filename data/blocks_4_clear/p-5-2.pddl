

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b3 b4 b5 )
(:init
(arm-empty)
(on b1 b5)
(on-table b2)
(on-table b3)
(on-table b4)
(on b5 b3)
(clear b1)
(clear b2)
(clear b4)
)
(:goal
(and
(clear b1))
)
)


