

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b2 b3 b4 b5 )
(:init
(arm-empty)
(on b1 b2)
(on b2 b3)
(on b3 b5)
(on-table b4)
(on b5 b4)
(clear b1)
)
(:goal
(and
(clear b1))
)
)


