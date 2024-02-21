

(define (problem BW-rand-7)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7  - block)
(:init
(on-table b1)
(on-table b2)
(on b3 b5)
(on b4 b3)
(on-table b5)
(on b6 b1)
(on b7 b4)
(clear b2)
(clear b6)
(clear b7)
)
(:goal
(and
(on b3 b5)
(on b4 b7)
(on b5 b6)
(on b6 b1))
)
)


