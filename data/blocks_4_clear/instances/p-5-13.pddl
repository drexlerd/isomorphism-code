

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b2 b3 b4 b5 )
(:init
(arm-empty)
(on b1 b3)
(on-table b2)
(on-table b3)
(on b4 b5)
(on b5 b1)
(clear b2)
(clear b4)
)
(:goal
(and
(clear b1))
)
)


