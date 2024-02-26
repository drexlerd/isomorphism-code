; Domain designed by Alfonso Gerevini and Alessandro Saetti
; This file has been automatically generated by the generator available from
; http://zeus.ing.unibs.it/ipc-5/generators/index.html

(define (problem TPP)
(:domain TPP-Propositional)
(:objects
	goods1 - goods
	truck1 truck2 truck3 - truck
	market1 market2 market3 - market
	depot1 depot2 - depot
	level0 level1 - level)

(:init
	(next level1 level0)
	(ready-to-load goods1 market1 level0)
	(ready-to-load goods1 market2 level0)
	(ready-to-load goods1 market3 level0)
	(stored goods1 level0)
	(loaded goods1 truck1 level0)
	(loaded goods1 truck2 level0)
	(loaded goods1 truck3 level0)
	(connected market1 market3)
	(connected market2 market3)
	(connected market3 market1)
	(connected market3 market2)
	(connected depot1 market2)
	(connected market2 depot1)
	(connected depot2 market2)
	(connected market2 depot2)
	(on-sale goods1 market1 level1)
	(on-sale goods1 market2 level0)
	(on-sale goods1 market3 level0)
	(at truck1 depot1)
	(at truck2 depot2)
	(at truck3 depot1))

(:goal (and
	(stored goods1 level1)))

)
