#!/bin/bash
#
#	run_test_checker.sh
#	04-12-2013
#	Nir Malbin

if [ "$3" == "" ]
then
	echo "USAGE: vod_peers gap test_Folder [-f]"
	exit -1
fi

if [ ! -d "$3" ]
then
	echo "Test folder $3 does not exists..."
	exit -1
fi

declare -i neededrows
neededrows=22+$1*$2-$2

echo "Checking test in ${3##*/} ..."

result=1

declare -i run
run=0

while [ -d "$3/$run" ]
do
	./run_run_check.sh $1 $2 $3/$run $4; runresult=$?

	if [ $runresult != 0 ]
	then
		result=0
	fi
			
	run=$run+1
done

if [ $result == 1 ]
then
	echo "Test ${3##*/} OK!"
	exit 0
else
	echo "Test ${3##*/} Failed!"
	exit -1
fi

