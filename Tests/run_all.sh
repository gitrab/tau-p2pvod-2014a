#!/bin/bash
#
#	run_all.sh
#
#	04-12-2013
#	Nir Malbin

TR_PY='/usr/bin/python'
TORRENTS=.
BT_SCRATCH=/home/$HOST/home/hillelav/$USER
MAX_UP='--max_upload_rate 90'
PREF=5
RATE=90
DELAY=20

case $1 in
	start)
        gap=`expr $3 \* 16`
        rm -rf $BT_SCRATCH/*

        mkdir -p $BT_SCRATCH
        chmod 0777 $BT_SCRATCH

 
	./run_scenario_vod.sh start $5 $6 $7

if [ "$2" == "" ]
then
        echo "You did not specify a Client. Run it separately."
else
		# set a file indicating the test is running
		echo 1 > $BT_SCRATCH/running
	
		# run all vod peers
        sleep $gap
        for ((thr=1; thr < $8 ; thr++));
        do
                echo Spawn VOD $thr and sleep $gap
                ./run_wrapper.sh vod $thr "$TR_PY $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --security 0 --delay $DELAY --prefetchT $PREF --rate $RATE --out_dir $4 --order $thr --gap $3 --group_size $8 --alg ORIG $TORRENTS/picture.$HOST.bmp.torrent" & pidvods[$thr]=$!
                sleep $gap
        done
    	echo Spawn VOD $8
        ./run_wrapper.sh vod $8 "$TR_PY $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --verbose 1 --security 0 --delay $DELAY  --prefetchT $PREF  --rate $RATE --out_dir $4 --order $8 --gap $3 --group_size $8 --alg ORIG $TORRENTS/picture.$HOST.bmp.torrent" & pidvods[$thr]=$!
    
    	# wait for all of the vod peers
		for pid in ${pidvods[*]}
		do
			wait $pid
		done
		
		# check if the test has been failed or not
		if [ ! -f $BT_SCRATCH/running ]
		then
			echo TEST FAILED
			
			exit -1
		else
			./run_scenario_vod.sh stop
			
			echo FINISHED TEST
	    
	    	exit 0
		fi
fi
	;;
	kill)
        ./run_scenario_vod.sh kill
        echo GOOD BYE 
	;;
	fail)
		if [ -f $BT_SCRATCH/running ]
		then
			./run_scenario_vod.sh stop
		fi
	;;
	*)
	echo "Usage: run_all.sh [start | kill | fail]"
	exit
	;;
esac

