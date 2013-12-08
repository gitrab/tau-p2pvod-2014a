#!/bin/bash
#
#	run_multiple.sh
if [ "$8" == '' ] 
then
        echo USAGE: run_multiple.sh your_client gap output_location iteration empty/full peers_num seeds_num vod_num
        exit
fi

echo "Running $4 iterations"

for ((  i = 0 ;  i < $4;  i++  ))
do
	testResult=-1

	# Run the test until success		
	while [ $testResult != 0 ]
	do
		rm -rf $3/$i
		echo mkdir $3/$i
		mkdir $3/$i/
		echo ./run_all.sh start $1 $2 $3/$i/ $5 $6 $7 $8
		./run_all.sh start $1 $2 $3/$i/ $5 $6 $7 $8; testResult=$?
		
		if [ $testResult == 1 ]
		then
			./run_test_check.sh $6 $2 $3; testResult=$?
		fi
		
    done

done


