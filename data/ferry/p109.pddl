;; cars=2, locations=3, seed=19, instance_id=109, out_folder=.

(define (problem ferry-109)
 (:domain ferry)
 (:objects 
    car1 car2 - car
    loc1 loc2 loc3 - location
 )
 (:init 
    (empty-ferry)
    (at-ferry loc2)
    (at car1 loc3)
    (at car2 loc1)
)
 (:goal  (and (at car1 loc1)
   (at car2 loc3))))
