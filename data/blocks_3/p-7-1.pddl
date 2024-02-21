

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7  - block)
(:init
(on b1 b5)
(on-table b2)
(on b3 b2)
(on b4 b3)
(on b5 b6)
(on-table b6)
(on b7 b1)
(clear b4)
(clear b7)
)
(:goal
(and
(on b1 b2)
(on b2 b5)
(on b3 b7)
(on b4 b3)
(on b6 b4))
)
)


