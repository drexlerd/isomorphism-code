(define (problem DLOG-2-1-1)
	(:domain driverlog)
	(:objects
	driver1 - driver
	driver2 - driver
	truck1 - truck
	package1 - obj
	s0 - location
	s1 - location
	p1-0 - location
	)
	(:init
	(at driver1 s0)
	(at driver2 s0)
	(at truck1 s0)
	(empty truck1)
	(at package1 s0)
	(path s1 p1-0)
	(path p1-0 s1)
	(path s0 p1-0)
	(path p1-0 s0)
	(link s0 s1)
	(link s1 s0)
)
	(:goal (and
	(at driver1 s0)
	(at driver2 s0)
	(at truck1 s0)
	(at package1 s1)
	))


)
