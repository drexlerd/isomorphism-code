

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 )
(:init
(arm-empty)
(on b1 b5)
(on-table b2)
(on b3 b7)
(on b4 b2)
(on b5 b3)
(on-table b6)
(on b7 b4)
(clear b1)
(clear b6)
)
(:goal
(and
(clear b1))
)
)


