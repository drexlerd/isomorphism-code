;; blocks=1, percentage_new_tower=20, out_folder=., instance_id=78, seed=18

(define (problem blocksworld-78)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
