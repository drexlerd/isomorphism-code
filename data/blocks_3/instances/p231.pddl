;; blocks=2, percentage_new_tower=40, out_folder=., instance_id=231, seed=21

(define (problem blocksworld-231)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on-table b2))))
