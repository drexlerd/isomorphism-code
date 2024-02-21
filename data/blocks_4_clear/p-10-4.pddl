

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b10)
(on b2 b1)
(on b3 b5)
(on b4 b3)
(on b5 b9)
(on-table b6)
(on b7 b8)
(on b8 b2)
(on b9 b6)
(on-table b10)
(clear b4)
(clear b7)
)
(:goal
(and
(clear b1))
)
)


