

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b4)
(on b2 b5)
(on b3 b2)
(on b4 b3)
(on b5 b9)
(on-table b6)
(on b7 b6)
(on-table b8)
(on b9 b10)
(on b10 b7)
(clear b1)
(clear b8)
)
(:goal
(and
(clear b1))
)
)


