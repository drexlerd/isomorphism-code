;; blocks=3, percentage_new_tower=10, out_folder=., instance_id=276, seed=6

(define (problem blocksworld-276)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b1)
    (on b1 b3)
    (on b3 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b3)
    (on b3 b2)
    (on-table b2))))
