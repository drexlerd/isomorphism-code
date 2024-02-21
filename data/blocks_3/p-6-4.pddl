

(define (problem BW-rand-6)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6  - block)
(:init
(on b1 b2)
(on-table b2)
(on b3 b6)
(on b4 b5)
(on b5 b3)
(on-table b6)
(clear b1)
(clear b4)
)
(:goal
(and
(on b1 b2)
(on b2 b3)
(on b4 b6))
)
)


