;; blocks=3, percentage_new_tower=10, out_folder=., instance_id=274, seed=4

(define (problem blocksworld-274)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b1)
    (on b1 b2)
    (on b2 b3)
    (on-table b3))
 (:goal  (and 
    (clear b2)
    (on b2 b1)
    (on b1 b3)
    (on-table b3))))
