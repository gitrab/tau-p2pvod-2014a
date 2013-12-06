#!/bin/bash
#
#	run1.sh
#	2009-09-16
#	Leon A.

TARS=.
TORRENTS=.
ENV_CLIENT=../BitTornado-CVS/btdownloadheadless.py
BT_SCRATCH=/home/$HOST/home/hillelav/$USER
TR_PY='/usr/bin/python'
MAX_UP='--max_upload_rate 70'

case $1 in
start)

	#start the tracker
	./run_wrapper.sh bttrack 1 "bttrack --port 6970 --dfile $BT_SCRATCH/trackerfile-$HOST" &

	if [ $2 == empty ]
	then
		cp $TARS/$HOST-save.tar.gz $BT_SCRATCH
	else
		cp $TARS/$HOST-save.steady.tar.gz $BT_SCRATCH/$HOST-save.tar.gz
	fi

	cd  $BT_SCRATCH
	tar -xzvf $TARS/$HOST-save.tar.gz
	cd -

	# spawn the seeds
	for ((thr=0; thr < $4 ; thr++));
	do
	    echo Spawn Seed $thr
	    ./run_wrapper.sh seed $thr "$TR_PY $ENV_CLIENT --saveas $BT_SCRATCH/$HOST-save/picture-100.bmp $MAX_UP --security 0 $TORRENTS/picture.$HOST.bmp.torrent" &
	done
	
	# spawn the regular peers
	for ((thr=0; thr < $3 ; thr++));
	do
	        echo Spawn BitTorrent $thr 
	        ./run_wrapper.sh peer $thr "$TR_PY $ENV_CLIENT --saveas  $BT_SCRATCH/$HOST-save/picture-bt-$thr.bmp $MAX_UP --security 0 $TORRENTS/picture.$HOST.bmp.torrent" &
	done
	
	chmod 0777 $BT_SCRATCH/*

	;;
	kill)
		USER=`echo $USER`
		CMD=`ps -fu $USER | egrep 'bttrack|btdownloadheadless.py' | grep -v grep| awk '{print $2}'`
	
		for pid in $CMD
		do
			kill -9 $pid
		done
		
		set -- $CMD
		echo ${#@} killed 
	
        rm -rf $BT_SCRATCH/*
	;;
	stop)
		USER=`echo $USER`
		CMD=`ps -fu $USER | egrep 'bttrack|btdownloadheadless.py' | grep -v grep|grep -v run| awk '{print $2}'`
		for pid in $CMD
		do
			kill -9 $pid
		done
		
		set -- $CMD
		echo ${#@} killed 
		
	    rm -rf $BT_SCRATCH/*
	    
	;;
	*)
	exit
	;;
esac
