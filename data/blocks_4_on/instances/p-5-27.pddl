

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b3 b4 b5 )
(:init
(arm-empty)
(on-table b1)
(on-table b2)
(on b3 b4)
(on b4 b2)
(on b5 b1)
(clear b3)
(clear b5)
)
(:goal
(and
(on b1 b2))
)
)


