;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=595, seed=25

(define (problem blocksworld-595)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b5)
    (on-table b5)
    (clear b4)
    (on b4 b1)
    (on b1 b3)
    (on b3 b2)
    (on-table b2))
 (:goal  (and 
    (clear b4)
    (on b4 b3)
    (on b3 b2)
    (on-table b2)
    (clear b5)
    (on b5 b1)
    (on-table b1))))
