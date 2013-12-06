#!/bin/bash
#
#	client_wrapper.sh
#	04-12-2013
#	Nir Malbin

if [ "$3" == "" ]
then
	exit
fi

command=$3

# Print the command and execute it
echo $command
$command; exitcode=$?
echo EXIT: $1 $2 with exitcode $exitcode

case $1 in
	vod)
		successcode=3
	;;
	*)
		successcode=137
	;;
esac

if [ $exitcode != $successcode ]
then

	# Notify user
	echo FAILED: $1 $2
	
	# Test failed!
	./run_all.sh fail
	
	exit -1
	
fi

exit 0

