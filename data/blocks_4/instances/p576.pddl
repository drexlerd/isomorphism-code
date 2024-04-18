;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=576, seed=6

(define (problem blocksworld-576)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on-table b2)
    (clear b4)
    (on b4 b3)
    (on-table b3)
    (clear b5)
    (on b5 b1)
    (on-table b1))
 (:goal  (and 
    (clear b4)
    (on b4 b3)
    (on-table b3)
    (clear b1)
    (on b1 b2)
    (on b2 b5)
    (on-table b5))))
