;; blocks=4, percentage_new_tower=20, out_folder=., instance_id=425, seed=5

(define (problem blocksworld-425)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (clear b1)
    (on b1 b3)
    (on b3 b4)
    (on-table b4)
    (clear b2)
    (on-table b2))
 (:goal  (and 
    (clear b3)
    (on b3 b4)
    (on b4 b1)
    (on b1 b2)
    (on-table b2))))
