;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=592, seed=22

(define (problem blocksworld-592)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b1)
    (on b1 b3)
    (on b3 b4)
    (on-table b4)
    (clear b2)
    (on b2 b5)
    (on-table b5))
 (:goal  (and 
    (clear b3)
    (on b3 b4)
    (on b4 b5)
    (on-table b5)
    (clear b2)
    (on b2 b1)
    (on-table b1))))
