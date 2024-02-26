; Domain designed by Alfonso Gerevini and Alessandro Saetti
; This file has been automatically generated by the generator available from
; http://zeus.ing.unibs.it/ipc-5/generators/index.html

(define (problem TPP)
(:domain TPP-Propositional)
(:objects
	goods1 goods2 goods3 - goods
	truck1 truck2 truck3 - truck
	market1 market2 - market
	depot1 depot2 depot3 - depot
	level0 level1 level2 level3 - level)

(:init
	(next level1 level0)
	(next level2 level1)
	(next level3 level2)
	(ready-to-load goods1 market1 level0)
	(ready-to-load goods1 market2 level0)
	(ready-to-load goods2 market1 level0)
	(ready-to-load goods2 market2 level0)
	(ready-to-load goods3 market1 level0)
	(ready-to-load goods3 market2 level0)
	(stored goods1 level0)
	(stored goods2 level0)
	(stored goods3 level0)
	(loaded goods1 truck1 level0)
	(loaded goods1 truck2 level0)
	(loaded goods1 truck3 level0)
	(loaded goods2 truck1 level0)
	(loaded goods2 truck2 level0)
	(loaded goods2 truck3 level0)
	(loaded goods3 truck1 level0)
	(loaded goods3 truck2 level0)
	(loaded goods3 truck3 level0)
	(connected market1 market2)
	(connected market2 market1)
	(connected depot1 market2)
	(connected market2 depot1)
	(connected depot2 market1)
	(connected market1 depot2)
	(connected depot3 market2)
	(connected market2 depot3)
	(on-sale goods1 market1 level2)
	(on-sale goods2 market1 level2)
	(on-sale goods3 market1 level0)
	(on-sale goods1 market2 level1)
	(on-sale goods2 market2 level1)
	(on-sale goods3 market2 level3)
	(at truck1 depot2)
	(at truck2 depot2)
	(at truck3 depot3))

(:goal (and
	(stored goods1 level3)
	(stored goods2 level1)
	(stored goods3 level1)))

)
