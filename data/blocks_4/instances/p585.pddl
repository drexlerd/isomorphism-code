;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=585, seed=15

(define (problem blocksworld-585)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (arm-empty)
    (clear b3)
    (on b3 b2)
    (on b2 b4)
    (on-table b4)
    (clear b1)
    (on-table b1)
    (clear b5)
    (on-table b5))
 (:goal  (and 
    (clear b4)
    (on b4 b2)
    (on-table b2)
    (clear b1)
    (on-table b1)
    (clear b3)
    (on b3 b5)
    (on-table b5))))
