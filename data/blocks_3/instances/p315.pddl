;; blocks=3, percentage_new_tower=20, out_folder=., instance_id=315, seed=15

(define (problem blocksworld-315)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b2)
    (on b2 b3)
    (on b3 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b3)
    (on b3 b1)
    (on-table b1))))
