#!/bin/bash
#
#	run_client.sh
#	04-12-2013
#	Nir Malbin

if [$3 == '']
then
	exit
fi

command = $3

# Print the command and execute it
echo $command
$command &
pid = $!

# Update the pid arrays
case $1 in
	seed)
		pidseeds[$2]=pid		
	;;
	peer)
		pidpeers[$2]=pid
	;;
	vod)
		pidvods[$2]=pid
	;;
esac

# Wait and check if command exit successfuly
wait $pid
exitcode = $?
if [$exitcode != 0]
then

	# Notify user
	echo FAILED: $1 
	
	# Fail them all!!
	if [$testResult == 0]
	then
		./run_all.sh fail
	fi
	
	exit exitcode

fi

