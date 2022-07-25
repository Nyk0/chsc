#!/bin/bash

/bin/bash /generate-config.sh

until oar-database --create --db-admin-user root --db-admin-pass azerty --db-ro-user $DB_OAR_BASE_USERNAME_RO --db-ro-pass $DB_OAR_BASE_USERPASS_RO --conf /etc/oar/oar.conf
do
	sleep 5
done

/usr/sbin/Almighty
