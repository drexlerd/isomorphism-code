;; blocks=2, percentage_new_tower=20, out_folder=., instance_id=199, seed=19

(define (problem blocksworld-199)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b2)
    (on-table b2)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on-table b2))))
