;; blocks=4, percentage_new_tower=40, out_folder=., instance_id=460, seed=10

(define (problem blocksworld-460)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (clear b2)
    (on b2 b1)
    (on b1 b4)
    (on-table b4)
    (clear b3)
    (on-table b3))
 (:goal  (and 
    (clear b2)
    (on b2 b3)
    (on b3 b1)
    (on b1 b4)
    (on-table b4))))
