#!/bin/bash

OAR_SSHD_PORT=6667

until nc -z `hostname` $OAR_SSHD_PORT
do
	sleep 2
done

until host `hostname`
do
	sleep 2
done

sleep 2

oarnodesetting -h `hostname` -s Alive
