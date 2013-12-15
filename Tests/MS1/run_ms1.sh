#!/bin/bash
#
#	run_ms1.sh
#
#	14-12-2013
#	Nir Malbin

seeds=2; iter=5;

RunTest () {
	testdir="$alg.$vpeers.$mode.$gap"
	echo Running Test $testdir
	mkdir $1/$testdir
	./run_all.sh kill
	./run_multiple.sh ~/p2pvod/src/$alg/btdownloadheadless.py $gap $1/$testdir $iter $mode $peers $seeds $vpeers > $1/$testdir/log.txt
}

alg='in_order'; vpeers=4; peers=26; mode='empty'; gap=2
RunTest $1
alg='in_order'; vpeers=16; peers=14; mode='empty'; gap=0
RunTest $1
alg='rarest_first'; vpeers=4; peers=26; mode='empty'; gap=2
RunTest $1
alg='rarest_first'; vpeers=16; peers=14; mode='empty'; gap=2
RunTest $1
alg='in_order'; vpeers=16; peers=14; mode='full'; gap=0
RunTest $1
alg='in_order'; vpeers=4; peers=26; mode='empty'; gap=0
RunTest $1
alg='rarest_first'; vpeers=16; peers=14; mode='full'; gap=0
RunTest $1
alg='in_order'; vpeers=4; peers=26; mode='full'; gap=0
RunTest $1
alg='rarest_first'; vpeers=4; peers=26; mode='full'; gap=0
RunTest $1
alg='rarest_first'; vpeers=4; peers=26; mode='empty'; gap=0
RunTest $1
alg='rarest_first'; vpeers=16; peers=14; mode='empty'; gap=0
RunTest $1
alg='in_order'; vpeers=16; peers=14; mode='empty'; gap=2
RunTest $1

echo MS1 Tests Done