;; blocks=3, percentage_new_tower=40, out_folder=., instance_id=337, seed=7

(define (problem blocksworld-337)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b1)
    (on-table b1)
    (clear b3)
    (on b3 b2)
    (on-table b2))
 (:goal  (and 
    (clear b2)
    (on-table b2)
    (clear b3)
    (on-table b3)
    (clear b1)
    (on-table b1))))
