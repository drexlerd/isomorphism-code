

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b2 b3 b4 b5 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b5)
(on b3 b2)
(on-table b4)
(on-table b5)
(clear b1)
(clear b4)
)
(:goal
(and
(clear b1))
)
)


