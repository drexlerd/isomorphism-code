

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6  - block)
(:init
(on b1 b4)
(on b2 b6)
(on b3 b5)
(on-table b4)
(on-table b5)
(on b6 b3)
(clear b1)
(clear b2)
)
(:goal
(and
(on b1 b2)
(on b3 b1)
(on b4 b5)
(on b5 b3))
)
)


