

(define (problem BW-rand-10)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10  - block)
(:init
(on b1 b7)
(on b2 b3)
(on-table b3)
(on b4 b9)
(on-table b5)
(on b6 b4)
(on-table b7)
(on b8 b2)
(on b9 b1)
(on b10 b6)
(clear b5)
(clear b8)
(clear b10)
)
(:goal
(and
(on b2 b4)
(on b3 b1)
(on b4 b6)
(on b5 b8)
(on b7 b9)
(on b8 b10)
(on b9 b2)
(on b10 b7))
)
)


