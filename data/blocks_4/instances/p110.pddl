;; blocks=1, percentage_new_tower=40, out_folder=., instance_id=110, seed=20

(define (problem blocksworld-110)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (arm-empty)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
