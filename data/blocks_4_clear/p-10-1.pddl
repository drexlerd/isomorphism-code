

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b3)
(on-table b2)
(on b3 b4)
(on-table b4)
(on b5 b9)
(on b6 b8)
(on b7 b6)
(on b8 b10)
(on-table b9)
(on b10 b2)
(clear b1)
(clear b5)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


