;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=571, seed=1

(define (problem blocksworld-571)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b5)
    (on b5 b2)
    (on b2 b3)
    (on b3 b4)
    (on b4 b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1)
    (clear b3)
    (on b3 b5)
    (on b5 b4)
    (on b4 b2)
    (on-table b2))))
