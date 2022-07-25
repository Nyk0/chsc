#!/bin/bash

until host toto.lab.local
do
	sleep 5
done
