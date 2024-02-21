

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9  - block)
(:init
(on b1 b5)
(on b2 b7)
(on b3 b6)
(on b4 b9)
(on b5 b8)
(on-table b6)
(on-table b7)
(on b8 b3)
(on b9 b2)
(clear b1)
(clear b4)
)
(:goal
(and
(on b1 b3)
(on b3 b8)
(on b4 b1)
(on b6 b5)
(on b7 b9)
(on b8 b7)
(on b9 b6))
)
)


