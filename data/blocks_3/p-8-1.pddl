

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8  - block)
(:init
(on b1 b7)
(on-table b2)
(on b3 b6)
(on b4 b2)
(on b5 b8)
(on-table b6)
(on b7 b3)
(on b8 b1)
(clear b4)
(clear b5)
)
(:goal
(and
(on b1 b7)
(on b3 b8)
(on b4 b3)
(on b6 b5)
(on b7 b6)
(on b8 b2))
)
)


