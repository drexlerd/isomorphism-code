;; blocks=5, percentage_new_tower=10, out_folder=., instance_id=523, seed=13

(define (problem blocksworld-523)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (arm-empty)
    (clear b4)
    (on b4 b2)
    (on b2 b3)
    (on-table b3)
    (clear b5)
    (on b5 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b5)
    (on b5 b1)
    (on b1 b4)
    (on b4 b3)
    (on-table b3))))
