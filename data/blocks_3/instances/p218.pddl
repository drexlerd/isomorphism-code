;; blocks=2, percentage_new_tower=40, out_folder=., instance_id=218, seed=8

(define (problem blocksworld-218)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b2)
    (on-table b2)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on-table b2))))
