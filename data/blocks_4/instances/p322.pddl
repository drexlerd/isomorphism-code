;; blocks=3, percentage_new_tower=20, out_folder=., instance_id=322, seed=22

(define (problem blocksworld-322)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (arm-empty)
    (clear b3)
    (on b3 b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on-table b2)
    (clear b1)
    (on-table b1)
    (clear b3)
    (on-table b3))))
