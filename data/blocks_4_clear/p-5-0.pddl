

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b3 b4 b5 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b1)
(on b3 b4)
(on b4 b5)
(on-table b5)
(clear b2)
)
(:goal
(and
(clear b1))
)
)


