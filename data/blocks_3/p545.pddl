;; blocks=5, percentage_new_tower=20, out_folder=., instance_id=545, seed=5

(define (problem blocksworld-545)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b3)
    (on b3 b5)
    (on b5 b2)
    (on b2 b4)
    (on b4 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b4)
    (on b4 b3)
    (on b3 b1)
    (on-table b1)
    (clear b5)
    (on-table b5))))
