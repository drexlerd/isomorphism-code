;; blocks=4, percentage_new_tower=10, out_folder=., instance_id=413, seed=23

(define (problem blocksworld-413)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (clear b1)
    (on b1 b2)
    (on b2 b3)
    (on b3 b4)
    (on-table b4))
 (:goal  (and 
    (clear b2)
    (on b2 b4)
    (on b4 b1)
    (on b1 b3)
    (on-table b3))))
