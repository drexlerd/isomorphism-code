;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=591, seed=21

(define (problem blocksworld-591)
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
    (clear b2)
    (on-table b2)
    (clear b3)
    (on b3 b5)
    (on-table b5)
    (clear b4)
    (on b4 b1)
    (on-table b1))))
