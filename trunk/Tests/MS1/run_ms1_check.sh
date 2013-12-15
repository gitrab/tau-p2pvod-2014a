#!/bin/bash
#
#	run_ms1_check.sh
#
#	15-12-2013
#	Nir Malbin

seeds=2; iter=5;

CheckTest () {
	testdir="$alg.$vpeers.$mode.$gap"
	./run_test_check.sh $vpeers $gap $1/$testdir $2
}

alg='in_order'; vpeers=4; peers=26; mode='empty'; gap=2
CheckTest $1 $2
alg='in_order'; vpeers=16; peers=14; mode='empty'; gap=0
CheckTest $1 $2
alg='rarest_first'; vpeers=4; peers=26; mode='empty'; gap=2
CheckTest $1 $2
alg='rarest_first'; vpeers=16; peers=14; mode='empty'; gap=2
CheckTest $1 $2
alg='in_order'; vpeers=16; peers=14; mode='full'; gap=0
CheckTest $1 $2
alg='in_order'; vpeers=4; peers=26; mode='empty'; gap=0
CheckTest $1 $2
alg='rarest_first'; vpeers=16; peers=14; mode='full'; gap=0
CheckTest $1 $2
alg='in_order'; vpeers=4; peers=26; mode='full'; gap=0
CheckTest $1 $2
alg='rarest_first'; vpeers=4; peers=26; mode='full'; gap=0
CheckTest $1 $2
alg='rarest_first'; vpeers=4; peers=26; mode='empty'; gap=0
CheckTest $1 $2
alg='rarest_first'; vpeers=16; peers=14; mode='empty'; gap=0
CheckTest $1 $2
alg='in_order'; vpeers=16; peers=14; mode='empty'; gap=2
CheckTest $1 $2

echo MS1 Checks Done