;; blocks=2, percentage_new_tower=10, out_folder=., instance_id=171, seed=21

(define (problem blocksworld-171)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b1)
    (on b1 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on-table b2))))
