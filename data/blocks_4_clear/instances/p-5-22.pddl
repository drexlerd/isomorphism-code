

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b2 b3 b4 b5 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b5)
(on b3 b1)
(on b4 b2)
(on-table b5)
(clear b3)
)
(:goal
(and
(clear b1))
)
)


