;; blocks=1, percentage_new_tower=10, out_folder=., instance_id=39, seed=9

(define (problem blocksworld-39)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
