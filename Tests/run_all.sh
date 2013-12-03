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
#        thr=1
        for ((thr=1; thr < $8 ; thr++));
#        while [ $thr -lt $8]
        do
                echo Spawn VOD $thr and sleep $gap
                echo /usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --security 0 --delay $DELAY --prefetchT $PREF --rate $RATE --out_dir $4 --order $thr --gap $3 --group_size $VOD_CLIENTS --alg 'ORIG' ./picture.$HOST.bmp.torrent& 
                /usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --security 0 --delay $DELAY --prefetchT $PREF  --rate $RATE --out_dir $4 --order $thr --gap $3 --group_size $8 --alg 'ORIG' ./picture.$HOST.bmp.torrent& 
                sleep $gap
#                thr=`expr $thr + 1`
        done
        echo Spawn VOD $VOD_CLIENTS 
        echo /usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --verbose 1 --security 0 --delay $DELAY  --prefetchT $PREF  --rate $RATE --out_dir $4 --order $VOD_CLIENTS --gap $3 --group_size $VOD_CLIENTS --alg 'ORIG' ./picture.$HOST.bmp.torrent
        /usr/bin/python $2 --saveas  $BT_SCRATCH/picture.$HOST-$thr.bmp  $MAX_UP  --verbose 1 --security 0 --delay $DELAY  --prefetchT $PREF  --rate $RATE --out_dir $4 --order $thr --gap $3 --group_size $8 --alg 'ORIG' ./picture.$HOST.bmp.torrent
fi
	;;
	kill)
        ./run_scenario_vod.sh kill
        echo GOOD BYE 
	;;
	stop)
        sleep 10
        ./run_scenario_vod.sh stop
        echo FINISHED TEST
	;;
	*)
	echo "Usage: run_all.sh [start | stop]"
	exit
	;;
esac

