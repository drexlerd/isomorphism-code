(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	image1 - mode
	thermograph0 - mode
	Star0 - direction
	Star1 - direction
	Star2 - direction
	Phenomenon3 - direction
)
(:init
	(supports instrument0 thermograph0)
	(supports instrument0 image1)
	(calibration_target instrument0 Star1)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Phenomenon3)
)
(:goal (and
	(have_image Star2 thermograph0)
	(have_image Phenomenon3 thermograph0)
))

)
