

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8  - block)
(:init
(on b1 b6)
(on b2 b4)
(on b3 b8)
(on b4 b3)
(on-table b5)
(on b6 b7)
(on b7 b5)
(on-table b8)
(clear b1)
(clear b2)
)
(:goal
(and
(on b2 b4)
(on b3 b1)
(on b4 b6)
(on b6 b7)
(on b7 b8))
)
)


