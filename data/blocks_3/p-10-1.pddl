

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10  - block)
(:init
(on-table b1)
(on b2 b9)
(on b3 b8)
(on-table b4)
(on b5 b3)
(on-table b6)
(on-table b7)
(on b8 b1)
(on b9 b6)
(on b10 b5)
(clear b2)
(clear b4)
(clear b7)
(clear b10)
)
(:goal
(and
(on b1 b10)
(on b4 b9)
(on b6 b5)
(on b7 b1)
(on b8 b7))
)
)


