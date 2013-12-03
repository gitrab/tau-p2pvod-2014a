#!/bin/bash
#
#	run1.sh
#	2009-09-16
#	Leon A.


ENV_CLIENT=../BitTornado-CVS/btdownloadheadless.py
BT_SCRATCH=/home/$HOST/home/hillelav/$USER
TR_PY='/usr/bin/python'
MAX_UP='--max_upload_rate 70'


case $1 in
start)

bttrack --port 6970 --dfile $BT_SCRATCH/trackerfile-$HOST &

if [ $2 == empty ]
then
cp ./$HOST-save.tar.gz $BT_SCRATCH


else
cp ./$HOST-save.steady.tar.gz $BT_SCRATCH/$HOST-save.tar.gz

fi

#cp ./$HOST-save.tar.gz $BT_SCRATCH
cd  $BT_SCRATCH
tar -xzvf ./$HOST-save.tar.gz
cd -

echo "Spawn $4 seeds"

for ((thr=0; thr < $4 ; thr++));
#for thr in { 1..$4 }
do
    echo Spawn Seed $thr 
    echo $TR_PY $ENV_CLIENT --saveas $BT_SCRATCH/$HOST-save/picture-100.bmp $MAX_UP --security 0 ./picture.$HOST.bmp.torrent &
    $TR_PY $ENV_CLIENT --saveas $BT_SCRATCH/$HOST-save/picture-100.bmp $MAX_UP --security 0 ./picture.$HOST.bmp.torrent &
done
for ((thr=0; thr < $3 ; thr++));
#for thr in { 1..$3 }
do
        echo Spawn BitTorrent $thr 
        echo $TR_PY $ENV_CLIENT --saveas  $BT_SCRATCH/$HOST-save/picture-bt-$thr.bmp $MAX_UP --security 0 ./picture.$HOST.bmp.torrent &
        $TR_PY $ENV_CLIENT --saveas  $BT_SCRATCH/$HOST-save/picture-bt-$thr.bmp $MAX_UP --security 0 ./picture.$HOST.bmp.torrent &
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
        rm -rf $BT_SCRATCH/*
	;;
	stop)
	USER=`echo $USER`
	CMD=`ps -fu $USER | egrep 'bttrack|btdownloadheadless.py' | grep -v grep|grep -v run| awk '{print $2}'`
	for pid in $CMD
	do
		kill -9 $pid
	done
        rm -rf $BT_SCRATCH/*
	;;
	*)
	exit
	;;
esac
