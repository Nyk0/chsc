#!/bin/bash

OAR_SSHD_PORT=6667

reach_sshd=1
while [ $reach_sshd != 0 ]
do
        nc -z `hostname` $OAR_SSHD_PORT > /dev/null 2>&1
        reach_sshd=$?
	sleep 2
	echo "try to register ..."
done

oarnodesetting -h `hostname` -s Alive
