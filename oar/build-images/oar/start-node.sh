#!/bin/bash

/bin/bash /generate-config.sh

sleep 2

/usr/sbin/sshd -f /etc/oar/sshd_config

until host `hostname`
do
	echo "Attempt to resolve ..."
	sleep 2
done

echo "Register"
oarnodesetting -h `hostname` -s Alive

while true
do
	sleep 30
done
