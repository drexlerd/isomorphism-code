;; blocks=1, percentage_new_tower=10, out_folder=., instance_id=41, seed=11

(define (problem blocksworld-41)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
