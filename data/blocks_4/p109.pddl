;; blocks=1, percentage_new_tower=40, out_folder=., instance_id=109, seed=19

(define (problem blocksworld-109)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (arm-empty)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
