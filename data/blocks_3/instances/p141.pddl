;; blocks=2, percentage_new_tower=0, out_folder=., instance_id=141, seed=21

(define (problem blocksworld-141)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b1)
    (on-table b1))))
