

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9  - block)
(:init
(on b1 b9)
(on b2 b4)
(on-table b3)
(on b4 b8)
(on-table b5)
(on b6 b1)
(on-table b7)
(on b8 b3)
(on b9 b7)
(clear b2)
(clear b5)
(clear b6)
)
(:goal
(and
(on b1 b3)
(on b3 b9)
(on b4 b6)
(on b5 b1)
(on b8 b2))
)
)

