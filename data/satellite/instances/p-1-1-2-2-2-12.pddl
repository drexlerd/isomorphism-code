(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	thermograph0 - mode
	GroundStation1 - direction
	Star0 - direction
	Phenomenon2 - direction
	Planet3 - direction
)
(:init
	(supports instrument0 thermograph0)
	(calibration_target instrument0 GroundStation1)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Phenomenon2)
	(supports instrument1 thermograph0)
	(calibration_target instrument1 Star0)
	(on_board instrument1 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Phenomenon2)
)
(:goal (and
	(have_image Phenomenon2 thermograph0)
	(have_image Planet3 thermograph0)
))

)
