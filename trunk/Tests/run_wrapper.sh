#!/bin/bash
#
#	run_wrapper.sh
#	04-12-2013
#	Nir Malbin

if [ "$3" == "" ]
then
	exit
fi

command=$3

# Print the command and execute it
echo $command

case $1 in
	vod)
		successcode=3
		$command; exitcode=$?
	;;
	*)
		successcode=137
		$command > /dev/null; exitcode=$?
	;;
esac

echo EXIT: $1 $2 with exitcode $exitcode

if [ $exitcode != $successcode ]
then

	# Notify user
	echo FAILED: $1 $2
	
	# Test failed!
	./run_all.sh fail
	
	exit -1
	
fi

exit 0

