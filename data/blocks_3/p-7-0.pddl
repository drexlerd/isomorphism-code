

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7  - block)
(:init
(on b1 b5)
(on-table b2)
(on b3 b2)
(on b4 b6)
(on b5 b4)
(on b6 b7)
(on-table b7)
(clear b1)
(clear b3)
)
(:goal
(and
(on b1 b4)
(on b2 b1)
(on b6 b7)
(on b7 b2))
)
)


