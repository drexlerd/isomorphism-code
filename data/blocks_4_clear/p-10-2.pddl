

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on-table b1)
(on b2 b10)
(on-table b3)
(on-table b4)
(on b5 b8)
(on b6 b9)
(on b7 b1)
(on b8 b6)
(on-table b9)
(on b10 b5)
(clear b2)
(clear b3)
(clear b4)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


