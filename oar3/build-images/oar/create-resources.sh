#!/bin/bash

nb_nodes=$1
cpus_per_node=$2

nb_cpus=$(( nb_nodes * cpus_per_node ))

i=0
while [ $i -lt $nb_cpus ]
do
	oarnodesetting -a -h $3-$(( i / cpus_per_node )) -p host=$3-$(( i / cpus_per_node )) -p cpu=$(( i + 1 ))
	((i=i+1))
done

i=1
while [ $i -le $nb_cpus ]
do
	oarnodesetting -r $i -p cpu=$i
	((i=i+1))
done
