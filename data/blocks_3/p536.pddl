;; blocks=5, percentage_new_tower=10, out_folder=., instance_id=536, seed=26

(define (problem blocksworld-536)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b5)
    (on b5 b2)
    (on-table b2)
    (clear b4)
    (on b4 b1)
    (on b1 b3)
    (on-table b3))
 (:goal  (and 
    (clear b5)
    (on b5 b4)
    (on b4 b3)
    (on-table b3)
    (clear b1)
    (on b1 b2)
    (on-table b2))))
