#!/bin/bash

/bin/bash /generate-config.sh

until host $DB_HOST
do
        sleep 2
done

until pg_isready -h $DB_HOST -p $DB_PORT
do
	sleep 2
done

oar-database --create --db-admin-user root --db-admin-pass azerty --db-ro-user $DB_OAR_BASE_USERNAME_RO --db-ro-pass $DB_OAR_BASE_USERPASS_RO --conf /etc/oar/oar.conf

oarproperty -a cpu -c -a host

/usr/sbin/Almighty
