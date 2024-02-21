

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b3 b4 b5 b6 )
(:init
(arm-empty)
(on-table b1)
(on b2 b6)
(on b3 b5)
(on b4 b2)
(on b5 b1)
(on b6 b3)
(clear b4)
)
(:goal
(and
(clear b1))
)
)


