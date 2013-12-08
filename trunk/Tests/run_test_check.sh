#!/bin/bash
#
#	client_wrapper.sh
#	04-12-2013
#	Nir Malbin

if [ "$3" == "" ]
then
	echo "USAGE: VodsPeers Gap TestFolder"
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
	echo -ne "\tTesting run $run... "
	
	runresult=1
	
	# Checks the peers count
	peers=`ls -l $3/$run | grep -v ^l | wc -l`
	peers=$[ $peers - 1 ]
	
	if [ $peers != $1 ]
	then
		#echo -e "\tERROR: Found $peers peers instead of $1!"
		runresult=0
	#else
		#echo -e "\tPASS: Found $peers peers!"
	fi
	
	# Check each peer CSV file
	for ((  i=1 ;  i <= $peers;  i++  ))
	do
		if [ -f $3/$run/statistics-order-$i-gap-$2.csv ]
		then
			rows=`wc -l < $3/$run/statistics-order-$i-gap-$2.csv`
			
			if [ $rows != $neededrows ]
			then
				#echo -e "\t\tERROR: Found $rows instead of $neededrows in peer $i!"
				runresult=0
			#else
				#echo -e "\t\tPASS: $rows in statistics-order-$i-gap-$2.csv"
			fi
		fi
	done
	
	if [ $runresult == 0 ]
	then
		echo "FAILED!"
		result=0 
	else
		echo "PASS!"
	fi
	
	run=$run+1
	
done

if [ $result == 1 ]
then
	echo "Check OK!"
	exit 0
else
	echo "Check Failed!"
	exit -1
fi