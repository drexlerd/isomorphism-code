

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10  - block)
(:init
(on b1 b7)
(on b2 b4)
(on-table b3)
(on b4 b9)
(on b5 b10)
(on-table b6)
(on b7 b2)
(on-table b8)
(on b9 b8)
(on b10 b3)
(clear b1)
(clear b5)
(clear b6)
)
(:goal
(and
(on b1 b6)
(on b2 b3)
(on b5 b2)
(on b8 b9)
(on b10 b4))
)
)

