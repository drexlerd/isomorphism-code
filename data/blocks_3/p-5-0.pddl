

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5  - block)
(:init
(on b1 b2)
(on-table b2)
(on b3 b1)
(on b4 b5)
(on b5 b3)
(clear b4)
)
(:goal
(and
(on b1 b3)
(on b3 b2)
(on b5 b4))
)
)


