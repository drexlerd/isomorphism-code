;; blocks=4, percentage_new_tower=10, out_folder=., instance_id=398, seed=8

(define (problem blocksworld-398)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (arm-empty)
    (clear b3)
    (on b3 b2)
    (on b2 b4)
    (on b4 b1)
    (on-table b1))
 (:goal  (and 
    (clear b4)
    (on b4 b1)
    (on b1 b2)
    (on-table b2)
    (clear b3)
    (on-table b3))))
