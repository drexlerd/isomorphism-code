;; blocks=5, percentage_new_tower=10, out_folder=., instance_id=531, seed=21

(define (problem blocksworld-531)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b3)
    (on b3 b1)
    (on b1 b5)
    (on b5 b2)
    (on-table b2)
    (clear b4)
    (on-table b4))
 (:goal  (and 
    (clear b1)
    (on b1 b5)
    (on b5 b4)
    (on b4 b3)
    (on b3 b2)
    (on-table b2))))
