#!/bin/bash
#
#	run_run_checker.sh
#	04-12-2013
#	Nir Malbin

if [ "$3" == "" ]
then
	echo "USAGE: vod_peers gap run_Folder [-f]"
	exit -1
fi

declare -i neededrows
neededrows=22+$1*$2-$2

echo -ne "Testing run ${3##*/}... "
	
runresult=1

# Checks the peers count
peers=`ls -l $3 | grep -v ^l | wc -l`
peers=$[ $peers - 1 ]

if [ $peers != $1 ]
then
	runresult=0
fi

if [ "$4" == "-f" ]
then
	echo -e "\n\t$peers peers found"
	echo -e "\torder\trows"
fi

# Check each peer CSV file
for ((  i=1 ;  i <= $peers;  i++  ))
do
	if [ -f $3/statistics-order-$i-gap-$2.csv ]
	then
		rows=`wc -l < $3/statistics-order-$i-gap-$2.csv`
		
		if [ "$4" == "-f" ]
		then
			echo -e "\t$i\t$rows"
		fi
		
		if [ $rows != $neededrows ]
		then
			runresult=0
		fi
	fi
done

if [ $runresult == 0 ]
then
	echo "FAILED!"
	exit -1
else
	echo "PASS!"
	exit 0
fi
