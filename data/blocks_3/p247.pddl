;; blocks=3, percentage_new_tower=0, out_folder=., instance_id=247, seed=7

(define (problem blocksworld-247)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b1)
    (on b1 b3)
    (on b3 b2)
    (on-table b2))
 (:goal  (and 
    (clear b2)
    (on b2 b1)
    (on b1 b3)
    (on-table b3))))
