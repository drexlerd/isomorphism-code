;; blocks=3, percentage_new_tower=20, out_folder=., instance_id=302, seed=2

(define (problem blocksworld-302)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b3)
    (on-table b3)
    (clear b2)
    (on-table b2)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on b2 b3)
    (on-table b3))))
