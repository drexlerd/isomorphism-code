;; blocks=5, percentage_new_tower=20, out_folder=., instance_id=544, seed=4

(define (problem blocksworld-544)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b4)
    (on b4 b1)
    (on b1 b3)
    (on b3 b2)
    (on-table b2)
    (clear b5)
    (on-table b5))
 (:goal  (and 
    (clear b4)
    (on b4 b1)
    (on b1 b3)
    (on b3 b5)
    (on b5 b2)
    (on-table b2))))
