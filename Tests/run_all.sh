#!/bin/bash
#
#	run_all.sh

MAX_UP='--max_upload_rate 90'
BT_SCRATCH=/home/$HOST/home/hillelav/$USER
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

if [$2 eq '']
then
        echo "You did not specify a Client. Run it separately."
else
        sleep $gap
        for ((thr=1; thr < $8 ; thr++));
        do
                echo Spawn VOD $thr and sleep $gap
                ./run_client vod $thr "/usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --security 0 --delay $DELAY --prefetchT $PREF --rate $RATE --out_dir $4 --order $thr --gap $3 --group_size $VOD_CLIENTS --alg 'ORIG' ./picture.$HOST.bmp.torrent" &
                sleep $gap
        done
        echo Spawn VOD $VOD_CLIENTS 
        ./run_client vod $8 "/usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --verbose 1 --security 0 --delay $DELAY  --prefetchT $PREF  --rate $RATE --out_dir $4 --order $VOD_CLIENTS --gap $3 --group_size $VOD_CLIENTS --alg 'ORIG' ./picture.$HOST.bmp.torrent"
fi
	;;
	kill)
        ./run_scenario_vod.sh kill
        echo GOOD BYE 
	;;
	stop)
		sleep 10
		
		# Wait for all of the VOD-Peers
		echo waiting for all vod peers to finish...
		
		for (( i=0; i<(${#pidvods[@]}-1); i++ ));
		do
			wait $pidvods[$i]
		done
		
		# shut down         
        ./run_scenario_vod.sh stop
        
        echo FINISHED TEST
	;;
	fail)
		testResult = -1
		./run_scenario_vod.sh stop
		echo TEST FAILED
	*)
	echo "Usage: run_all.sh [start | stop | kill | fail]"
	exit
	;;
esac

