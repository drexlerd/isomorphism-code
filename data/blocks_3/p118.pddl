;; blocks=1, percentage_new_tower=40, out_folder=., instance_id=118, seed=28

(define (problem blocksworld-118)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
