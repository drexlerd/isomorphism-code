

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8  - block)
(:init
(on-table b1)
(on-table b2)
(on b3 b8)
(on-table b4)
(on b5 b6)
(on b6 b1)
(on b7 b5)
(on b8 b2)
(clear b3)
(clear b4)
(clear b7)
)
(:goal
(and
(on b1 b8)
(on b2 b1)
(on b4 b7)
(on b5 b4)
(on b7 b3)
(on b8 b5))
)
)


