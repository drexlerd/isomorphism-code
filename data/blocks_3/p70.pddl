;; blocks=1, percentage_new_tower=20, out_folder=., instance_id=70, seed=10

(define (problem blocksworld-70)
 (:domain blocksworld)
 (:objects b1 - object)
 (:init 
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1))))
