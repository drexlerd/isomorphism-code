

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9  - block)
(:init
(on b1 b9)
(on-table b2)
(on b3 b8)
(on b4 b7)
(on b5 b6)
(on-table b6)
(on-table b7)
(on b8 b4)
(on b9 b3)
(clear b1)
(clear b2)
(clear b5)
)
(:goal
(and
(on b1 b7)
(on b3 b1)
(on b5 b8)
(on b6 b5)
(on b7 b9)
(on b9 b2))
)
)


