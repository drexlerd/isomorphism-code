;; blocks=4, percentage_new_tower=40, out_folder=., instance_id=477, seed=27

(define (problem blocksworld-477)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (clear b3)
    (on b3 b4)
    (on b4 b1)
    (on b1 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on b2 b3)
    (on-table b3)
    (clear b4)
    (on-table b4))))
