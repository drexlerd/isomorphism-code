

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6  - block)
(:init
(on b1 b3)
(on-table b2)
(on b3 b2)
(on b4 b1)
(on b5 b4)
(on b6 b5)
(clear b6)
)
(:goal
(and
(on b1 b4)
(on b2 b1)
(on b3 b5)
(on b5 b6))
)
)


