;; blocks=5, percentage_new_tower=0, out_folder=., instance_id=487, seed=7

(define (problem blocksworld-487)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on b2 b3)
    (on b3 b5)
    (on b5 b1)
    (on b1 b4)
    (on-table b4))
 (:goal  (and 
    (clear b3)
    (on b3 b5)
    (on b5 b4)
    (on b4 b1)
    (on b1 b2)
    (on-table b2))))
