;; blocks=2, percentage_new_tower=10, out_folder=., instance_id=174, seed=24

(define (problem blocksworld-174)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b1)
    (on-table b1))))
