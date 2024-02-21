

(define (problem BW-rand-8)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8  - block)
(:init
(on b1 b6)
(on b2 b3)
(on b3 b4)
(on b4 b5)
(on b5 b1)
(on b6 b7)
(on-table b7)
(on b8 b2)
(clear b8)
)
(:goal
(and
(on b2 b7)
(on b3 b6)
(on b4 b3)
(on b5 b1)
(on b6 b2)
(on b8 b4))
)
)


