;; blocks=1, percentage_new_tower=0, out_folder=., instance_id=12, seed=12

(define (problem blocksworld-12)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))