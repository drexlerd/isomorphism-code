
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Instance file automatically generated by the Tarski FSTRIPS writer
;;; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem reward-3x1)
    (:domain reward-strips)

    (:objects
        c_0_0 c_1_0 c_2_0 - cell
    )

    (:init
        (adjacent c_0_0 c_1_0)
        (adjacent c_1_0 c_2_0)
        (adjacent c_1_0 c_0_0)
        (adjacent c_2_0 c_1_0)
        (at c_0_0)
        (unblocked c_1_0)
        (unblocked c_2_0)
        (unblocked c_0_0)
        (reward c_1_0)
        (reward c_2_0)
    )

    (:goal
        (and (picked c_2_0) (picked c_1_0))
    )

    
    
    
)

