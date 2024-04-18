;; blocks=5, percentage_new_tower=10, out_folder=., instance_id=537, seed=27

(define (problem blocksworld-537)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on b2 b1)
    (on b1 b3)
    (on b3 b5)
    (on b5 b4)
    (on-table b4))
 (:goal  (and 
    (clear b1)
    (on b1 b5)
    (on b5 b2)
    (on b2 b4)
    (on b4 b3)
    (on-table b3))))
