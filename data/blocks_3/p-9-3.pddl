

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9  - block)
(:init
(on-table b1)
(on b2 b4)
(on b3 b9)
(on-table b4)
(on b5 b1)
(on-table b6)
(on-table b7)
(on-table b8)
(on b9 b2)
(clear b3)
(clear b5)
(clear b6)
(clear b7)
(clear b8)
)
(:goal
(and
(on b1 b6)
(on b4 b3)
(on b5 b9)
(on b6 b5)
(on b8 b2))
)
)


