

(define (problem BW-rand-9)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9  - block)
(:init
(on b1 b2)
(on b2 b6)
(on-table b3)
(on-table b4)
(on b5 b4)
(on-table b6)
(on b7 b8)
(on b8 b1)
(on-table b9)
(clear b3)
(clear b5)
(clear b7)
(clear b9)
)
(:goal
(and
(on b2 b4)
(on b3 b7)
(on b4 b8)
(on b5 b6)
(on b6 b3)
(on b9 b5))
)
)


