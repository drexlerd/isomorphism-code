;; blocks=5, percentage_new_tower=20, out_folder=., instance_id=540, seed=0

(define (problem blocksworld-540)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b5)
    (on b5 b3)
    (on b3 b1)
    (on b1 b4)
    (on b4 b2)
    (on-table b2))
 (:goal  (and 
    (clear b3)
    (on-table b3)
    (clear b2)
    (on b2 b1)
    (on b1 b4)
    (on b4 b5)
    (on-table b5))))
