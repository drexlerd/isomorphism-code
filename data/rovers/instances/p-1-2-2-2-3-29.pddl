(define (problem roverprob29) (:domain Rover)
(:objects
	general - Lander
	colour high_res low_res - Mode
	rover0 rover1 - Rover
	rover0store rover1store - Store
	waypoint0 waypoint1 waypoint2 - Waypoint
	camera0 - Camera
	objective0 objective1 - Objective
	)
(:init
	(visible waypoint0 waypoint1)
	(visible waypoint1 waypoint0)
	(visible waypoint0 waypoint2)
	(visible waypoint2 waypoint0)
	(visible waypoint2 waypoint1)
	(visible waypoint1 waypoint2)
	(at_soil_sample waypoint0)
	(at_soil_sample waypoint1)
	(at_rock_sample waypoint1)
	(at_lander general waypoint1)
	(channel_free general)
	(at rover0 waypoint2)
	(available rover0)
	(store_of rover0store rover0)
	(empty rover0store)
	(equipped_for_rock_analysis rover0)
	(equipped_for_imaging rover0)
	(can_traverse rover0 waypoint2 waypoint0)
	(can_traverse rover0 waypoint0 waypoint2)
	(at rover1 waypoint0)
	(available rover1)
	(store_of rover1store rover1)
	(empty rover1store)
	(equipped_for_rock_analysis rover1)
	(can_traverse rover1 waypoint0 waypoint1)
	(can_traverse rover1 waypoint1 waypoint0)
	(can_traverse rover1 waypoint0 waypoint2)
	(can_traverse rover1 waypoint2 waypoint0)
	(on_board camera0 rover0)
	(calibration_target camera0 objective1)
	(supports camera0 colour)
	(supports camera0 high_res)
	(supports camera0 low_res)
	(visible_from objective0 waypoint1)
	(visible_from objective1 waypoint2)
)

(:goal (and
(communicated_rock_data waypoint1)
(communicated_image_data objective1 low_res)
	)
)
)
