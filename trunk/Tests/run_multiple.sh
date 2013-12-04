#!/bin/bash
#
#	run_multiple.sh
if [$8 eq ''] 
then
        echo USAGE: run_multiple.sh your_client gap output_location iteration empty/full peers_num seeds_num vod_num
        exit
fi
num=$4

echo NUM = $4
for ((  i = 0 ;  i < $num;  i++  ))
do
	testResult = -1

	# Run the test until success		
	while [testResult != 0]
	do
		rm -rf $3/$i
		echo mkdir $3/$i
		mkdir $3/$i/
		echo ./run_all.sh start $1 $2 $3/$i/ $5 $6 $7 $8
		./run_all.sh start $1 $2 $3/$i/ $5 $6 $7 $8
    done

done


