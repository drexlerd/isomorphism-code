;; blocks=5, percentage_new_tower=40, out_folder=., instance_id=587, seed=17

(define (problem blocksworld-587)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b2)
    (on b2 b1)
    (on-table b1)
    (clear b5)
    (on-table b5)
    (clear b3)
    (on b3 b4)
    (on-table b4))
 (:goal  (and 
    (clear b2)
    (on-table b2)
    (clear b5)
    (on-table b5)
    (clear b4)
    (on b4 b1)
    (on-table b1)
    (clear b3)
    (on-table b3))))
