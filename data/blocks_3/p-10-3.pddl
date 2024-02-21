

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10  - block)
(:init
(on b1 b4)
(on b2 b1)
(on b3 b5)
(on-table b4)
(on-table b5)
(on b6 b9)
(on b7 b6)
(on b8 b3)
(on b9 b8)
(on b10 b7)
(clear b2)
(clear b10)
)
(:goal
(and
(on b2 b4)
(on b4 b1)
(on b6 b8)
(on b7 b3)
(on b8 b7)
(on b9 b5)
(on b10 b2))
)
)


