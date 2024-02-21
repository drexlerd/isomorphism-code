

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7  - block)
(:init
(on-table b1)
(on-table b2)
(on-table b3)
(on b4 b7)
(on b5 b1)
(on-table b6)
(on b7 b6)
(clear b2)
(clear b3)
(clear b4)
(clear b5)
)
(:goal
(and
(on b1 b5)
(on b2 b7)
(on b3 b2)
(on b6 b4)
(on b7 b6))
)
)


