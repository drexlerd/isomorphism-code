

(define (problem BW-rand-4)
(:domain blocksworld)
(:objects b1 b2 b3 b4  - block)
(:init
(on-table b1)
(on-table b2)
(on b3 b4)
(on-table b4)
(clear b1)
(clear b2)
(clear b3)
)
(:goal
(and
(on b2 b4))
)
)


