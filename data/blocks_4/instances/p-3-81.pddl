

(define (problem BW-rand-3)
(:domain blocksworld)
(:objects b1 b2 b3 )
(:init
(arm-empty)
(on-table b1)
(on b2 b1)
(on b3 b2)
(clear b3)
)
(:goal
(and
(on b1 b3))
)
)


